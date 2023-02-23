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

"""Game for the magic carpet experiment: abstract versus story instructions."""

import sys
from psychopy import core, event

def main():
    # Add parent directory to the path so Python can find this package
    # sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
    from run import init_task, load_image_collection,\
        run_game, create_window
    from config import GameConfig, ASSETS_DIR

    condition, game_model, results_base_filename = init_task('game')

    test = len(sys.argv) > 1 and '--test' in sys.argv
    if test:
        # Displays small window in case we want to abort
        fullscr = False
        # Make the test faster
        GameConfig.blocks = 2
        GameConfig.trials_per_block = 2
    else:
        fullscr = True
    win = create_window(fullscr)

    images = load_image_collection(win, ASSETS_DIR)
    run_game(win, images, condition, game_model, results_base_filename)
    event.waitKeys(keyList=['escape', 'space'])
    win.close()
    core.quit()

if __name__ == '__main__':
    main()
