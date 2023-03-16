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

"""Calculates the predictors for the replication of Daw et al. (2011)"""

import os
import pandas as pd
import numpy as np
from scipy.special import expit
from config import CONDITIONS
from hybrid_mle import HYBRID_MIXED_PARAMS, HYBRID_SINGLE_PARAMS, HYBRID_ORIGINAL_PARAMS, PARAM_NAMES

def calculate_a1value_derivative(w, beta1, qmbdiff, qmfdiff, p):
    return (
        beta1
        * (qmbdiff - qmfdiff)
        / (4 * np.cosh(beta1 * (p + qmbdiff * w - qmfdiff * (w - 1)) / 2) ** 2)
    )

def calculate_prediction_errors(part_results, params):
    q1 = np.zeros(2)
    q2 = np.zeros((2, 2))
    prev_choice1 = None
    for trial in part_results.itertuples():
        a1value = params.w * 0.4 * (
            np.max(q2[trial.choice1 - 1, :]) - np.max(q2[2 - trial.choice1, :])
        ) + (1 - params.w) * (q1[trial.choice1 - 1] - q1[2 - trial.choice1])
        if prev_choice1 == trial.choice1:
            p = params.p
        elif prev_choice1 is not None:
            assert prev_choice1 == 3 - trial.choice1
            p = -params.p
        else:
            p = 0
        a1value += p
        a1value = expit(params.beta1 * a1value)
        qmbdiff = 0.4 * (
            np.max(q2[trial.choice1 - 1, :]) - np.max(q2[2 - trial.choice1, :])
        )
        a1value_deriv = calculate_a1value_derivative(
            params.w,
            params.beta1,
            qmbdiff,
            q1[trial.choice1 - 1] - q1[2 - trial.choice1],
            p,
        )
        a2value = q2[trial.final_state - 1, trial.choice2 - 1]
        # Reward prediction errors
        mfrpe = a2value - q1[trial.choice1 - 1]
        mbrpe = a2value - (
            0.7 * max(q2[trial.choice1 - 1]) + 0.3 * max(q2[2 - trial.choice1])
        )
        rpe2 = trial.reward - a2value
        # Reinforcement learning rules
        q1[trial.choice1 - 1] += params.alpha1 * (mfrpe + params.lmbd * rpe2)
        q2[trial.final_state - 1, trial.choice2 - 1] += params.alpha2 * rpe2
        prev_choice1 = trial.choice1
        yield (mfrpe, mbrpe, mbrpe - mfrpe, rpe2, a1value, a1value_deriv, a2value)

PARAMS_FILE = {
    "mean": HYBRID_SINGLE_PARAMS,
    "mixed": HYBRID_MIXED_PARAMS,
    "original": HYBRID_ORIGINAL_PARAMS,
}
PREDICTOR_ANALYSES = PARAMS_FILE.keys()

def get_onsets_durations_filename(predictor_analysis, condition):
    return os.path.join(
        f"onsets_durations_predictors_{predictor_analysis}_{condition}.csv",
    )

def main():
    beh = pd.read_csv("beh_noslow.csv").sort_values(
        by=["participant", "trial"]
    )
    fmri_participants = pd.read_csv("participants.csv")
    onsets_df = pd.read_csv("onsets_durations_noslow.csv").sort_values(
        by=["participant", "trial"]
    )
    for analysis in PREDICTOR_ANALYSES:
        hybrid_fit_data = pd.read_csv(PARAMS_FILE[analysis])
        for condition in CONDITIONS:
            if analysis == "mean":
                # Calculate mean parameters
                mean_params = hybrid_fit_data[hybrid_fit_data.condition == condition].mean(numeric_only=True)
                for param in PARAM_NAMES[:-1]:
                    hybrid_fit_data.loc[hybrid_fit_data.condition == condition, param] = mean_params[param]
            group_onsets = onsets_df[onsets_df.condition == condition][:]
            newcols = {
                "mfrpe": [],
                "mbrpe": [],
                "rpediff": [],
                "rpe2": [],
                "chosen_action1_value": [],
                "chosen_action1_value_deriv": [],
                "chosen_action2_value": [],
            }
            start_index = 0
            for part_num, part_results in beh[beh.condition == condition].groupby("participant"):
                params = hybrid_fit_data[hybrid_fit_data.participant == part_num].iloc[0]
                # Check that rows belong to the assumed participant
                part_onsets = group_onsets[start_index : start_index + len(part_results)]
                assert part_onsets.participant.unique() == part_num
                assert list(part_results.trial) == list(part_onsets.trial)
                start_index += len(part_results)
                for (
                    mfrpe,
                    mbrpe,
                    rpediff,
                    rpe2,
                    a1value,
                    a1value_derv,
                    a2value,
                ) in calculate_prediction_errors(part_results, params):
                    newcols["mfrpe"].append(mfrpe)
                    newcols["mbrpe"].append(mbrpe)
                    newcols["rpediff"].append(rpediff)
                    newcols["rpe2"].append(rpe2)
                    newcols["chosen_action1_value"].append(a1value)
                    newcols["chosen_action1_value_deriv"].append(a1value_derv)
                    newcols["chosen_action2_value"].append(a2value)
            output_new_df = (
                group_onsets.assign(mfrpe=newcols["mfrpe"])
                .assign(mbrpe=newcols["mbrpe"])
                .assign(rpediff=newcols["rpediff"])
                .assign(rpe2=newcols["rpe2"])
                .assign(chosen_action1_value=newcols["chosen_action1_value"])
                .assign(
                    chosen_action1_value_deriv=newcols["chosen_action1_value_deriv"]
                )
                .assign(chosen_action2_value=newcols["chosen_action2_value"])
            )
            output_new_df.to_csv(
                get_onsets_durations_filename(analysis, condition), index=False
            )


if __name__ == "__main__":
    main()
