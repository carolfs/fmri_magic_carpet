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

import io
import sys
import random
import os
import csv
from os.path import join
from psychopy import visual, core, event, data, gui, logging, clock
try:
    import pylink
except ImportError:
    sys.stderr.write('Error: pylink not available')
import pandas as pd
from model import Trial, Model
from utils import code_to_bin, replace_all,\
    load_image_collection, get_money_reward
from config import ASSETS_DIR, TutorialConfig, GameConfig, RWRD,\
    BLOCK_FINAL_INTERVAL, RESULTS_DIR, FMRI_TRIGGER, LEFT_KEY, RIGHT_KEY,\
    SCN_WIDTH, SCN_HEIGHT
from display import AbstractGameDisplay, StoryGameDisplay,\
    AbstractTutorialDisplay, StoryTutorialDisplay

CSV_FIELDNAMES = (
    'trial', 'common', 'reward.1.1', 'reward.1.2', 'reward.2.1',
    'reward.2.2', 'isymbol_lft', 'isymbol_rgt', 'rt1', 'choice1', 'final_state',
    'fsymbol_lft', 'fsymbol_rgt', 'rt2', 'choice2', 'reward', 'slow')

# Trial duration in seconds (ITIs not considered)
TRIAL_DURATION = 12.5

class FileExistsError(Exception):
    pass

def start_times(itis):
    total = 0
    times = []
    for iti in itis:
        times.append(total)
        total += iti
    return times

EDF_FN = 'mgcarpet.edf'

def create_window(fullscr, main_screen=True):
    # Create PsychoPy window
    kwargs = {
        'units': 'pix',
        'color': '#404040',
    }
    if fullscr:
        kwargs['fullscr'] = True
    else:
        kwargs['fullscr'] = False
        kwargs['size'] = [SCN_WIDTH, SCN_HEIGHT]
    win = visual.Window(**kwargs)
    win.mouseVisible = False
    return win

def close_window_wait_enter(win, logfl):
    logfl.setLevel(logging.CRITICAL)
    win.close()
    input('Press ENTER to continue...')
    win = create_window(fullscr=True)
    logfl.setLevel(logging.INFO)
    return win

