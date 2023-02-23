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

"""Questionnaire for the magic carpet experiment: abstract versus story instructions."""

import sys
import os
import random
import io
from os.path import join
import wx
import wx.adv as wiz

WIDTH = 600

def setup_page(page, title):
    # font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
    # font.SetPointSize(14)
    vbox = wx.BoxSizer(wx.VERTICAL)
    page.SetSizer(vbox)
    overall_text = wx.StaticText(
        page,
        label=title)
    # overall_text.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
    vbox.Add(overall_text, 0, wx.LEFT|wx.RIGHT|wx.TOP, border=10)
    vbox.Add(wx.StaticLine(page, -1), 0, wx.EXPAND|wx.ALL, 5)
    return vbox, None

class SymbolsPage(wiz.WizardPageSimple):
    def __init__(self, parent, assets_dir, config):
        wiz.WizardPageSimple.__init__(self, parent)
        vbox, font = setup_page(self, 'About the game you played in the fMRI scanner')
        # Symbol 1
        text_symbol1 = wx.StaticText(
            self,
            label='When you selected the symbol below, which lamps did you usually get?')
        # text_symbol1.SetFont(font)
        vbox.Add(text_symbol1, 0, wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        symbol1_png = wx.Image(
            join(assets_dir, 'tibetan.{:02d}.png'.format(config.initial_state_symbols[0])),
            wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        s1bm = wx.StaticBitmap(
            self, bitmap=symbol1_png, size=(
                symbol1_png.GetWidth(), symbol1_png.GetHeight()))
        mountains = ['{} lamps'.format(color.capitalize()) \
            for color in config.final_state_colors]
        self.symbol1_color = [
            wx.RadioButton(self, label=label, style=(wx.RB_GROUP if i == 0 else 0))
            for i, label in enumerate(mountains)
        ]
        rb = wx.RadioButton(self, label='', style=0)
        rb.SetValue(True)
        rb.Show(False)
        s1_hbox = wx.BoxSizer(wx.HORIZONTAL)
        s1_hbox.Add(s1bm, 1, wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        s1_vbox = wx.BoxSizer(wx.VERTICAL)
        for button in self.symbol1_color:
            s1_vbox.Add(button, 1, wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        s1_hbox.Add(s1_vbox, 1, wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(s1_hbox, 0, wx.BOTTOM, border=20)
        # Symbol 2
        text_symbol2 = wx.StaticText(
            self,
            label='When you selected the symbol below, which lamps did you usually get?')
        # text_symbol2.SetFont(font)
        vbox.Add(text_symbol2, 0, wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        symbol2_png = wx.Image(
            join(assets_dir, 'tibetan.{:02d}.png'.format(config.initial_state_symbols[1])),
            wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        s2bm = wx.StaticBitmap(
            self, bitmap=symbol2_png, size=(
                symbol1_png.GetWidth(), symbol2_png.GetHeight()))
        self.symbol2_color = [
            wx.RadioButton(self, label=label, style=(wx.RB_GROUP if i == 0 else 0))
            for i, label in enumerate(mountains)
        ]
        rb = wx.RadioButton(self, label='', style=0)
        rb.SetValue(True)
        rb.Show(False)
        s2_hbox = wx.BoxSizer(wx.HORIZONTAL)
        s2_hbox.Add(s2bm, 1, wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        s2_vbox = wx.BoxSizer(wx.VERTICAL)
        for button in self.symbol2_color:
            s2_vbox.Add(button, 1, wx.TOP|wx.LEFT|wx.RIGHT, border=10)
        s2_hbox.Add(s2_vbox, 1, wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add(s2_hbox, 0, wx.BOTTOM, border=20)

class GameDifficultyPage(wiz.WizardPageSimple):
    def __init__(self, parent):
        wiz.WizardPageSimple.__init__(self, parent)
        vbox, font = setup_page(self, 'About the game you played in the fMRI scanner')
        questions = [
            (
                'understanding',
                'Please rate on a 0 to 4 scale how well you understood the game.',
                'not at all',
                'perfectly',
            ),
            (
                'complexity',
                'Please rate on a 0 to 4 scale how complex you thought the game was.',
                'not at all',
                'extremely',
            ),
            (
                'effort',
                'Please rate on a 0 to 4 scale how effortful playing the game was.',
                'not at all',
                'extremely',
            ),
        ]
        random.shuffle(questions)
        self.difficulty_buttons = {}
        for name, label, zerolabel, tenlabel in questions:
            text_hard = wx.StaticText(self, label=label)
            # text_hard.SetFont(font)
            vbox.Add(text_hard, 0, wx.LEFT|wx.RIGHT|wx.TOP, border=10)
            difficulty_labels = [str(i) for i in range(5)]
            difficulty_labels[0] += ': {}'.format(zerolabel)
            difficulty_labels[4] += ': {}'.format(tenlabel)
            self.difficulty_buttons[name] = [
                wx.RadioButton(self, label=label, style=(wx.RB_GROUP if i == 0 else 0))
                for i, label in enumerate(difficulty_labels)
            ]
            diff_box = wx.BoxSizer(wx.HORIZONTAL)
            for button in self.difficulty_buttons[name]:
                diff_box.Add(button, 1, wx.TOP|wx.LEFT|wx.RIGHT, border=10)
            rb = wx.RadioButton(self, label='', style=0)
            rb.SetValue(True)
            rb.Show(False)
            vbox.Add(diff_box, 0, wx.BOTTOM, border=20)

class StrategyPage(wiz.WizardPageSimple):
    def __init__(self, parent):
        wiz.WizardPageSimple.__init__(self, parent)
        vbox, font = setup_page(self, 'About the game you played in the fMRI scanner')
        question = wx.StaticText(
            self,
            label='Please describe in detail the strategy you used to make your choices in the game.')
        # question.SetFont(font)
        vbox.Add(question, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        self.answer = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        # self.answer.SetFont(font)
        vbox.Add(self.answer, 10, wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

def add_multiple_choice(page, font, vbox, question, responses):
    question_text = wx.StaticText(page, label=question)
    # question_text.SetFont(font)
    vbox.Add(question_text, 0, wx.LEFT|wx.RIGHT|wx.TOP, border=10)
    buttons = [
        wx.RadioButton(page, label=label, style=(wx.RB_GROUP if i == 0 else 0))
        for i, label in enumerate(responses)
    ]
    rb = wx.RadioButton(page, label='', style=0)
    rb.SetValue(True)
    rb.Show(False)
    resp_box = wx.BoxSizer(wx.VERTICAL)
    for button in buttons:
        resp_box.Add(button, 0)
    vbox.Add(resp_box, 0, wx.TOP|wx.BOTTOM|wx.LEFT, border=10)

class FoodChoicePage1(wiz.WizardPageSimple):
    def __init__(self, parent):
        wiz.WizardPageSimple.__init__(self, parent)
        vbox, font = setup_page(self, 'About the food choice task')
        add_multiple_choice(
            self,
            font,
            vbox,
            'What colour represents a health rating?',
            ('Green', 'Orange', 'I don’t remember'),
        )
        add_multiple_choice(
            self,
            font,
            vbox,
            'What colour represents a taste rating?',
            ('Green', 'Orange', 'I don’t remember'),
        )
        add_multiple_choice(
            self,
            font,
            vbox,
            'Where on the screen are the health ratings of the food items located '\
            'if they are shown during decision trials?',
            ('Upper half of the screen', 'Randomly assigned each trial', 'Lower half of the screen'),
        )
        add_multiple_choice(
            self,
            font,
            vbox,
            'Where on the screen are the taste ratings of the food items located '\
            'if they are shown during decision trials?',
            ('Upper half of the screen', 'Randomly assigned each trial', 'Lower half of the screen'),
        )

class FoodChoicePage2(wiz.WizardPageSimple):
    def __init__(self, parent):
        wiz.WizardPageSimple.__init__(self, parent)
        vbox, font = setup_page(self, 'About the food choice task')
        add_multiple_choice(
            self,
            font,
            vbox,
            'Concerning my food choices…',
            (
                'I only ever chose the healthier items',
                'I tried to keep to the health goal most of the time, but '\
                'sometimes chose a better tasting, less healthy food',
                'I did not try to keep the health goal at all'
            ),
        )
        questions = (
            'How difficult did you find the food ratings task?',
            'How difficult did you find the food choice task?',
        )
        responses = ('easy', 'not easy but not very difficult', 'difficult: because ')
        for question in questions:
            question_text = wx.StaticText(self, label=question)
            # question_text.SetFont(font)
    
            vbox.Add(question_text, 0, wx.LEFT|wx.RIGHT|wx.TOP, border=10)
            buttons = [
                wx.RadioButton(self, label=label, style=(wx.RB_GROUP if i == 0 else 0))
                for i, label in enumerate(responses)
            ]
            rb = wx.RadioButton(self, label='', style=0)
            rb.SetValue(True)
            rb.Show(False)
            resp_box = wx.BoxSizer(wx.VERTICAL)
            for button in buttons[:-1]:
                resp_box.Add(button, 0)
            hor_box = wx.BoxSizer(wx.HORIZONTAL)
            hor_box.Add(buttons[-1], 0)
            reason_textbox = wx.TextCtrl(self, 1, size=(200, 22))
            hor_box.Add(reason_textbox, 0)
            resp_box.Add(hor_box, 0)
            vbox.Add(resp_box, 0, wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT, border=10)

class FeedbackPage(wiz.WizardPageSimple):
    def __init__(self, parent):
        wiz.WizardPageSimple.__init__(self, parent)
        vbox, font = setup_page(self, 'About the whole experiment')
        question = wx.StaticText(
            self,
            label='Do you have any other feedback/issue/concern you would like to tell us about?')
        # question.SetFont(font)
        vbox.Add(question, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        self.answer = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        # self.answer.SetFont(font)
        vbox.Add(self.answer, 10, wx.EXPAND|wx.LEFT|wx.RIGHT, border=10)

class ThankYouPage(wiz.WizardPageSimple):
    def __init__(self, parent):
        wiz.WizardPageSimple.__init__(self, parent)
        vbox, font = setup_page(self, 'About the whole experiment')
        text = wx.StaticText(
            self,
            label='Thank you for participating in this experiment! Please make sure '\
                'you completed the questionnaire,\nthen submit it below.',
        )
        # text.SetFont(font)
        vbox.Add(text, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)


def main():
    from run import init_task
    from config import GameConfig, ASSETS_DIR

    _, game_model, results_base_filename = init_task('questionnaire')
    answers_filename = '{}_questionnaire.txt'.format(results_base_filename)
    app = wx.App(False)
    wizard = wx.adv.Wizard(None, -1, "Questionnaire", style=wx.CAPTION)
    wizard.SetPageSize((600, 400))
    cancel_btn = wizard.FindWindowById(wx.ID_CANCEL)
    cancel_btn.Disable()
    pages = []
    pages.append(SymbolsPage(wizard, ASSETS_DIR, GameConfig))
    pages.append(GameDifficultyPage(wizard))
    pages.append(StrategyPage(wizard))
    pages.append(FoodChoicePage1(wizard))
    pages.append(FoodChoicePage2(wizard))
    pages.append(FeedbackPage(wizard))
    pages.append(ThankYouPage(wizard))

    for prev_page, next_page in zip(pages[:-1], pages[1:]):
        wx.adv.WizardPageSimple.Chain(prev_page, next_page)
    wizard.FitToPage(pages[0])

    wizard.RunWizard(pages[0])

    wizard.Destroy()
    common_transitions = [None]*len(GameConfig.initial_state_symbols)
    for isymbol_code, color, _ in game_model.get_paths(common=True):
        common_transitions[GameConfig.initial_state_symbols.index(isymbol_code)] = color
    common_transitions.reverse()

    with io.open(answers_filename, 'w', encoding='utf-8') as outf:
        for page in pages:
            for child in page.GetChildren():
                if isinstance(child, wx._core.StaticText):
                    outf.write(child.GetLabelText() + '\n')
                elif isinstance(child, wx._core.StaticLine):
                    outf.write(child.GetLabelText() + '\n')
                elif isinstance(child, wx._core.StaticBitmap):
                    outf.write('Correct answer: ' + common_transitions.pop() + '\n')
                elif isinstance(child, wx._core.RadioButton):
                    if child.GetValue():
                        outf.write(child.GetLabelText() + '\n')
                elif isinstance(child, wx._core.TextCtrl):
                    text = child.GetValue().strip()
                    if text:
                        outf.write('-------\n' + text + '\n-------\n')
                else:
                    raise Exception("Unrecognized form control")
            outf.write('\n\n')
    app.MainLoop()


if __name__ == '__main__':
    main()
