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