def run_trial_sequence(win, config, display, model, results_base_filename):
    rewards = 0
    slow_trials = 0
    common_transitions = {
        isymbol_code: color
        for isymbol_code, color, fsymbol_codes in model.get_paths(True)
    }
    if config.inside_scanner:
        # Logging
        logfl = logging.LogFile(results_base_filename + '.log', level=logging.INFO, filemode='w')
    # Results file
    game_results_filename = '{}_game.csv'.format(results_base_filename)
    with io.open(game_results_filename, 'w', encoding='utf-8') as outf:
        csv_writer = csv.DictWriter(outf, fieldnames=CSV_FIELDNAMES)
        csv_writer.writeheader()
        # Trial loop
        trial_sequence = Trial.get_sequence(config, model)
        for block in range(config.blocks):
            # Calculate block duration
            itis = config.get_itis()
            block_duration = TRIAL_DURATION*config.trials_per_block +\
                sum(itis) + BLOCK_FINAL_INTERVAL
            logging.log(
                level=logging.EXP,
                msg='Block duration should be {} seconds'.format(block_duration))
            trial_iti_durations = [TRIAL_DURATION + iti for iti in itis]
            trial_start_times = start_times(trial_iti_durations)
            if config.inside_scanner:
                # Wait for fMRI trigger or ESC
                while True:
                    display.display_end_of_trial(win, -1)
                    keys = event.waitKeys(keyList=(FMRI_TRIGGER + ('escape',)))
                    if keys[0] in FMRI_TRIGGER:
                        break
                    else:
                        win = close_window_wait_enter(win, logfl)
                # Eye tracker
                try:
                    tracker = pylink.EyeLink('100.1.1.1')
                except:
                    from unittest.mock import MagicMock
                    tracker = MagicMock()
                    sys.stderr.write('Could not connect to eye tracker\n')
                    logging.log(level=logging.ERROR, msg='Could not connect to eye tracker')
                tracker.openDataFile(EDF_FN)
                block_clock = clock.Clock()
                # Start eye tracker
                tracker.startRecording(1, 1, 1, 1)
                logging.log(
                    level=logging.EXP,
                    msg='Eye tracker started')
            for _ in range(config.trials_per_block):
                trial = next(trial_sequence)
                if config.inside_scanner:
                    tracker.sendMessage('Trial {} started'.format(trial.number))
                completed_trials = trial.number - slow_trials
                logging.log(level=logging.EXP, msg='Start of trial {}'.format(trial.number))
                row = {'trial': trial.number, 'common': int(trial.common)}
                for isymbol in trial.initial_state.symbols:
                    for fsymbol in isymbol.final_state.symbols:
                        key = 'reward.{}.{}'.format(
                            code_to_bin(isymbol.code, trial.common), code_to_bin(fsymbol.code))
                        row[key] = fsymbol.reward_probability
                row['isymbol_lft'] = code_to_bin(trial.initial_state.symbols[0].code)
                row['isymbol_rgt'] = code_to_bin(trial.initial_state.symbols[1].code)

                display.display_start_of_trial(win, trial.number)

                # First-stage choice
                isymbols = [symbol.code for symbol in trial.initial_state.symbols]
                display.display_carpets(win, completed_trials, isymbols, common_transitions)
                if config.inside_scanner:
                    logging.log(
                        level=logging.EXP,
                        msg='Eye-tracker time: {}'.format(tracker.trackerTime()))
                    tracker.sendMessage('Carpets displayed')
                if config.fixed_duration_trial:
                    trial_period = clock.StaticPeriod(screenHz=60)
                    trial_index = trial.number % config.trials_per_block
                    trial_duration = trial_iti_durations[trial_index] +\
                        trial_start_times[trial_index] - block_clock.getTime()
                    trial_period.start(trial_duration)

                event.clearEvents()
                keys_times = event.waitKeys(
                    maxWait=2, keyList=(LEFT_KEY + RIGHT_KEY), timeStamped=core.Clock())

                if keys_times is None:
                    slow_trials += 1
                    display.display_slow1(win)
                    row.update({
                        'rt1': '',
                        'choice1': '',
                        'final_state': '',
                        'fsymbol_lft': '',
                        'fsymbol_rgt': '',
                        'rt2': '',
                        'choice2': '',
                        'reward': 0,
                        'slow': 1,
                    })
                else:
                    choice1, rt1 = keys_times[0]
                    row['rt1'] = rt1
                    chosen_symbol1 = trial.initial_state.symbols[int(choice1 in RIGHT_KEY)]
                    row['choice1'] = code_to_bin(chosen_symbol1.code)

                    display.display_selected_carpet(
                        win, completed_trials, chosen_symbol1.code,
                        common_transitions[chosen_symbol1.code])
                    if config.inside_scanner:
                        logging.log(
                            level=logging.EXP,
                            msg='Eye-tracker time: {}'.format(tracker.trackerTime()))
                        tracker.sendMessage('Selected carpet displayed')

                    # Transition
                    final_state = chosen_symbol1.final_state
                    row['final_state'] = code_to_bin(chosen_symbol1.code, trial.common)

                    display.display_transition(
                        win, completed_trials, final_state.color, trial.common)
                    if config.inside_scanner:
                        tracker.sendMessage('Transition displayed')

                    # Second-stage choice
                    fsymbols = [symbol.code for symbol in final_state.symbols]
                    row['fsymbol_lft'] = code_to_bin(final_state.symbols[0].code)
                    row['fsymbol_rgt'] = code_to_bin(final_state.symbols[1].code)

                    display.display_lamps(win, completed_trials, final_state.color, fsymbols)
                    if config.inside_scanner:
                        logging.log(
                            level=logging.EXP,
                            msg='Eye-tracker time: {}'.format(tracker.trackerTime()))
                        tracker.sendMessage('Lamps displayed')

                    event.clearEvents()
                    keys_times = event.waitKeys(
                        maxWait=2, keyList=(LEFT_KEY + RIGHT_KEY), timeStamped=core.Clock())
                    if keys_times is None:
                        slow_trials += 1
                        display.display_slow2(win, final_state.color, fsymbols)
                        row.update({
                            'rt2': '',
                            'choice2': '',
                            'reward': 0,
                            'slow': 1,
                        })
                    else:
                        choice2, rt2 = keys_times[0]
                        row['rt2'] = rt2
                        chosen_symbol2 = final_state.symbols[int(choice2 in RIGHT_KEY)]
                        row['choice2'] = code_to_bin(chosen_symbol2.code)

                        display.display_selected_lamp(
                            win, completed_trials, final_state.color,
                            chosen_symbol2.code)
                        if config.inside_scanner:
                            logging.log(
                                level=logging.EXP,
                                msg='Eye-tracker time: {}'.format(
                                    tracker.trackerTime()))
                            tracker.sendMessage('Selected lamp displayed')

                        # Reward
                        reward = chosen_symbol2.reward
                        row['reward'] = reward
                        row['slow'] = 0
                        if reward:
                            rewards += 1
                            display.display_reward(
                                win, completed_trials, final_state.color,
                                chosen_symbol2.code)
                        else:
                            display.display_no_reward(
                                win, completed_trials, final_state.color,
                                chosen_symbol2.code)
                        if config.inside_scanner:
                            tracker.sendMessage('Feedback displayed')
                logging.log(level=logging.EXP, msg='End of trial {}'.format(trial.number))
                display.display_end_of_trial(win, trial.number)
                if config.inside_scanner:
                    tracker.sendMessage('Fixation point displayed')
                if config.fixed_duration_trial:
                    trial_period.complete()

                assert all([fdn in row for fdn in CSV_FIELDNAMES])
                assert all([key in CSV_FIELDNAMES for key in row])
                csv_writer.writerow(row)
            # Break
            if config.inside_scanner:
                # Wait extra
                logging.log(
                    level=logging.EXP,
                    msg='End of block interval for {} seconds'.format(
                        block_duration - block_clock.getTime()))
                core.wait(block_duration - block_clock.getTime())
                logging.log(
                    level=logging.EXP,
                    msg='Block ended after {} seconds'.format(block_clock.getTime()))
                tracker.stopRecording()
                tracker.setOfflineMode()
                tracker.closeDataFile()
                tracker.receiveDataFile(
                    EDF_FN, results_base_filename + '_block_{}.edf'.format(block))
            if block + 1 < config.blocks:
                display.display_break(win)
                event.clearEvents()
                if config.inside_scanner:
                    event.waitKeys(keyList=['escape'])
                    win = close_window_wait_enter(win, logfl)
                else:
                    event.waitKeys(keyList=['space'])

    if config.inside_scanner:
        tracker.close()
    return rewards, win

