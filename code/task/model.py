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
import io
import pickle
from itertools import chain

class RewardProbability(float):
    "Reward probability that drifts within a min and a max value."
    MIN_VALUE = 0.25
    MAX_VALUE = 0.75
    DIFFUSION_RATE = 0.025
    def __new__(cls, value):
        assert value >= cls.MIN_VALUE and value <= cls.MAX_VALUE
        return super(RewardProbability, cls).__new__(cls, value)
    @classmethod
    def create_random(cls):
        "Create a random reward probability within the allowed interval."
        return cls(random.uniform(cls.MIN_VALUE, cls.MAX_VALUE))
    def diffuse(self):
        "Get the next probability by diffusion."
        return self.__class__(
            self.reflect_on_boundaries(random.gauss(0, self.DIFFUSION_RATE)))
    def get_reward(self):
        "Get a reward (0 or 1) with this probability."
        return int(random.random() < self)
    def reflect_on_boundaries(self, incr):
        "Reflect reward probability on boundaries."
        next_value = self + (incr % 1)
        if next_value > self.MAX_VALUE:
            next_value = 2*self.MAX_VALUE - next_value
        if next_value < self.MIN_VALUE:
            next_value = 2*self.MIN_VALUE - next_value
        return next_value

class Symbol(object):
    "A Tibetan symbol for a carpet or lamp."
    def __init__(self, code):
        self.code = code
    def __str__(self):
        return '{:02d}'.format(self.code)

class InitialSymbol(Symbol):
    "An initial state symbol."
    def __init__(self, code, final_state):
        super(InitialSymbol, self).__init__(code)
        self.final_state = final_state

class FinalSymbol(Symbol):
    "A final state symbol."
    def __init__(self, code, reward_probability):
        super(FinalSymbol, self).__init__(code)
        self.reward_probability = reward_probability
        self.reward = self.reward_probability.get_reward()

class State(object):
    "A initial state in the task."
    def __init__(self, symbols):
        assert len(symbols) == 2
        self.symbols = symbols

class FinalState(State):
    "A final state in the task."
    def __init__(self, color, symbols):
        self.color = color
        super(FinalState, self).__init__(symbols)

class Model(object):
    """A transition model and configuration of final states for the task."""
    def __init__(self, isymbol_codes, colors, fsymbol_codes):
        self.isymbol_codes = isymbol_codes
        self.colors = colors
        self.fsymbol_codes = fsymbol_codes
    @classmethod
    def create_random(cls, config):
        """Create a random model for the task from a given configuration."""
        colors = list(config.final_state_colors)
        random.shuffle(colors)
        fsymbol_codes = list(config.final_state_symbols)
        random.shuffle(fsymbol_codes)
        return cls(config.initial_state_symbols, colors, fsymbol_codes)
    def get_paths(self, common):
        "Generator for the paths from initial symbol to final symbols."
        if common:
            for isymbol_code, color, fsymbol_codes in zip(
                    self.isymbol_codes, self.colors, self.fsymbol_codes):
                yield (isymbol_code, color, fsymbol_codes)
        else:
            for isymbol_code, color, fsymbol_codes in zip(
                    self.isymbol_codes, reversed(self.colors), reversed(self.fsymbol_codes)):
                yield (isymbol_code, color, fsymbol_codes)
    def __str__(self):
        output = "Common transitions: "
        for isymbol_code, color, fsymbol_codes in self.get_paths(True):
            output += "{} -> {} -> {}; ".format(isymbol_code, color, fsymbol_codes)
        return output
    @classmethod
    def load(cls, exp_config, part_config):
        isymbol_codes = exp_config.initial_state_symbols
        colors = (part_config.transition1, part_config.transition2)
        fsymbol_codes = [
            (symbols // 10, symbols % 10)
            for symbols in [part_config['symbols_{}'.format(color)] for color in colors]
        ]
        return cls(isymbol_codes, colors, fsymbol_codes)

class Trial(object):
    "A trial in the task."
    def __init__(self, number, initial_state, common):
        self.number = number
        self.initial_state = initial_state
        self.common = common
    @classmethod
    def get_sequence(cls, config, model):
        "Get an infinite sequence of trials with this configuration."
        trials = 0
        reward_probabilities = {
            fsymbol_code: RewardProbability.create_random()
            for fsymbol_code in chain(*config.final_state_symbols)
        }
        while True:
            common = config.get_common(trials)
            isymbols = []
            for isymbol_code, color, fsymbol_codes in model.get_paths(common):
                fsymbols = [
                    FinalSymbol(fsymbol_code, reward_probabilities[fsymbol_code])
                    for fsymbol_code in fsymbol_codes
                ]
                random.shuffle(fsymbols)
                final_state = FinalState(color, tuple(fsymbols))
                isymbols.append(InitialSymbol(isymbol_code, final_state))
            random.shuffle(isymbols)
            initial_state = State(isymbols)
            yield cls(trials, initial_state, common)
            for fsymbol_code, prob in reward_probabilities.items():
                reward_probabilities[fsymbol_code] = prob.diffuse()
            trials += 1

def get_random_transition_model(config):
    isymbols = list(config.initial_state_symbols)
    fsymbols = list(config.final_state_symbols)
    colors = list(config.final_state_colors)
    random.shuffle(isymbols)
    random.shuffle(fsymbols)
    random.shuffle(colors)
    return {isymbols[i]: {'color': colors[i], 'symbols': fsymbols[i]} for i in range(2)}
