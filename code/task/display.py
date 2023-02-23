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

import random
import os
from os.path import join
from config import GameConfig, TutorialConfig, ASSETS_DIR,\
    SCN_HEIGHT, SCN_WIDTH
from psychopy import visual, core, logging

REDUCE_BRIGHTNESS = 0.65

class StoryGameDisplay(object):
    def __init__(self, win, images):
        self.images = images
        self.reduce_brightness = visual.Rect(
            win=win,
            pos=(0, 0),
            width=SCN_WIDTH,
            height=SCN_HEIGHT,
            fillColor=(-1, -1, -1),
            opacity=REDUCE_BRIGHTNESS,
            lineColor=None,
            name='Reduce brightness for the fMRI',
        )
    def display_start_of_trial(self, win, trial):
        pass
    def display_carpets(self, win, trial, isymbols, common_transitions):
        isymbols_image = self.images['tibetan.{:02d}{:02d}'.format(*isymbols)]
        self.images['carpets_glow'].draw(win)
        isymbols_image.draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Carpets displayed')
        win.flip()
    def display_selected_carpet(self, win, trial, chosen_symbol, common_transition):
        self.images['selected_carpet'].draw(win)
        self.images['tibetan.{:02d}.selected'.format(chosen_symbol)].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Selected carpet displayed')
        win.flip()
        core.wait(3)
    def display_transition(self, win, trial, final_state_color, common):
        self.images['nap'].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Transition displayed')
        win.flip()
        core.wait(1)
    def display_lamps(self, win, trial, final_state_color, fsymbols):
        fsymbols_image = self.images['tibetan.{:02}{:02}'.format(*fsymbols)]
        self.images['lamps_{}_glow'.format(final_state_color)].draw(win)
        fsymbols_image.draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Lamps displayed')
        win.flip()
    def display_selected_lamp(self, win, trial, final_state_color, chosen_symbol2):
        self.images['selected_lamp_{}'.format(final_state_color)].draw(win)
        self.images['tibetan.{:02d}.selected'.format(chosen_symbol2)].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Selected lamp displayed')
        win.flip()
        core.wait(3)
    def display_reward(self, win, trial, final_state_color, chosen_symbol2):
        self.images['genie_coin'].draw(win)
        self.images['reward_{}'.format(final_state_color)].draw(win)
        self.images['tibetan.{:02}'.format(chosen_symbol2)].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Reward displayed')
        win.flip()
        core.wait(1.5)
    def display_no_reward(self, win, trial, final_state_color, chosen_symbol2):
        self.images['genie_zero'].draw(win)
        self.images['reward_{}'.format(final_state_color)].draw(win)
        self.images['tibetan.{:02}'.format(chosen_symbol2)].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='No reward displayed')
        win.flip()
        core.wait(1.5)
    def display_end_of_trial(self, win, trial):
        self.images['fixation_point'].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Fixation point displayed')
        win.flip()
    def display_slow1(self, win):
        self.images['slow1'].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Slow screen displayed')
        win.flip()
        core.wait(3)
    def display_slow2(self, win, final_state_color, fsymbols):
        self.images['lamps_{}'.format(final_state_color)].draw(win)
        self.images['tibetan.{:02}{:02}'.format(*fsymbols)].draw(win)
        self.images['slow2'].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Slow screen displayed')
        win.flip()
        core.wait(2)
    def display_break(self, win):
        self.images['break'].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Break screen displayed')
        win.flip()