def get_string_replacements(config, mountain_sides, model, capitalize_colors):
    string_replacements = {
        '[color1]': mountain_sides[0].capitalize() if capitalize_colors else mountain_sides[0],
        '[color2]': mountain_sides[1].capitalize() if capitalize_colors else mountain_sides[1],
        '[num_trials]': str(config.num_trials),
    }
    for num, (isymbol_code, color, fsymbol_codes) in enumerate(model.get_paths(True)):
        string_replacements.update({
            '[color_common{}]'.format(num + 1): color.capitalize() if capitalize_colors else color,
            '[isymbol{}]'.format(num + 1): '{:02d}'.format(isymbol_code),
            '[fsymbol{}1]'.format(num + 1): '{:02d}'.format(fsymbol_codes[0]),
            '[fsymbol{}2]'.format(num + 1): '{:02d}'.format(fsymbol_codes[1]),
        })
    return string_replacements

class Instructions(object):
    def __init__(self, win, images):
        self.win = win
        self.images = images
        self.instr_text = visual.TextStim(
            win=win,
            pos=(-527, 359),
            anchorHoriz='left',
            alignText='left',
            height=35,
            fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
            font='OpenSans',
            color=(1, 1, 1),
            wrapWidth=1077,
            name='Instructions text'
        )
        self.instr_all_text = visual.TextStim(
            win=win,
            pos=(-527, 0),
            anchorHoriz='left',
            alignText='left',
            height=35,
            fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
            font='OpenSans',
            color=(1, 1, 1),
            wrapWidth=1077,
            name='Introduction text'
        )
        self.instr_image = visual.ImageStim(
            win=win,
            pos=(0, -97),
            name='Instructions image'
        )
    @staticmethod
    def __parse_instructions(instructions_fn, string_replacements):
        with io.open(join(ASSETS_DIR, instructions_fn), encoding='utf-8') as instr_file:
            screens = []
            images = []
            while True:
                line = instr_file.readline()
                if line == "":
                    text = replace_all(text, string_replacements)
                    screens.append({'text': text, 'images': tuple(images)})
                    break
                elif line.startswith('"'):
                    text = line[1:]
                    while True:
                        if len(line.strip()) > 0 and line.strip()[-1] == '"':
                            text = text.strip()[:-1]
                            break
                        line = instr_file.readline()
                        text += line
                elif line == '\n':
                    text = replace_all(text, string_replacements)
                    screens.append({'text': text, 'images': tuple(images)})
                    images = []
                else:
                    image = replace_all(line.strip(), string_replacements)
                    images.append(image)
        return screens
    def display(self, instructions_fn, string_replacements):
        screens = self.__parse_instructions(instructions_fn, string_replacements)
        scrnum = 0
        while True:
            screen = screens[scrnum]
            if screen['text'].find('\n') != -1:
                self.instr_all_text.text = screen['text']
                self.instr_all_text.draw()
            else:
                self.instr_text.text = screen['text']
                self.instr_text.draw()
                for image in screen['images']:
                    self.instr_image.image = join(
                        ASSETS_DIR, 'instructions', image.lower() + '.png')
                    self.instr_image.draw()
            keyList = tuple()
            if scrnum > 0:
                self.images['arrow_left'].draw()
                keyList += ('left',)
            if scrnum < (len(screens) - 1):
                self.images['arrow_right'].draw()
                keyList += ('right',)
            else:
                keyList += ('space',)
            self.win.flip()
            keys = event.waitKeys(keyList=keyList)
            if 'left' in keys:
                scrnum -= 1
                if scrnum < 0:
                    scrnum = 1
            elif 'right' in keys:
                scrnum += 1
            else:
                assert 'space' in keys
                break

