# Copyright (C) 2016, 2017, 2018, 2023 Carolina Feher da Silva

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Runs the first level of the condition comparison analysis"""

CONTRASTS = [
    ['First choice', 'T', ['first_choice'], [1]],
    ['Second choice', 'T', ['second_choice'], [1]],
    ['Feedback', 'T', ['feedback'], [1]],
    ['RT1', 'T', ['first_choicexrt1^1'], [1]],
    ['RT2', 'T', ['second_choicexrt2^1'], [1]],
]
MODEL_NAME = 'condition_comparison'

def get_subject_info(participant, fmri_run, all_parts_df, get_regressors, preprocessed_dir):
    from nipype.interfaces.base import Bunch

    part_df = all_parts_df[
        (all_parts_df.participant == participant) & (all_parts_df.run == fmri_run)]
    part_df.sort_values(by='trial')

    regressors, regressor_names = get_regressors(participant, fmri_run, preprocessed_dir)

    info = Bunch(
        conditions=['first_choice', 'second_choice', 'feedback'],
        onsets=[
            list(part_df.onset_first_choice),
            list(part_df.onset_second_choice),
            list(part_df.onset_feedback),
        ],
        durations=[
            list(part_df.rt1),
            list(part_df.rt2),
            [1.5]*len(part_df),
        ],
        pmod=[
            Bunch(
                name=['rt1'],
                poly=[1], param=[list(part_df.rt1)]),
            Bunch(
                name=['rt2'],
                poly=[1], param=[list(part_df.rt2)]),
            Bunch(name=[], poly=[], param=[]),
        ],
        regressors=regressors,
        regressor_names=regressor_names,
    )
    return info

import os
import argparse
import pandas as pd
from nipype.interfaces.io import DataSink
from nipype import (
    Workflow,
    Node,
    MapNode,
    Function,
    SelectFiles,
)

from nipype.interfaces.spm import Level1Design, EstimateModel, EstimateContrast
from nipype.algorithms.modelgen import SpecifySPMModel
from calculate_fmri_predictors import get_onsets_durations_filename, CONDITIONS

# Number of runs
NUM_RUNS = 3
# Number of volumes
NUM_VOLS = 337

# Grey matter mask
if not os.path.exists("mask_gm_conj_3mm.nii"):
    assert os.path.exists("mask_gm_conj_3mm.nii.gz")
    with gzip.open("mask_gm_conj_3mm.nii.gz", "rb") as inpf, open("mask_gm_conj_3mm.nii", "wb") as outf:
        outf.write(inpf.read())
GM_MASK = os.path.abspath("mask_gm_conj_3mm.nii")

def get_model_data_sink_dir(data_sink_dir):
    return os.path.join(data_sink_dir, f"first_level_{MODEL_NAME}")

def get_part_data_sink_dir(part, data_sink_dir):
    return os.path.join(
        get_model_data_sink_dir(data_sink_dir), f"participant_{part}"
    )

def finished(part, data_sink_dir):
    return os.path.exists(get_part_data_sink_dir(part, data_sink_dir))

def get_regressors(participant, fmri_run, preprocessed_dir):
    confounds_flnm = os.path.join(
        preprocessed_dir,
        f"confounds-prereg-sub-{participant:05d}-run{fmri_run}.csv",
    )
    if not os.path.exists(confounds_flnm):
        raise ValueError(f"Could not find the confounds file {confounds_flnm}")
    confounds = pd.read_csv(confounds_flnm)
    regressors = [list(confounds[col]) for col in confounds]
    regressor_names = [col for col in confounds]
    return regressors, regressor_names

def main():
    """Runs the first-level models"""
    # Get directories
    parser = argparse.ArgumentParser()
    parser.add_argument("preprocessed_dir")
    parser.add_argument("data_sink_dir")
    parser.add_argument("base_dir")
    args = parser.parse_args()
    if not os.path.exists(args.data_sink_dir):
        os.mkdir(args.data_sink_dir)

    # Load the onsets/durations/predictors
    all_parts_df = pd.read_csv("onsets_durations_noslow.csv")
    # Load behavioral results
    beh_df = pd.read_csv("beh_noslow.csv")
    # Merge all participant results
    assert len(all_parts_df) == len(beh_df)
    all_parts_df = pd.merge(
        all_parts_df, beh_df, on=("participant", "condition", "trial")
    )
    data_sink_dir = args.data_sink_dir
    if not os.path.exists(args.data_sink_dir):
        os.mkdir(args.data_sink_dir)

    workflow_name = MODEL_NAME
    participants = list(all_parts_df.participant.unique())
    participants.sort()

    # Creates fMRI workflow
    workflow = Workflow(name=workflow_name, base_dir=args.base_dir)

    fmri_runs = range(1, NUM_RUNS + 1)

    model_parts = [
        part
        for part in reversed(participants)
        if not finished(part, data_sink_dir)
    ]
    if not model_parts:
        return
    if not os.path.exists(get_model_data_sink_dir(data_sink_dir)):
        os.mkdir(get_model_data_sink_dir(data_sink_dir))
    func_filename = os.path.join(
        args.preprocessed_dir,
        "sub-{participant:05d}_task-fMRI_run-{fmri_run}_space-MNI152NLin2009cAsym"
        "_desc-preproc_bold.nii",
    )
    for part in model_parts:
        part_runs = []
        for fmri_run in fmri_runs:
            if os.path.exists(
                func_filename.format(participant=part, fmri_run=fmri_run)
            ):
                part_runs.append(fmri_run)
        assert part_runs
        # Select the files for the each participant
        templates = {
            "func_filename": func_filename,
        }
        select_files = MapNode(
            SelectFiles(templates, sort_filelist=True),
            iterfield=["fmri_run"],
            name=f"selectfiles_{MODEL_NAME}_{part}",
        )
        select_files.inputs.participant = part
        select_files.inputs.fmri_run = part_runs

        model_node = Node(SpecifySPMModel(), name=f"modelspec_{MODEL_NAME}_{part}")
        model_node.inputs.input_units = "secs"
        model_node.inputs.time_repetition = 2.5
        model_node.inputs.high_pass_filter_cutoff = (
            128.0  # Estimated 90. by FSL. In SPM 128.
        )
        model_node.inputs.concatenate_runs = False

        get_info_node = MapNode(
            Function(
                input_names=[
                    "participant",
                    "fmri_run",
                    "all_parts_df",
                    "get_regressors",
                    "preprocessed_dir",
                ],
                output_names=["subject_info"],
                function=get_subject_info,
            ),
            iterfield=["fmri_run"],
            name=f"getsubjinfo_{MODEL_NAME}_{part}",
        )
        get_info_node.inputs.all_parts_df = all_parts_df
        get_info_node.inputs.get_regressors = get_regressors
        get_info_node.inputs.fmri_run = part_runs
        get_info_node.inputs.preprocessed_dir = args.preprocessed_dir
        get_info_node.inputs.participant = part

        workflow.connect(
            select_files, "func_filename", model_node, "functional_runs"
        )
        workflow.connect(get_info_node, "subject_info", model_node, "subject_info")

        level1design = Node(
            Level1Design(
                bases={"hrf": {"derivs": [0, 0]}},
                timing_units="secs",
                interscan_interval=2.5,
                model_serial_correlations="AR(1)",
                microtime_resolution=42,
                microtime_onset=21,
                volterra_expansion_order=1,
                global_intensity_normalization="none",
                mask_image=GM_MASK,
            ),
            name=f"level1design_{MODEL_NAME}_{part}",
        )

        workflow.connect(model_node, "session_info", level1design, "session_info")

        estimate_model = Node(
            EstimateModel(estimation_method={"Classical": 1}),
            name=f"estimate_model_{MODEL_NAME}_{part}",
        )

        workflow.connect(
            level1design, "spm_mat_file", estimate_model, "spm_mat_file"
        )

        estimate_contrast = Node(
            EstimateContrast(contrasts=CONTRASTS),
            name=f"estimate_contrast_{MODEL_NAME}_{part}",
        )

        workflow.connect(
            estimate_model, "spm_mat_file", estimate_contrast, "spm_mat_file"
        )
        workflow.connect(
            estimate_model, "beta_images", estimate_contrast, "beta_images"
        )
        workflow.connect(
            estimate_model, "residual_image", estimate_contrast, "residual_image"
        )

        # Output directory
        data_sink = Node(
            DataSink(remove_dest_dir=True), name=f"data_sink_{MODEL_NAME}_{part}"
        )
        part_data_sink_dir = get_part_data_sink_dir(part, data_sink_dir)
        if not os.path.exists(part_data_sink_dir):
            os.mkdir(part_data_sink_dir)
        data_sink.inputs.base_directory = part_data_sink_dir
        workflow.connect(
            [
                (
                    estimate_contrast,
                    data_sink,
                    [
                        ("spmT_images", "@T"),
                        ("con_images", "@con"),
                    ],
                ),
            ]
        )

    args_dict = {'n_procs' : 2, 'memory_gb' : 8}
    workflow.run(plugin='MultiProc', plugin_args=args_dict)


if __name__ == "__main__":
    main()
