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

"""Fit the hybrid reinforcement learning model using maximum-likelihood estimation"""

import sys
from os.path import join, exists
from os import mkdir
import numpy as np
import pandas as pd
from cmdstanpy import CmdStanModel
from config import (
    ANALYSIS_RESULTS_DIR,
    CONDITIONS,
)

PARAM_NAMES = ('alpha1', 'alpha2', 'lmbd', 'beta1', 'beta2', 'p', 'w')
NOPTIM = 1000
HYBRID_MIXED_PARAMS = join(ANALYSIS_RESULTS_DIR, "hybrid_mixed.csv")
HYBRID_SINGLE_PARAMS = join(ANALYSIS_RESULTS_DIR, "hybrid_single.csv")
HYBRID_ORIGINAL_PARAMS = join(ANALYSIS_RESULTS_DIR, "hybrid_original.csv")

def optimize_model(stan_model, model_dat):
    log_lik = -np.inf
    for _ in range(NOPTIM):
        while True:
            try:
                op = stan_model.optimize(data=model_dat)
            except RuntimeError as rterror:
                sys.stderr.write(f"Error: {str(rterror)}\n")
            else:
                if op.converged:
                    break
        if op.optimized_params_dict["lp__"] > log_lik:
            log_lik = op.optimized_params_dict["lp__"]
            params = op.optimized_params_dict
    return params

def main():
    if not exists(ANALYSIS_RESULTS_DIR):
        mkdir(ANALYSIS_RESULTS_DIR)
    game_results = pd.read_csv("beh_noslow.csv")
    NTRIALS = game_results.trial.max() + 1
    if not exists(HYBRID_MIXED_PARAMS):
        # Fit the mixed-effects model (Daw et al., 2011)
        stan_model = CmdStanModel(stan_file=f"hybrid_mixed.stan")
        with open(HYBRID_MIXED_PARAMS, "w") as outf:
            outf.write(f'participant,condition,{",".join(PARAM_NAMES)}\n')
        for condition in CONDITIONS:
            model_dat = {
                "N": 0,
                "num_trials": [],
                "action1": [],
                "action2": [],
                "s2": [],
                "reward": [],
            }
            model_dat["maxtrials"] = NTRIALS
            condition_results = game_results[game_results.condition == condition]
            for _, part_data in condition_results.groupby("participant"):
                model_dat["N"] += 1
                action1 = list(part_data.choice1)
                action2 = list(part_data.choice2)
                s2 = list(part_data.final_state)
                reward = list(part_data.reward)
                for lst in (action1, action2, s2, reward):
                    lst += [1] * (NTRIALS - len(part_data))
                    assert len(lst) == NTRIALS
                model_dat["num_trials"].append(len(part_data))
                model_dat["action1"].append(action1)
                model_dat["action2"].append(action2)
                model_dat["s2"].append(s2)
                model_dat["reward"].append(reward)
            params = optimize_model(stan_model, model_dat)
            with open(HYBRID_MIXED_PARAMS, "a") as outf:
                for part_num, part in enumerate(condition_results.participant.unique()):
                    line = "{},{},{},{}\n".format(
                        part,
                        condition,
                        ",".join([str(params[k]) for k in PARAM_NAMES[:-1]]),
                        params[f"w[{part_num + 1}]"],
                    )
                    outf.write(line)
    if not exists(HYBRID_SINGLE_PARAMS):
        # Perform individual fits too to get the mean parameters
        stan_model = CmdStanModel(stan_file=f"hybrid_single.stan")
        results = []
        for part, part_data in game_results.groupby("participant"):
            model_dat = {
                "num_trials": len(part_data),
                "action1": list(part_data.choice1),
                "action2": list(part_data.choice2),
                "s2": list(part_data.final_state),
                "reward": list(part_data.reward),
            }
            params = optimize_model(stan_model, model_dat)
            condition = part_data.iloc[0].condition
            results.append((part, condition, params))
        with open(HYBRID_SINGLE_PARAMS, "w") as outf:
            outf.write(f'participant,condition,{",".join(PARAM_NAMES)}\n')
            for part, condition, params in results:
                line = "{},{},{}\n".format(
                    part,
                    condition,
                    ",".join([str(params[k]) for k in PARAM_NAMES]),
                )
                outf.write(line)
    if not exists(HYBRID_ORIGINAL_PARAMS):
        # Fit the model to get w but using the other parameters from Daw et al., 2011
        alpha1, alpha2, lmbd, beta1, beta2, p = 0.70, 0.40, 0.63, 4.23, 2.95, 0.17
        stan_model = CmdStanModel(stan_file=f"hybrid_wonly.stan")
        model_dat = {
            "N": 0,
            "num_trials": [],
            "action1": [],
            "action2": [],
            "s2": [],
            "reward": [],
            'alpha1': alpha1,
            'alpha2': alpha2,
            'lmbd': lmbd,
            'beta1': beta1,
            'beta2': beta2,
            'p': p,
        }
        model_dat["maxtrials"] = NTRIALS
        for _, part_data in game_results.groupby("participant"):
            model_dat["N"] += 1
            action1 = list(part_data.choice1)
            action2 = list(part_data.choice2)
            s2 = list(part_data.final_state)
            reward = list(part_data.reward)
            for lst in (action1, action2, s2, reward):
                lst += [1] * (NTRIALS - len(part_data))
                assert len(lst) == NTRIALS
            model_dat["num_trials"].append(len(part_data))
            model_dat["action1"].append(action1)
            model_dat["action2"].append(action2)
            model_dat["s2"].append(s2)
            model_dat["reward"].append(reward)
        params = optimize_model(stan_model, model_dat)
        with open(HYBRID_ORIGINAL_PARAMS, "w") as outf:
            outf.write(f'participant,condition,{",".join(PARAM_NAMES)}\n')
            for part_num, (part, part_data) in enumerate(game_results.groupby("participant")):
                line = "{},{},{},{}\n".format(
                    part,
                    part_data.iloc[0].condition,
                    ",".join([str(k) for k in (alpha1, alpha2, lmbd, beta1, beta2, p)]),
                    params[f"w[{part_num + 1}]"],
                )
                outf.write(line)

if __name__ == "__main__":
    main()
