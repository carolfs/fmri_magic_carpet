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

functions {
    real hybrid(int num_trials, int[] action1, int[] s2, int[] action2,
        int[] reward, real alpha1, real alpha2, real lmbd, real beta1, 
        real beta2, real w, real p) {

        real log_lik;
        real q[2];
        real v[2, 2];

        // Initializing values
        for (i in 1:2)
            q[i] = 0;
        for (i in 1:2)
            for (j in 1:2)
                v[i, j] = 0;

        log_lik = 0;

        for (t in 1:num_trials) {
            real x1;
            real x2;
            x1 = // Model-based value
                w*0.4*(max(v[2]) - max(v[1])) +
                // Model-free value
                (1 - w)*(q[2] - q[1]);
            // Perseveration
            if (t > 1) {
                if (action1[t - 1] == 2)
                    x1 += p;
                else
                    x1 -= p;
            }
            // Exploration
            x1 *= beta1;
            // First stage choice
            if (action1[t] == 2)
                log_lik += log_inv_logit(x1);
            else
                log_lik += log1m_inv_logit(x1);

            // Second stage choice
            x2 = beta2*(v[s2[t], 2] - v[s2[t], 1]);
            if (action2[t] == 2)
                log_lik += log_inv_logit(x2);
            else
                log_lik += log1m_inv_logit(x2);

            // Learning
            q[action1[t]] += alpha1*(v[s2[t], action2[t]] - q[action1[t]]) +
                alpha1*lmbd*(reward[t] - v[s2[t], action2[t]]);
            v[s2[t], action2[t]] += alpha2*(reward[t] - v[s2[t], action2[t]]);
        }
        return log_lik;
    }
}
data {
    int<lower=0> N; // Number of participants
    int<lower=0> maxtrials;
    // Number of trials (can be < maxtrials if participant missed some)
    int<lower=1, upper=maxtrials> num_trials[N];
    int<lower=0, upper=1> condition[N];
    int<lower=1, upper=2> action1[N,maxtrials]; // First stage actions
    int<lower=1, upper=2> action2[N,maxtrials]; // Second stage actions
    int<lower=1, upper=2> s2[N,maxtrials]; // Second stage states
    int<lower=0, upper=1> reward[N,maxtrials]; // Rewards
}
parameters {
    // Transformed model parameters
    matrix[7, N] z;
    vector<lower=0, upper=pi()/2>[7] sigma_unif;
    vector<lower=-pi()/2,upper=pi()/2>[7] mu_unif;
    vector<lower=-pi()/2,upper=pi()/2>[7] condition_beta_unif;
}
model {
    vector[7] mu = 5.*tan(mu_unif); // Cauchy(0, 5) distribution
    vector[7] condition_beta = 5.*tan(condition_beta_unif);
    vector[7] sigma = 5.*tan(sigma_unif);
    to_vector(z) ~ student_t(4., 0., 1.);
    for (i in 1:N) {
        vector[7] subjparams = z[,i].*sigma + mu + condition[i]*condition_beta;
        real alpha1 = inv_logit(subjparams[1]);
        real alpha2 = inv_logit(subjparams[2]);
        real lmbd = inv_logit(subjparams[3]);
        real beta1 = exp(subjparams[4]);
        real beta2 = exp(subjparams[5]);
        real w = inv_logit(subjparams[6]);
        real p = subjparams[7];
        target += hybrid(num_trials[i], action1[i], s2[i], action2[i], reward[i], alpha1,
            alpha2, lmbd, beta1, beta2, w, p);
    }
}