class AbstractGameDisplay(object):
    def __init__(self, win, images):
        self.images = images
        self.reduce_brightness = visual.Rect(
            win=win,
            pos=(0, 0),
            width=SCN_WIDTH,
            height=SCN_HEIGHT,
            fillColor=(-1, -1, -1),
            opacity=REDUCE_BRIGHTNESS,
            lineColor=None,
            name='Reduce brightness for the fMRI',
        )
    def display_start_of_trial(self, win, trial):
        pass
    def display_carpets(self, win, trial, isymbols, common_transitions):
        isymbols_image = self.images['tibetan.{:02d}{:02d}'.format(*isymbols)]
        self.images['abstract_carpets_glow'].draw(win)
        isymbols_image.draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Carpets displayed')
        win.flip()
    def display_selected_carpet(self, win, trial, chosen_symbol, common_transition):
        self.images['selected_carpet_abstract'].draw(win)
        self.images['tibetan.{:02d}.selected'.format(chosen_symbol)].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Selected carpet displayed')
        win.flip()
        core.wait(3)
    def display_transition(self, win, trial, final_state_color, common):
        self.images['nap'].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Transition displayed')
        win.flip()
        core.wait(1)
    def display_lamps(self, win, trial, final_state_color, fsymbols):
        fsymbols_image = self.images['tibetan.{:02}{:02}'.format(*fsymbols)]
        self.images['lamps_{}_glow'.format(final_state_color)].draw(win)
        fsymbols_image.draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Lamps displayed')
        win.flip()
    def display_selected_lamp(self, win, trial, final_state_color, chosen_symbol2):
        self.images['selected_lamp_{}'.format(final_state_color)].draw(win)
        self.images['tibetan.{:02d}.selected'.format(chosen_symbol2)].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Selected lamp displayed')
        win.flip()
        core.wait(3)
    def display_reward(self, win, trial, final_state_color, chosen_symbol2):
        self.images['genie_coin'].draw(win)
        self.images['reward_{}'.format(final_state_color)].draw(win)
        self.images['tibetan.{:02}'.format(chosen_symbol2)].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Reward displayed')
        win.flip()
        core.wait(1.5)
    def display_no_reward(self, win, trial, final_state_color, chosen_symbol2):
        self.images['genie_zero'].draw(win)
        self.images['reward_{}'.format(final_state_color)].draw(win)
        self.images['tibetan.{:02}'.format(chosen_symbol2)].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='No reward displayed')
        win.flip()
        core.wait(1.5)
    def display_end_of_trial(self, win, trial):
        self.images['fixation_point'].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Fixation point displayed')
        win.flip()
    def display_slow1(self, win):
        self.images['slow_abstract'].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Slow screen displayed')
        win.flip()
        core.wait(3)
    def display_slow2(self, win, final_state_color, fsymbols):
        self.images['slow_abstract'].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Slow screen displayed')
        win.flip()
        core.wait(2)
    def display_break(self, win):
        self.images['break'].draw(win)
        self.reduce_brightness.draw(win)
        win.logOnFlip(level=logging.EXP, msg='Break screen displayed')
        win.flip()

