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

"""Runs the second-level GLM of the condition comparison analysis"""

from subprocess import run
import os
from os.path import join
import tempfile
import argparse
import importlib
from multiprocessing import Process
import pandas as pd
import first_level_condcomp as model

def run_contrast_analysis(parts, contrast, contrast_info, data_sink_dir, root_results_dir):
    with tempfile.TemporaryDirectory() as tempdir:
        design_con = join(tempdir, 'design.con')
        design_mat = join(tempdir, 'design.mat')
        with open(design_con + '.txt', 'w') as conf:
            conf.write('0\t1\t0\n')
            conf.write('0\t-1\t0\n')
            conf.write('1\t0\t0\n')
            conf.write('-1\t0\t0\n')
        run(['Text2Vest', design_con + '.txt', design_con])
        files = []
        with open(design_mat + '.txt', 'w') as matf:
            for part in parts.itertuples():
                condition = 2*int(part.condition == 'abstract') - 1
                matf.write(f'1\t{condition}\t{part.runs}\n')
                image_path = join(
                    data_sink_dir, f'participant_{part.participant}',
                    f'con_{contrast + 1:04d}.nii')
                assert os.path.exists(image_path)
                files.append(image_path)
        # Glue all images together for FSL :/
        merged = join(tempdir, 'merged.nii.gz')
        run(['fslmerge', '-t', merged] + files)
        # Images can't have NaNs
        run(['fslmaths', merged, '-nan', merged])
        run(['Text2Vest', design_mat + '.txt', design_mat])
        contrast_name = contrast_info[0].lower().replace(' ', '_').replace('(', '').replace(')', '')
        results_dir = join(root_results_dir, f'contrast_{contrast_name}_2ndlevel')
        if not os.path.exists(root_results_dir):
            os.mkdir(root_results_dir)
        if not os.path.exists(results_dir):
            os.mkdir(results_dir)
        cmd = [
            'randomise', '-i', merged, '-o', results_dir + '/', '-d',
            design_mat, '-t', design_con, '-x',
            '--uncorrp', '-v', '6', '-n', '5000', '-T']
        run(cmd)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_sink_dir")
    parser.add_argument("root_results_dir")
    args = parser.parse_args()
    parts = pd.read_csv('participants.csv')
    processes = []
    for contrast, contrast_info in enumerate(model.CONTRASTS):
        p = Process(
            target=run_contrast_analysis, args=(
                parts, contrast, contrast_info,
                args.data_sink_dir, args.root_results_dir))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

if __name__ == "__main__":
    main()
