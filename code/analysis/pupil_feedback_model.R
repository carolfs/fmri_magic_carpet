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

library("brms")
feedback_model <- read.csv("feedback_model.csv")
fbm <- feedback_model
fbm$participant <- as.factor(fbm$participant)
fbm$reward <- 2* fbm$reward - 1
fbm$common <- 2* fbm$common - 1
fbm$cond_num <- 2*(fbm$condition == 'story') - 1
m <- brm(mean_pupdiam ~ (1 + reward*common |participant) + cond_num*reward*common, data = fbm, chains = 1, iter = 8000, warmup = 4000)
summary(m)

