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

"""Combined-RPE model from Daw et al. (2011)"""

NAME = 'combined'
CONTRASTS = [
    ['Model-free RPE', 'T', ['second_choice_and_feedbackxmfrpe^1'], [1]],
    ['RPE difference', 'T', ['second_choice_and_feedbackxrpediff^1'], [1]],
]

def get_subject_info(participant, fmri_run, all_parts_df, get_regressors, preprocessed_dir):
    import pandas as pd
    from nipype.interfaces.base import Bunch

    part_df = all_parts_df[
        (all_parts_df.participant == participant) & (all_parts_df.run == fmri_run)]
    part_df.sort_values(by='trial')

    mfrpe, rpediff, rpe2 = list(part_df.mfrpe), list(part_df.rpediff), list(part_df.rpe2)
    a1value, a1value_deriv = list(part_df.chosen_action1_value), list(part_df.chosen_action1_value_deriv)

    regressors, regressor_names = get_regressors(participant, fmri_run, preprocessed_dir)

    info = Bunch(
        conditions=['first_choice', 'second_choice_and_feedback', 'feedback'],
        onsets=[
            part_df.onset_first_choice,
            pd.concat((part_df.onset_second_choice, part_df.onset_feedback)),
            part_df.onset_feedback,
        ],
        durations=[
            [0]*len(part_df),
            [0]*(len(part_df)*2),
            [0]*len(part_df),
        ],
        pmod=[
            Bunch(
                name=['a1value', 'a1value_deriv'],
                poly=[1, 1], param=[a1value, a1value_deriv]),
            Bunch(
                name=['mfrpe', 'rpediff'],
                poly=[1, 1], param=[mfrpe + rpe2, rpediff + [0]*(len(part_df))]),
            Bunch(name=[], poly=[], param=[]),
        ],
        regressors=regressors,
        regressor_names=regressor_names,
    )
    return info

if __name__ == "__main__":
    print("Run first_level_repl.py instead")
