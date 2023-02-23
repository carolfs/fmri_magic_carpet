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
from psychopy import visual

def read_itis(filename):
    """Read ITIs from a file."""
    with open(filename) as inpf:
        itis = [float(line.strip()) for line in inpf.readlines() if line.strip() and line[0] != '#']
    return itis

def code_to_bin(code, common=True):
    if common:
        return 2 - code % 2
    else:
        return code % 2 + 1

# String replacements
def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def load_image_collection(win, images_directory):
    image_collection = {
        os.path.splitext(fn)[0]: visual.ImageStim(
            win=win,
            pos=(0, 0),
            image=join(images_directory, fn),
            name=os.path.splitext(fn)[0]
        )
        for fn in os.listdir(images_directory) if os.path.splitext(fn)[1] == '.png'
    }
    return image_collection

def get_money_reward(rwrd, x):
    """Round reward for easier paying"""
    return round(rwrd*x, 1)
