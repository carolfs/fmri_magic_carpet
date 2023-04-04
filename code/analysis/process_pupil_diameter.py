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

"""Process the eye-tracking data to extract the pupil diameter"""

from os.path import join, basename, exists
from os import listdir
import sys
import pickle
import bz2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d, median_filter
from scipy.interpolate import interp1d
from config import CONDITIONS

EYE_TRACKER_DIR = join('..', '..', 'data', 'eye_tracking')
if not exists(EYE_TRACKER_DIR):
    print("Eye-tracking data not found", file=sys.stderr)
    sys.exit()
BLINK_SKIP = 100 # Skip some time (in ms) around each blink

def get_pupil_diameter(flnm):
    times = []
    pupdiams = []
    with bz2.open(flnm, "rt") as inpf:
        last_blink = -np.inf
        blinking = False
        for linenum, line in enumerate(inpf.readlines()):
            if line.startswith('SBLINK'):
                blinking = True
                # drop past info
                blink_time = int(line.split(' ')[-1])
                while times and (times[-1] >= blink_time - BLINK_SKIP):
                    times.pop()
                    pupdiams.pop()
            elif line.startswith('EBLINK'):
                last_blink = int(line.split('\t')[1])
                blinking = False
            elif line.startswith('END\t'):
                end_time = int(line.split('\t')[1])
            elif line.endswith('...\n'):
                pieces = line.split('\t')
                assert len(pieces) == 5
                time = int(pieces[0])
                pupdiam = float(pieces[3])
                if not blinking and time > last_blink + BLINK_SKIP:
                    times.append(time)
                    pupdiams.append(pupdiam)
            elif linenum == 11:
                start_time = int(line.split('\t')[1].split(' ')[0])
    duration = (end_time - start_time)/1000.
    return duration, (np.array(times) - start_time)/1000., np.array(pupdiams)

def get_all_pupil_diameter(flnm):
    times = []
    pupdiams = []
    with bz2.open(flnm, "rt") as inpf:
        for linenum, line in enumerate(inpf.readlines()):
            if line.startswith('END\t'):
                end_time = int(line.split('\t')[1])
            elif line.endswith('...\n'):
                pieces = line.split('\t')
                assert len(pieces) == 5
                time = int(pieces[0])
                pupdiam = float(pieces[3])
                if pupdiam < 1:
                    pupdiam = np.nan
                times.append(time)
                pupdiams.append(pupdiam)
            elif linenum == 11:
                start_time = int(line.split('\t')[1].split(' ')[0])
    duration = (end_time - start_time)/1000.
    return duration, (np.array(times) - start_time)/1000., np.array(pupdiams)

def get_participant_run(flnm):
    pieces = basename(flnm).split('_')
    part_num = int(pieces[0])
    assert part_num >= 1 and part_num <= 100
    run = int(pieces[-1][0])
    assert run >= 1 and run <= 3
    return part_num, run

def get_eye_tracker_files():
    return {get_participant_run(flnm): join(EYE_TRACKER_DIR, flnm)\
        for flnm in listdir(EYE_TRACKER_DIR) if flnm.endswith('.asc.bz2')}

def plot_pupil_diam():
    eye_tracker_files = get_eye_tracker_files()
    for part_num in range(1, 101):
        if (part_num, 1) not in eye_tracker_files.keys():
            continue
        plt.figure(figsize=(20, 3*3))
        for run in range(1, 4):
            try:
                flnm = eye_tracker_files[(part_num, run)]
            except KeyError:
                continue
            duration, times, pupdiams = get_pupil_diameter(flnm)
            plt.subplot(3, 1, run)
            plt.title(f'Run {run}')
            plt.ylabel('Pupil diameter')
            plt.xlabel('Time (s)')
            plt.plot(times, pupdiams, '.')
            plt.xlim(0, duration)
            plt.xlim(0, duration)
        plt.tight_layout()
        plt.savefig(join('pupil_diam_plots', f'part_{part_num:03d}_pupil_diam_zoom.png'))
        plt.close()

