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

"""Tutorial for the two-stage task: abstract versus story instructions."""

import sys
import os
from os.path import join
from psychopy import gui, visual, event

def main():
    # Add parent directory to the path so Python can find this package
    # sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
    from run import init_task
    from config import TutorialConfig, ASSETS_DIR
    from run import load_image_collection, Instructions,\
        run_tutorial, run_game_instructions, create_window

    condition, game_model, results_base_filename = init_task('tutorial')

    test = '--test' in sys.argv
    if test:
        # Displays small window in case we want to abort
        fullscr = False
        # Make the test faster
        TutorialConfig.trials_per_block = 2
    else:
        fullscr = True

    win = create_window(fullscr)
    win.mouseVisible = False
    images = load_image_collection(win, ASSETS_DIR)
    instructions = Instructions(win, images)

    run_tutorial(win, images, condition, instructions, results_base_filename)
    run_game_instructions(condition, game_model, instructions)
    win.close()

if __name__ == '__main__':
    main()
