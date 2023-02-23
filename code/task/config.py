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

"""Two-stage task: abstract versus story instructions."""

import os
from os.path import join
import random

# Directories
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
ASSETS_DIR = join(CURRENT_DIR, 'assets')
RESULTS_DIR = join(CURRENT_DIR, 'results')
# Money per trial
RWRD = 0.60
# Screen refreshing rate (Hz)
REFRESHING_RATE = 60
# Interval at the end of every block, in seconds
BLOCK_FINAL_INTERVAL = 10
# Keys for the fMRI game
FMRI_TRIGGER = ('5', 't')
# Decision keys
LEFT_KEY = ('left', 'g', '3')
RIGHT_KEY = ('right', 'b', '1')
# Screen resolution
SCN_WIDTH = 1280
SCN_HEIGHT = 1024
# Configuration for tutorial and game
class TutorialConfig:
    final_state_colors = ('red', 'black')
    initial_state_symbols = (7, 8)
    final_state_symbols = ((9, 10), (11, 12))
    trials_per_block = 50
    blocks = 1
    common_prob = 0.7 # Optimal performance 61%
    inside_scanner = False
    fixed_duration_trial = False
    @classmethod
    def get_common(cls, trial):
        if trial == 0 or trial == 1:
            return True
        if trial == 2:
            return False
        return random.random() < cls.common_prob
    @classmethod
    def get_itis(cls):
        return [0]*cls.trials_per_block
TutorialConfig.num_trials = TutorialConfig.blocks*TutorialConfig.trials_per_block

class GameConfig:
    final_state_colors = ('pink', 'blue')
    initial_state_symbols = (1, 2)
    final_state_symbols = ((3, 4), (5, 6))
    trials_per_block = 50
    blocks = 3
    common_prob = 0.7 # Optimal performance 61%
    inside_scanner = True
    fixed_duration_trial = True
    @classmethod
    def get_common(cls, _):
        return random.random() < cls.common_prob
    @classmethod
    def get_itis(cls):
        from utils import read_itis
        itis = read_itis(join(ASSETS_DIR, 'iti.txt'))
        assert len(itis) >= cls.trials_per_block
        itis = itis[:cls.trials_per_block]
        random.shuffle(itis)
        return itis
GameConfig.num_trials = GameConfig.blocks*GameConfig.trials_per_block
