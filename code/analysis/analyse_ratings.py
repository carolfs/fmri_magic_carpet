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

"""Analyse if the ratings (effort, understanding, and complexity) differ by condition"""

from os.path import join
import pandas as pd
from cmdstanpy import CmdStanModel
import numpy as np

parts_rts = pd.read_csv(join("..", "..", "data", "ratings.csv"))
model = CmdStanModel(stan_file="ratings_model.stan")
for rating in ("effort", "understanding", "complexity"):
    print(rating.capitalize(), "analysis...")
    model_dat = {
        "K": 5,
        "N": len(parts_rts),
        "ratings": list(parts_rts[rating] + 1),
        "condition": list((parts_rts.condition == "story").astype("int")),
    }
    fit = model.sample(
        chains=4,
        data=model_dat,
        iter_warmup=2000,
        iter_sampling=10000,
        show_progress=True,
    )
    print(fit.summary(percentiles=(2, 5, 50, 95, 97)))
    eta = fit.stan_variable("eta")
    print(f"Effect of story instructions on {rating}:")
    print(
        "95% CI:", round(np.quantile(eta, 0.025), 3), round(np.quantile(eta, 0.975), 3)
    )
    print(
        "Posterior probabilities (< 0 and > 0):",
        round(np.mean(eta < 0), 3),
        round(np.mean(eta > 0), 3),
    )
    print(
        "Bayes factors (< 0 and > 0):",
        round(np.mean(eta < 0) / np.mean(eta >= 0), 1),
        round(np.mean(eta > 0) / np.mean(eta <= 0), 1),
    )
    print()