def run_quiz(win, quiz_file, images, string_replacements):
    quiz_text = visual.TextStim(
        win=win,
        pos=(-450, +50),
        anchorHoriz='left',
        alignText='left',
        height=35,
        fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
        font='OpenSans',
        color=(1, 1, 1),
        wrapWidth=900,
        name='Quiz text'
    )
    quiz_help_text = visual.TextStim(
        win=win,
        pos=(-450, -250),
        text='Press the key corresponding to the correct answer.',
        anchorHoriz='left',
        alignText='left',
        height=35,
        fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
        font='OpenSans',
        color=(1, 1, 1),
        wrapWidth=900,
        name='Quiz help text'
    )
    quiz_feedback = visual.TextStim(
        win=win,
        pos=(-250, -250),
        anchorHoriz='left',
        alignText='left',
        height=35,
        fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
        font='OpenSans',
        color=(1, 1, 1),
        wrapWidth=900,
        name='Quiz feedback text'
    )
    with io.open(quiz_file, encoding='utf-8') as qf:
        quiz = qf.read()
    quiz = eval(quiz)

    answered = []
    while True:
        for qn, (question, answer, correct, maxanswer) in enumerate(quiz):
            if qn in answered:
                continue
            quiz_text.text = "{}\n\n{}".format(
                replace_all(question, string_replacements),
                replace_all(answer, string_replacements))
            quiz_text.draw()
            quiz_help_text.draw()
            win.flip()
            keyList = [chr(ord('a') + i) for i in range(ord(maxanswer) - ord('a') + 1)]
            key = event.waitKeys(keyList=keyList)[0].lower()
            quiz_text.draw()
            if key == correct:
                images['quiz_correct'].draw()
                quiz_feedback.text = 'Correct!'
                answered.append(qn)
            else:
                images['quiz_incorrect'].draw()
                quiz_feedback.text = 'The correct answer is {}.'.format(correct)
            quiz_feedback.draw()
            win.flip()
            core.wait(3)
        if len(answered) == len(quiz):
            break

class Condition(object):
    abstract = 1
    story = 2

def run_tutorial(win, images, condition, instructions, results_base_filename):
    tutorial_mountain_sides = list(TutorialConfig.final_state_colors)
    random.shuffle(tutorial_mountain_sides)
    tutorial_model = Model.create_random(TutorialConfig)
    # Tutorial instructions
    string_replacements = get_string_replacements(
        TutorialConfig, tutorial_mountain_sides, tutorial_model, condition != Condition.abstract)
    if condition == Condition.abstract:
        instructions.display('abstract_tutorial_instructions.txt', string_replacements)
    else:
        instructions.display('tutorial_instructions.txt', string_replacements)

    if condition != Condition.abstract:
        run_quiz(win, join(ASSETS_DIR, 'quiz.py'), images, string_replacements)
        instructions.display('tutorial_flights_instructions.txt', string_replacements)

    # Tutorial flights
    if condition == Condition.abstract:
        tutorial_display = AbstractTutorialDisplay(win, images)
    else:
        tutorial_display = StoryTutorialDisplay(win, images, tutorial_mountain_sides)
    run_trial_sequence(
        win, TutorialConfig, tutorial_display, tutorial_model, results_base_filename)

