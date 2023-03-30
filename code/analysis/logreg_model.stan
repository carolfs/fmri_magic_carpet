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

data {
    int M; // number of participants
    int N; // number of trials per participant
    int K; // number of predictors
    int<lower=0, upper=1> y[M,N]; // stay for each trial
    matrix[N,K] x[M]; // predictors for each trial
    int<lower=0, upper=1> condition[M];
}
parameters {
    // Coefficients for each participants
    vector[K] coefs[M];
    // Distribution of coefficients
    cholesky_factor_corr[K] L_Omega;
    vector<lower=0>[K] tau;
    vector[K] beta0;
    vector[K] condition_beta;
}
transformed parameters {
    matrix[K, K] Sigma;
    Sigma = diag_pre_multiply(tau, L_Omega);
    Sigma *= Sigma';
}

model {
    tau ~ cauchy(0, 1);
    beta0 ~ normal(0, 5);
    condition_beta ~ cauchy(0, 1);
    L_Omega ~ lkj_corr_cholesky(2);
    for (p in 1:M) {
        coefs[p] ~ multi_student_t(4, beta0 + condition[p] * condition_beta, Sigma);
        y[p] ~ bernoulli_logit(x[p] * coefs[p]);
    }
}
