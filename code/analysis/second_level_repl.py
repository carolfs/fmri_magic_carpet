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

"""Runs the second-level GLM to replicate the original paper's results"""

from subprocess import run
import os
from os.path import join
import tempfile
import argparse
from multiprocessing import Process
import pandas as pd
from first_level_repl import (
    get_part_data_sink_dir,
    MODELS,
)
from calculate_fmri_predictors import PARAMS_FILE, CONDITIONS, PREDICTOR_ANALYSES


def finished_analysis(parts, data_sink_dir, model, contrast):
    for part in parts.itertuples():
        image_path = join(
            get_part_data_sink_dir(part.participant, model, data_sink_dir),
            f"con_{contrast + 1:04d}.nii",
        )
        if not os.path.exists(image_path):
            print(f"Unfinished analysis: {image_path} not found")
            return False
    return True


def run_contrast_analysis(
    parts, data_sink_dir, results_dir, mask, model, contrast, contrast_info
):
    with tempfile.TemporaryDirectory() as tempdir:
        contrast_name = (
            contrast_info[0].lower().replace(" ", "_").replace("(", "").replace(")", "")
        )
        contrast_results_dir = os.path.join(
            results_dir, f"contrast_{model.NAME}" f"_{contrast_name}"
        )
        files = []
        for part in parts.itertuples():
            image_path = join(
                get_part_data_sink_dir(part.participant, model, data_sink_dir),
                f"con_{contrast + 1:04d}.nii",
            )
            assert os.path.exists(image_path)
            files.append(image_path)
        if os.path.exists(contrast_results_dir):
            return
        else:
            os.mkdir(contrast_results_dir)
        # Glue all images together for FSL :/
        merged = join(tempdir, "merged.nii.gz")
        run(["fslmerge", "-t", merged] + files)
        # Images can't have NaNs
        run(["fslmaths", merged, "-nan", merged])
        cmd = ["randomise", "-i", merged, "-o", contrast_results_dir + "/"]
        design_con = join(tempdir, "design.con")
        design_mat = join(tempdir, "design.mat")
        if (
            contrast_info[2][0].find("rpediff") == -1
            and contrast_info[2][0].find("mbrpe") == -1
        ):
            # Not model-based, run a simple t-test
            with open(design_con + ".txt", "w") as conf:
                conf.write("1\t0\n")
                conf.write("-1\t0\n")
            with open(design_mat + ".txt", "w") as matf:
                for part in parts.itertuples():
                    matf.write(f"1\t{part.runs}\n")
        else:
            # Model-based values, add weight as a covariate
            with open(design_con + ".txt", "w") as conf:
                conf.write("1\t0\t0\n")
                conf.write("-1\t0\t0\n")
                conf.write("0\t1\t0\n")
                conf.write("0\t-1\t0\n")
            with open(design_mat + ".txt", "w") as matf:
                for part in parts.itertuples():
                    matf.write(f"1\t{part.w}\t{part.runs}\n")
        run(["Text2Vest", design_con + ".txt", design_con])
        run(["Text2Vest", design_mat + ".txt", design_mat])
        cmd = [
            "-d", design_mat, "-t", design_con,
            "--uncorrp", "-x", "-n", "5000", "-T", "-v", "6"]
        if mask is not None:
            cmd += ["-m", mask]
        run(cmd)


NUM_SIMULT_PROCS = 4

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_sink_dir")
    parser.add_argument("results_dir")
    parser.add_argument("--mask", help="run the analysis only on the mask")
    args = parser.parse_args()
    if args.mask is not None and not os.path.exists(args.mask):
        print(f"The mask {args.mask} does not exist!")
        return
    if not os.path.exists(args.data_sink_dir):
        print(f"Directory {args.data_sink_dir} does not exist!")
        return
    if not os.path.exists(args.results_dir):
        os.mkdir(args.results_dir)
    fmri_participants = pd.read_csv("participants.csv")
    processes = []
    for group in CONDITIONS:
        if not os.path.exists(os.path.join(args.results_dir, group)):
            os.mkdir(os.path.join(args.results_dir, group))
        for predictor_analysis in PREDICTOR_ANALYSES:
            results_dir = os.path.join(args.results_dir, group, predictor_analysis)
            if not os.path.exists(results_dir):
                os.mkdir(results_dir)
            predictors = pd.read_csv(PARAMS_FILE[predictor_analysis].format(group))
            parts = pd.merge(
                fmri_participants, predictors, on=["participant", "condition"]
            )
            if group in CONDITIONS:
                parts = parts[parts.condition == group]
            # Mean center MB weights
            parts["w"] = parts.w - parts.w.mean()
            parts["runs"] = parts.runs - parts.runs.mean()
            data_sink_dir = os.path.join(args.data_sink_dir, group, predictor_analysis)
            for model in MODELS:
                for contrast, contrast_info in enumerate(model.CONTRASTS):
                    if not finished_analysis(parts, data_sink_dir, model, contrast):
                        continue
                    p = Process(
                        target=run_contrast_analysis,
                        args=(
                            parts,
                            data_sink_dir,
                            results_dir,
                            args.mask,
                            model,
                            contrast,
                            contrast_info,
                        ),
                    )
                    processes.append(p)
    print("Running", len(processes), "analyses...")
    for batch in range(len(processes) // NUM_SIMULT_PROCS + 1):
        batch_processes = processes[
            batch * NUM_SIMULT_PROCS : (batch + 1) * NUM_SIMULT_PROCS
        ]
        for p in batch_processes:
            p.start()
        for p in batch_processes:
            p.join()


if __name__ == "__main__":
    main()