def get_condition(flnm):
    condition = basename(flnm).split('_')[1]
    assert condition in CONDITIONS
    return condition

def smooth(data):
    return gaussian_filter1d(median_filter(data, 50), 10)

def zscore(x):
    return (x - np.mean(x))/np.std(x)

def preprocess(times, pupdiams):
    # Break pupil information into pieces
    filtered_pupdiams = np.array([])
    prev_i = 0
    for i, t in enumerate(times[1:]):
        if t > times[i] + 0.004:
            filtered_pupdiams = np.concatenate((filtered_pupdiams, smooth(pupdiams[prev_i:i + 1])))
            prev_i = i + 1
    filtered_pupdiams = np.concatenate((filtered_pupdiams, smooth(pupdiams[prev_i:])))
    assert len(filtered_pupdiams) == len(pupdiams)
    return interp1d(times, filtered_pupdiams, kind=3)

def preprocess_pupil_diameter():
    if exists('preprocessed_pupil_diam.dat'):
        return
    eye_tracker_files = get_eye_tracker_files()
    onsets = pd.read_csv('onsets_durations.csv')
    onsets = onsets.dropna()
    with open('preprocessed_pupil_diam.dat', 'wb') as outf:
        for part in onsets.participant.unique():
            for run in onsets.run.unique():
                if part == 69 and run == 2: # This causes a segmentation fault for some reason
                    continue
                print(f'Processing participant {part}, run {run}...')
                try:
                    etfile = eye_tracker_files[(part, run)]
                except KeyError:
                    continue
                duration, times, pupdiams = get_pupil_diameter(etfile)
                if len(times)/(duration*500) < 0.8: # Too little data
                    print(f'Participant {part}, run {run} excluded...')
                    continue
                pupdiams = zscore(pupdiams)
                pupilf = preprocess(times, pupdiams)
                pickle.dump((part, run, pupilf), outf)

def get_feedback_mean_diam():
    onsets = pd.read_csv('onsets_durations.csv')
    onsets = onsets.dropna()
    feedback_interval = np.arange(0, 1.5, 0.002)
    with open('mean_feedback_pupdiam.csv', 'w') as outf, open('preprocessed_pupil_diam.dat', 'rb') as inpf:
        outf.write('participant,condition,trial,pupdiam\n')
        while True:
            try:
                (part, run, pupilf) = pickle.load(inpf)
            except:
                break
            print(f'Processing participant {part}, run {run}...')
            part_trials = onsets[(onsets.participant == part) & (onsets.run == run)]
            for trial in part_trials.itertuples():
                try:
                    mean_pupdiam = np.mean(pupilf(feedback_interval + trial.onset_feedback))
                except ValueError:
                    print(f'Error calculating mean pupil diameter at {trial.onset_feedback} of {part}.{run}...')
                else:
                    outf.write(f'{part},{trial.condition},{trial.trial},{mean_pupdiam}\n')

def get_first_stage_mean_diam():
    onsets = pd.read_csv('onsets_durations.csv')
    onsets = onsets.dropna()
    with open('mean_first_stage_pupdiam.csv', 'w') as outf, open('preprocessed_pupil_diam.dat', 'rb') as inpf:
        outf.write('participant,condition,trial,pupdiam\n')
        while True:
            try:
                (part, run, pupilf) = pickle.load(inpf)
            except:
                break
            print(f'Processing participant {part}, run {run}...')
            part_trials = onsets[(onsets.participant == part) & (onsets.run == run)]
            for trial in part_trials.itertuples():
                interval = np.arange(0, trial.duration_first_choice, 0.002)
                try:
                    mean_pupdiam = np.mean(pupilf(interval + trial.onset_first_choice))
                except ValueError:
                    print(f'Error calculating mean pupil diameter at {trial.onset_first_choice} of {part}.{run}...')
                else:
                    outf.write(f'{part},{trial.condition},{trial.trial},{mean_pupdiam}\n')