def run_game_instructions(condition, game_model, instructions):
    game_mountain_sides = list(GameConfig.final_state_colors)
    random.shuffle(game_mountain_sides)
    # Game instructions
    string_replacements = get_string_replacements(
        GameConfig, game_mountain_sides, game_model, condition != Condition.abstract)
    if condition == Condition.abstract:
        instructions.display('abstract_game_instructions.txt', string_replacements)
    else:
        instructions.display('game_instructions.txt', string_replacements)
    return game_model

def run_game(win, images, condition, game_model, results_base_filename):
    # Create a text stimulus for the instructions reminder
    reminder_text = visual.TextStim(
        win=win,
        pos=(-500, +50),
        anchorHoriz='left',
        alignText='left',
        height=40,
        fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
        font='OpenSans',
        color=(0, 0, 0),
        wrapWidth=1000,
        name='Reminder text',
    )
    if condition == Condition.story:
        def fix_case(s):
            return s.capitalize()
    else:
        def fix_case(s):
            return s
    reminder_strings = {
        '[color_common1]': fix_case(game_model.colors[0]),
        '[color_common2]': fix_case(game_model.colors[1]),
    }
    with io.open(
            join(
                ASSETS_DIR,
                ('' if condition == Condition.story else 'abstract_') +\
                'instructions_reminder.txt'), encoding='utf-8') as inpf:
        reminder_text.text = replace_all(
            inpf.read(), reminder_strings)
    reminder_text.draw()
    win.flip()
    event.waitKeys(keyList=(LEFT_KEY + RIGHT_KEY))

    # Game flights
    if condition == Condition.abstract:
        rewards, win = run_trial_sequence(
            win, GameConfig, AbstractGameDisplay(win, images), game_model, results_base_filename)
    else:
        rewards, win = run_trial_sequence(
            win, GameConfig, StoryGameDisplay(win, images), game_model, results_base_filename)

    # Save payment information in a file
    payment_filename = '{}_{:.2f}'.format(results_base_filename, get_money_reward(RWRD, rewards))
    with open(payment_filename, 'w') as _:
        pass

    # Show payment
    # Create a center text stimulus for announcing the reward
    reward_text = visual.TextStim(
        win=win,
        pos=(0, 0),
        fontFiles=[join(ASSETS_DIR, 'OpenSans-SemiBold.ttf')],
        font='OpenSans',
        color=(0, 0, 0),
        units='height',
        height=0.09,
        name='Reward text',
    )
    money_msg = 'You won CHF {:.2f}.'.format(get_money_reward(RWRD, rewards))
    reward_text.text = money_msg
    reward_text.draw()
    win.logOnFlip(level=logging.EXP, msg='earned money displayed')
    win.flip()

def init_task(flnm_str):
    if not os.path.exists(RESULTS_DIR):
        os.mkdir(RESULTS_DIR)
    # Trying to find the participant ID automatically
    max_id = 0
    for flnm in os.listdir(RESULTS_DIR):
        if flnm.find(flnm_str) != -1:
            this_id = int(flnm.split('_')[0])
            if this_id > max_id:
                max_id = this_id
    settings = {
        'Participant ID': str(max_id + 1),
    }
    gui.DlgFromDict(settings, title='Experiment settings', sort_keys=False)
    if settings['Participant ID'].strip() == '':
        print('Please enter the participant ID')
        sys.exit(0)
    part_config = pd.read_csv(join(ASSETS_DIR, 'part_config.csv'))
    part_id = settings['Participant ID']
    try:
        part_id = int(part_id)
        assert part_id in part_config.participant.unique()
    except:
        print('Invalid participant ID')
        sys.exit(0)
    config = part_config[part_config.participant == part_id].iloc[0]
    condition = Condition.abstract if config.condition == 'abstract' else \
        Condition.story
    results_base_filename = join(RESULTS_DIR,
        '{}_{}_{}'.format(
            settings['Participant ID'].strip(), config.condition,
            data.getDateStr()))
    game_model = Model.load(GameConfig, config)
    return condition, game_model, results_base_filename
