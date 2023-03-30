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

"""Categorical model for model comparison"""

NAME = 'categorical'
CONTRASTS = [
    ['Common', 'T', ['second_choicexcommon^1'], [1]],
    ['Rewarded', 'T', ['feedbackxreward^1'], [1]],
]

def get_subject_info(participant, fmri_run, all_parts_df, get_regressors, preprocessed_dir):
    from nipype.interfaces.base import Bunch

    part_df = all_parts_df[
        (all_parts_df.participant == participant) & (all_parts_df.run == fmri_run)]
    part_df.sort_values(by='trial')

    a1value, a1value_deriv = list(part_df.chosen_action1_value), list(part_df.chosen_action1_value_deriv)
    common = list(part_df.common)
    reward = list(part_df.reward)

    regressors, regressor_names = get_regressors(participant, fmri_run, preprocessed_dir)

    info = Bunch(
        conditions=['first_choice', 'second_choice', 'feedback'],
        onsets=[
            part_df.onset_first_choice,
            part_df.onset_second_choice,
            part_df.onset_feedback,
        ],
        durations=[
            [0]*len(part_df),
            [0]*len(part_df),
            [0]*len(part_df),
        ],
        pmod=[
            Bunch(
                name=['a1value', 'a1value_deriv'],
                poly=[1, 1], param=[a1value, a1value_deriv]),
            Bunch(
                name=['common'],
                poly=[1], param=[common]),
            Bunch(name=['reward'], poly=[1], param=[reward]),
        ],
        regressors=regressors,
        regressor_names=regressor_names,
    )
    return info

if __name__ == "__main__":
    print("Run first_level_repl.py instead")
