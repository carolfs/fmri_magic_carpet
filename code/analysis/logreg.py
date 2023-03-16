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

"""Logistic regression analysis (one trial back)"""

import os
from os.path import join
import numpy as np
import pandas as pd
from cmdstanpy import CmdStanModel
from config import CONDITIONS, ANALYSIS_RESULTS_DIR

def topm1(v):
    """Convert 0/1 value to -1/+1."""
    return 2*v - 1

def get_regression_row(reward, common):
    """Returns a row of predictors."""
    x_row = [
        1,
        reward,
        common,
        reward*common,
    ]
    return np.array(x_row)

def get_part_data():
    """Get x, y data for all participants from a given condition."""
    x, y, condition = [], [], []
    for _, part_data in pd.read_csv("beh_noslow.csv").groupby("participant"):
        part_condition = part_data.iloc[0].condition
        assert part_condition in CONDITIONS
        condition.append(int(part_condition == CONDITIONS[-1]))
        part_x, part_y = [], []
        for prev_row, next_row in zip(part_data[:-1].itertuples(), part_data[1:].itertuples()):
            reward = topm1(prev_row.reward)
            common = topm1(prev_row.common)
            x_row = get_regression_row(reward, common)
            part_x.append(x_row)
            part_y.append(int(prev_row.choice1 == next_row.choice1))
        x.append(part_x)
        y.append(part_y)
    # Create dummy rows to get the same number of rows for every participant
    num_trials = max([len(yy) for yy in y])
    xdummy = [0]*len(x[0][0])
    for xx, yy in zip(x, y):
        assert len(xx) == len(yy)
        while len(yy) < num_trials:
            yy.append(0)
            xx.append(xdummy)
    return x, y, condition

def get_logreg_model_dat():
    "Creates a dictionary with the data for the logistic regression."
    x, y, condition = get_part_data()

    model_dat = {
        'M': len(y),
        'N': len(y[0]),
        'K': len(x[0][0]),
        'y': y,
        'x': x,
        'condition': condition,
    }
    return model_dat

SAMPLE_FN = join(ANALYSIS_RESULTS_DIR, 'logreg_samples')
SAMPLESFIT_FN = join(ANALYSIS_RESULTS_DIR, 'logreg_analysis_fit.csv')
ITER = 32000
WARMUP = 16000
CHAINS = 4

def get_exp_fit(its, chains, warmup):
    'Extracts the predictors and fits the regression model to the data.'
    stan_model = CmdStanModel(stan_file=join(ANALYSIS_DIR, 'logreg_model.stan'))
    model_dat = get_logreg_model_dat()
    fit = stan_model.sample(
        data=model_dat,
        iter_sampling=its,
        chains=chains,
        iter_warmup=warmup,
        output_dir=SAMPLE_FN,
        show_progress=True,
    )
    return fit

def main():
    "Analyzes the results by logistic regression."
    if not os.path.exists(ANALYSIS_RESULTS_DIR):
        os.mkdir(ANALYSIS_RESULTS_DIR)
    fit = get_exp_fit(ITER, CHAINS, WARMUP)
    fit.summary().to_csv(SAMPLESFIT_FN)

if __name__ == "__main__":
    main()