class StoryTutorialDisplay(object):
    def __init__(self, win, images, mountain_sides):
        self.images = images
        self.mountain_sides = mountain_sides
        self.visits_to_mountains = {color: 0 for color in TutorialConfig.final_state_colors}
        # Create frame to display messages
        self.msg_frame = visual.Rect(
            win=win,
            pos=(0, 400),
            width=1180,
            height=80,
            fillColor=(1.0, 1.0, 1.0),
            opacity=0.9,
            lineColor=None,
            name='Tutorial message frame',
        )
        self.msg_text = visual.TextStim(
            win=win,
            pos=(-560, 405),
            height=30,
            fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
            font='OpenSans',
            color=(-1, -1, -1),
            wrapWidth=1120,
            alignText='left',
            anchorHoriz='left',
            anchorVert='center',
            name='Tutorial message text'
        )
        self.center_text = visual.TextStim(
            win=win,
            pos=(0, 0),
            height=80,
            wrapWidth=980,
            fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
            font='OpenSans',
            color=(1, 1, 1),
            name='Center text'
        )
    def display_start_of_trial(self, win, trial):
        self.center_text.text = 'Tutorial flight #{}'.format(trial + 1)
        self.center_text.draw(win)
        win.flip()
        core.wait(3)
    def display_carpets(self, win, trial, isymbols, common_transitions):
        isymbols_image = self.images['tibetan.{:02d}{:02d}'.format(*isymbols)]
        destination_image = self.images['carpets_to_{}_{}'.format(
            *[common_transitions[symbol] for symbol in isymbols]
        )]

        def draw_main_images():
            self.images['carpets_tutorial'].draw(win)
            isymbols_image.draw(win)
            destination_image.draw(win)

        if trial < 3:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'You took your magic carpets out of the cupboard '\
                'and unrolled them on the floor.'
            self.msg_text.draw(win)
            win.flip()
            core.wait(4.5)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            if trial < 2:
                draw_main_images()
                self.images['left_carpet_destination'].draw(win)
                self.msg_frame.draw(win)
                self.msg_text.text = "On the left you put the carpet that was enchanted "\
                    "to fly to {} Mountain …".format(
                        common_transitions[isymbols[0]].capitalize())
                self.msg_text.draw(win)
                win.flip()
                core.wait(4.5)

                draw_main_images()
                win.flip()
                core.wait(0.5)

                draw_main_images()
                self.images['right_carpet_destination'].draw(win)
                self.msg_frame.draw(win)
                self.msg_text.text = "… and on the right the carpet that was enchanted "\
                    "to fly to {} Mountain.".format(
                        common_transitions[isymbols[1]].capitalize())
                self.msg_text.draw(win)
                win.flip()
                core.wait(4.5)

                draw_main_images()
                win.flip()
                core.wait(0.5)

                draw_main_images()
                self.images['tutorial_carpet_symbols'].draw(win)
                self.msg_frame.draw(win)
                self.msg_text.text = "The symbols written on the carpets mean “{} "\
                    "Mountain” and “{} Mountain” in the local language.".format(
                        common_transitions[isymbols[0]].capitalize(),
                        common_transitions[isymbols[1]].capitalize(),
                    )
                self.msg_text.draw(win)
                win.flip()
                core.wait(6)

                draw_main_images()
                win.flip()
                core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'You will soon be able to choose a carpet '\
                'and fly on it by pressing the left or right arrow key.'
            self.msg_text.draw(win)
            win.flip()
            core.wait(6)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'When the carpets start to glow, you have 2 seconds '\
                'to press a key, or else they will fly away without you.'
            self.msg_text.draw(win)
            win.flip()
            core.wait(6)

            draw_main_images()
            win.flip()
            core.wait(0.5)
        elif trial < 10:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = "Your carpets are out of the cupboard and about "\
                "to glow. Prepare to make your choice."
            self.msg_text.draw(win)
            win.flip()
            core.wait(5)

        # Glow carpets for response
        self.images['carpets_glow_tutorial'].draw(win)
        isymbols_image.draw(win)
        destination_image.draw(win)
        win.flip()
    def display_selected_carpet(self, win, trial, chosen_symbol, common_transition):
        destination_image = self.images['selected_{}'.format(common_transition)]
        def draw_main_images():
            self.images['selected_carpet_tutorial'].draw(win)
            self.images['tutorial.tibetan.{:02d}.selected'.format(chosen_symbol)].draw(win)
            destination_image.draw(win)
        if trial < 10:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'You chose the carpet enchanted to fly to '\
                '{} Mountain. Bon voyage!'.format(common_transition.capitalize())
            self.msg_text.draw(win)
            win.flip()
            core.wait(4)

            draw_main_images()
            win.flip()
            core.wait(0.5)
        else:
            draw_main_images()
            win.flip()
            core.wait(3)
    def display_transition(self, win, trial, final_state_color, common):
        transition_image = self.images['flight_{}-{}_{}{}'.format(
            final_state_color,
            self.mountain_sides[0],
            self.mountain_sides[1],
            '-wind' if not common else '',
        )]

        if common:
            self.msg_text.text = 'Your flight to {} Mountain goes well, without '\
                'any incidents.'.format(final_state_color.capitalize())
        else:
            colors = TutorialConfig.final_state_colors
            self.msg_text.text = 'Oh, no! The wind near {} Mountain is too strong. '\
                'You decide to land your carpet on {} Mountain instead.'.format(
                    colors[1 - colors.index(final_state_color)].capitalize(),
                    final_state_color.capitalize(),
                )
        if trial < 10:
            transition_image.draw(win)
            win.flip()
            core.wait(0.5)

            transition_image.draw(win)
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            win.flip()
            core.wait(3 if common else 6)

            transition_image.draw(win)
            win.flip()
            core.wait(0.5)
        else:
            transition_image.draw(win)
            win.flip()
            core.wait(2)
    def display_lamps(self, win, trial, final_state_color, fsymbols):
        fsymbols_image = self.images['tibetan.{:02}{:02}'.format(*fsymbols)]
        def draw_main_images():
            self.images['lamps_{}'.format(final_state_color)].draw(win)
            fsymbols_image.draw(win)

        if self.visits_to_mountains[final_state_color] < 1:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'You have safely landed on {} Mountain.'.format(
                final_state_color.capitalize())
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            win.flip()
            core.wait(4.5)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'Here are the lamps where the {} Mountain genies live.'.format(
                final_state_color.capitalize())
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            win.flip()
            core.wait(4.5)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'The lamp on the left is home to the genie '\
                'whose name is shown below.'
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            self.images['left_lamp_symbol'].draw(win)
            win.flip()
            core.wait(5)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'The lamp on the right is home to the genie '\
                'whose name is shown below.'
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            self.images['right_lamp_symbol'].draw(win)
            win.flip()
            core.wait(5)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'You will soon be able to choose a lamp and '\
                'rub it by pressing the left or right arrow key.'
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            win.flip()
            core.wait(6)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'When the lamps start to glow, you have 2 seconds '\
                'to press a key, or else the genies will go to sleep.'
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            win.flip()
            core.wait(6)

            draw_main_images()
            win.flip()
            core.wait(0.5)
        elif trial < 10:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'You have safely landed on {} Mountain, and the '\
                'lamps are about to glow. Prepare to make your choice.'.format(
                    final_state_color.capitalize())
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            win.flip()
            core.wait(5)

            draw_main_images()
            win.flip()
            core.wait(0.5)

        self.images['lamps_{}_glow'.format(final_state_color)].draw(win)
        fsymbols_image.draw(win)
        win.flip()
        self.visits_to_mountains[final_state_color] += 1
    def display_selected_lamp(self, win, trial, final_state_color, chosen_symbol2):
        def draw_main_images():
            self.images['selected_lamp_{}'.format(final_state_color)].draw(win)
            self.images['tibetan.{:02d}.selected'.format(chosen_symbol2)].draw(win)
        if trial < 10:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'You pick up this lamp and rub it.'
            self.msg_text.draw(win)
            win.flip()
            core.wait(3.5)

            draw_main_images()
            win.flip()
            core.wait(0.5)
        else:
            draw_main_images()
            win.flip()
            core.wait(3)
    def display_reward(self, win, trial, final_state_color, chosen_symbol2):
        def draw_main_images():
            self.images['genie_coin'].draw(win)
            self.images['reward_{}'.format(final_state_color)].draw(win)
            self.images['tibetan.{:02}'.format(chosen_symbol2)].draw(win)

        if trial < 10:
            draw_main_images()
            win.flip()
            core.wait(1.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'The genie came out of his lamp, listened to a song, '\
                'and gave you a gold coin!'
            self.msg_text.draw(win)
            win.flip()
            core.wait(5)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            if trial < 2:
                draw_main_images()
                self.msg_frame.draw(win)
                self.msg_text.text = 'Remember this genie’s name in case you want to choose his '\
                    'lamp again in the future.'
                self.msg_text.draw(win)
                self.images['rubbed_lamp'].draw(win)
                win.flip()
                core.wait(5)

                draw_main_images()
                self.images['rubbed_lamp'].draw(win)
                win.flip()
                core.wait(0.5)

                draw_main_images()
                self.msg_frame.draw(win)
                self.msg_text.text = 'The color of his lamp reminds you he lives '\
                    'on {} Mountain.'.format(final_state_color.capitalize())
                self.msg_text.draw(win)
                self.images['rubbed_lamp'].draw(win)
                win.flip()
                core.wait(5)

                draw_main_images()
                win.flip()
                core.wait(0.5)
        else:
            draw_main_images()
            win.flip()
            core.wait(1.5)
    def display_no_reward(self, win, trial, final_state_color, chosen_symbol2):
        def draw_main_images():
            self.images['genie_zero'].draw(win)
            self.images['reward_{}'.format(final_state_color)].draw(win)
            self.images['tibetan.{:02}'.format(chosen_symbol2)].draw(win)

        if trial < 10:
            draw_main_images()
            win.flip()
            core.wait(1.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'The genie stayed inside his lamp, and you didn’t get a gold coin.'
            self.msg_text.draw(win)
            win.flip()
            core.wait(5)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            if trial < 2:
                draw_main_images()
                self.msg_frame.draw(win)
                self.msg_text.text = 'Remember this genie’s name in case you want to choose his '\
                    'lamp again in the future.'
                self.msg_text.draw(win)
                self.images['rubbed_lamp'].draw(win)
                win.flip()
                core.wait(5)

                draw_main_images()
                self.images['rubbed_lamp'].draw(win)
                win.flip()
                core.wait(0.5)

                draw_main_images()
                self.msg_frame.draw(win)
                self.msg_text.text = 'The color of his lamp reminds you he lives '\
                    'on {} Mountain.'.format(final_state_color.capitalize())
                self.msg_text.draw(win)
                self.images['rubbed_lamp'].draw(win)
                win.flip()
                core.wait(5)

                draw_main_images()
                win.flip()
                core.wait(0.5)
        else:
            draw_main_images()
            win.flip()
            core.wait(1.5)
    def display_end_of_trial(self, win, _):
        pass
    def display_slow1(self, win):
        self.images['slow1'].draw(win)
        win.flip()
        core.wait(4)
    def display_slow2(self, win, final_state_color, fsymbols):
        self.images['lamps_{}'.format(final_state_color)].draw(win)
        self.images['tibetan.{:02}{:02}'.format(*fsymbols)].draw(win)
        self.images['slow2'].draw(win)
        win.flip()
        core.wait(4)
    def display_break(self, win):
        pass

class AbstractTutorialDisplay(object):
    def __init__(self, win, images):
        self.images = images
        self.visits_to_mountains = {color: 0 for color in TutorialConfig.final_state_colors}
        # Create frame to display messages
        self.msg_frame = visual.Rect(
            win=win,
            pos=(0, 400),
            width=1180,
            height=80,
            fillColor=(1.0, 1.0, 1.0),
            opacity=0.9,
            lineColor=None,
            name='Tutorial message frame',
        )
        self.msg_text = visual.TextStim(
            win=win,
            pos=(-560, 405),
            height=30,
            fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
            font='OpenSans',
            color=(-1, -1, -1),
            wrapWidth=1120,
            alignText='left',
            anchorHoriz='left',
            anchorVert='center',
            name='Tutorial message text'
        )
        self.center_text = visual.TextStim(
            win=win,
            pos=(0, 0),
            height=80,
            wrapWidth=980,
            fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
            font='OpenSans',
            color=(1, 1, 1),
            name='Center text'
        )
    def display_start_of_trial(self, win, trial):
        self.center_text.text = 'Tutorial trial #{}'.format(trial + 1)
        self.center_text.draw(win)
        win.flip()
        core.wait(3)
    def display_carpets(self, win, trial, isymbols, _):
        isymbols_image = self.images['original.tibetan.{:02d}{:02d}'.format(*isymbols)]

        def draw_main_images():
            self.images['abstract_carpets'].draw(win)
            isymbols_image.draw(win)

        if trial < 3:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'You will soon be able to choose a box '\
                'by pressing the left or right arrow key.'
            self.msg_text.draw(win)
            win.flip()
            core.wait(6)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'When the boxes start to glow, you have 2 seconds '\
                'to press a key.'
            self.msg_text.draw(win)
            win.flip()
            core.wait(6)

            draw_main_images()
            win.flip()
            core.wait(0.5)
        elif trial < 5:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = "The boxes are about "\
                "to glow. Prepare to make your choice."
            self.msg_text.draw(win)
            win.flip()
            core.wait(5)

        # Glow carpets for response
        self.images['abstract_carpets_glow'].draw(win)
        isymbols_image.draw(win)
        win.flip()
    def display_selected_carpet(self, win, trial, chosen_symbol, common_transition):
        def draw_main_images():
            self.images['selected_carpet_abstract'].draw(win)
            self.images['original.tibetan.{:02d}.selected'.format(chosen_symbol)].draw(win)
            
        if trial < 5:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'You chose this box.'
            self.msg_text.draw(win)
            win.flip()
            core.wait(4)

            draw_main_images()
            win.flip()
            core.wait(0.5)
        else:
            draw_main_images()
            win.flip()
            core.wait(3)
    def display_transition(self, win, trial, final_state_color, common):
        self.images['nap'].draw(win)
        win.flip()
        core.wait(1)
    def display_lamps(self, win, trial, final_state_color, fsymbols):
        fsymbols_image = self.images['tibetan.{:02}{:02}'.format(*fsymbols)]
        def draw_main_images():
            self.images['lamps_{}'.format(final_state_color)].draw(win)
            fsymbols_image.draw(win)

        if self.visits_to_mountains[final_state_color] < 1:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'Here are the {} lamps.'.format(
                final_state_color)
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            win.flip()
            core.wait(4.5)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'You will soon be able to choose a lamp '\
                'by pressing the left or right arrow key.'
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            win.flip()
            core.wait(6)

            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'When the lamps start to glow, you have 2 seconds '\
                'to press a key.'
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            win.flip()
            core.wait(6)

            draw_main_images()
            win.flip()
            core.wait(0.5)
        elif trial < 5:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_text.text = 'The '\
                '{} lamps are about to glow. Prepare to make your choice.'.format(
                    final_state_color)
            self.msg_frame.draw(win)
            self.msg_text.draw(win)
            win.flip()
            core.wait(5)

            draw_main_images()
            win.flip()
            core.wait(0.5)

        self.images['lamps_{}_glow'.format(final_state_color)].draw(win)
        fsymbols_image.draw(win)
        win.flip()
        self.visits_to_mountains[final_state_color] += 1
    def display_selected_lamp(self, win, trial, final_state_color, chosen_symbol2):
        def draw_main_images():
            self.images['selected_lamp_{}'.format(final_state_color)].draw(win)
            self.images['tibetan.{:02d}.selected'.format(chosen_symbol2)].draw(win)
        if trial < 5:
            draw_main_images()
            win.flip()
            core.wait(0.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'You chose this lamp.'
            self.msg_text.draw(win)
            win.flip()
            core.wait(3.5)

            draw_main_images()
            win.flip()
            core.wait(0.5)
        else:
            draw_main_images()
            win.flip()
            core.wait(3)
    def display_reward(self, win, trial, final_state_color, chosen_symbol2):
        def draw_main_images():
            self.images['genie_coin'].draw(win)
            self.images['reward_{}'.format(final_state_color)].draw(win)
            self.images['tibetan.{:02}'.format(chosen_symbol2)].draw(win)

        if trial < 5:
            draw_main_images()
            win.flip()
            core.wait(1.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'The genie came out of his lamp '\
                'and gave you a gold coin!'
            self.msg_text.draw(win)
            win.flip()
            core.wait(5)

            draw_main_images()
            win.flip()
            core.wait(0.5)
        else:
            draw_main_images()
            win.flip()
            core.wait(1.5)
    def display_no_reward(self, win, trial, final_state_color, chosen_symbol2):
        def draw_main_images():
            self.images['genie_zero'].draw(win)
            self.images['reward_{}'.format(final_state_color)].draw(win)
            self.images['tibetan.{:02}'.format(chosen_symbol2)].draw(win)

        if trial < 5:
            draw_main_images()
            win.flip()
            core.wait(1.5)

            draw_main_images()
            self.msg_frame.draw(win)
            self.msg_text.text = 'The genie stayed inside his lamp, and you didn’t get a gold coin.'
            self.msg_text.draw(win)
            win.flip()
            core.wait(5)

            draw_main_images()
            win.flip()
            core.wait(0.5)
        else:
            draw_main_images()
            win.flip()
            core.wait(1.5)
    def display_end_of_trial(self, win, _):
        pass
    def display_slow1(self, win):
        self.images['slow_abstract'].draw(win)
        win.flip()
        core.wait(4)
    def display_slow2(self, win, final_state_color, fsymbols):
        self.images['slow_abstract'].draw(win)
        win.flip()
        core.wait(4)
    def display_break(self, win):
        pass