def get_interchoice_mean_diam():
    onsets = pd.read_csv('onsets_durations.csv')
    onsets = onsets.dropna()
    with open('mean_interchoice_pupdiam.csv', 'w') as outf, open('preprocessed_pupil_diam.dat', 'rb') as inpf:
        outf.write('participant,condition,trial,pupdiam\n')
        while True:
            try:
                (part, run, pupilf) = pickle.load(inpf)
            except:
                break
            print(f'Processing participant {part}, run {run}...')
            part_trials = onsets[(onsets.participant == part) & (onsets.run == run)]
            for trial in part_trials.itertuples():
                interval = np.arange(0, 4, 0.002)
                start = trial.onset_first_choice + trial.duration_first_choice
                try:
                    mean_pupdiam = np.mean(pupilf(interval + start))
                except ValueError:
                    print(f'Error calculating mean pupil diameter at {start} of {part}.{run}...')
                else:
                    outf.write(f'{part},{trial.condition},{trial.trial},{mean_pupdiam}\n')

def plot_feedback_pupil_diam():
    plt.figure(figsize=(6, 4))
    onsets = pd.read_csv('onsets_durations.csv')
    onsets = onsets.dropna()
    beh_results = pd.read_csv('beh_noslow.csv')
    onsets = pd.merge(onsets, beh_results, on=('participant', 'trial', 'condition'))
    plot_interval = np.arange(-2., 2., 0.002)
    for condition in CONDITIONS:
        cond_pupdiam = np.zeros(len(plot_interval))
        all_pupdiam = []
        last_part = 0
        num_parts = 0
        with open('preprocessed_pupil_diam.dat', 'rb') as inpf:
            while True:
                try:
                    (part, run, pupilf) = pickle.load(inpf)
                except:
                    num_parts += 1
                    cond_pupdiam += part_pupdiam/num_trials
                    all_pupdiam.append(part_pupdiam/num_trials)
                    break
                part_trials = onsets[(onsets.participant == part) & (onsets.run == run)]
                if part_trials.empty:
                    continue
                if part_trials.iloc[0].condition != condition:
                    continue
                if last_part != part:
                    if last_part > 0:
                        num_parts += 1
                        cond_pupdiam += part_pupdiam/num_trials
                        all_pupdiam.append(part_pupdiam/num_trials)
                    part_pupdiam = np.zeros(len(plot_interval))
                    num_trials = 0
                    last_part = part
                for trial in part_trials.itertuples():
                    try:
                        pupdiam = pupilf(plot_interval + trial.onset_feedback)
                    except ValueError:
                        print(f'Error calculating mean pupil diameter at {trial.onset_feedback} of {part}.{run}...')
                    else:
                        part_pupdiam += pupdiam
                        num_trials += 1
                        print(part, trial.condition, trial.trial, trial.reward, trial.common, np.mean(pupdiam), sep=',')
        cond_pupdiam /= num_parts
        mean_pupdiam = np.zeros(len(plot_interval))
        for pupd in all_pupdiam:
            mean_pupdiam += pupd
        mean_pupdiam /= num_parts
        assert len(all_pupdiam) == num_parts
        plt.plot(plot_interval, mean_pupdiam, '-', label=condition)
        ysup = []
        yinf = []
        for i, x in enumerate(mean_pupdiam):
            values = [pupd[i] for pupd in all_pupdiam]
            stderr = np.std(values) / np.sqrt(len(values))
            ysup.append(x + stderr)
            yinf.append(x - stderr)
        plt.fill_between(plot_interval, ysup, yinf, alpha=0.25)
        print(condition, num_parts, np.mean(cond_pupdiam))
    plt.xlabel('Time from feedback onset (s)')
    plt.ylabel('Pupil diameter z-score')
    plt.legend(loc='best')
    plt.savefig('mean_feedback_pupil_diameter.pdf')
    plt.close()

if __name__ == "__main__":
    preprocess_pupil_diameter()
    get_feedback_mean_diam()
    get_first_stage_mean_diam()
    get_interchoice_mean_diam()
    plot_feedback_pupil_diam()
