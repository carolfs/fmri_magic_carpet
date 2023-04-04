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

# Ratings model

data {
    int K; // Max rating (should be from 1 to 5)
    int N; // number of points
    int<lower=1, upper=K> ratings[N];
    int<lower=0, upper=1> condition[N];
}
transformed data {
}
parameters {
    real eta;
    ordered[K - 1] c;
}
model {
    eta ~ normal(0, 1.5);
    c ~ normal(0, 5);
    for (i in 1:N)
        ratings[i] ~ ordered_logistic((2*condition[i] - 1)*eta, c);
}