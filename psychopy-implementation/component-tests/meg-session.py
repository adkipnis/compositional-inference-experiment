#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 12:23:50 2022

@author: akipnis
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment
from psychopy import data
import numpy as np


# Initialize
exp = Experiment()
exp.dialogue_box(show=False, participant=1, session=2, test_mode=False)
exp.init_window(screen=0, fullscr=True)
exp.load_trials()
exp.render_visuals()
exp.init_progbar()

# Run Cue Practice Session task
def Session2(self):
    # init session variables
    self.win.mouseVisible = False
    goal_streak_d = 0 if self.test_mode else 16 # decoder
    goal_streak_p = 1 if self.test_mode else 20 # primitives
    goal_streak_b = 1 if self.test_mode else 15 # binaries
    n_trials = [self.n_primitives * goal_streak_d,
                self.n_primitives * goal_streak_p,
                self.n_primitives * goal_streak_b]
    n_total = sum(n_trials)
    milestones = np.cumsum(n_trials)/n_total
    self.init_progbar(milestones=milestones[:-1])
    self.progbar_inc = 1/n_total

    demoCount = data.TrialHandler(self.trials_prim_prac_c[:1], 1, method="sequential").trialList[0]
    demoPosition = data.TrialHandler(self.trials_prim_prac_p[:1], 1, method="sequential").trialList[0]
    demoBin = data.TrialHandler(self.trials_bin[:1], 1, method="sequential").trialList[0]

    ''' --- 1. Initial instructions and function decoder ------------------------'''
    # Navigation
    self.Instructions(part_key="Navigation3",
                        special_displays=[self.iSingleImage],
                        args=[self.keyboard_dict["keyBoardMegBF"] if self.meg else self.keyboard_dict["keyBoardArrows"]],
                        font="mono",
                        fontcolor=self.color_dict["mid_grey"])

    # if not self.test_mode:
    if not self.test_mode:
        # Introduction & Function Decoder
        self.Instructions(part_key="IntroMEG",
                        special_displays=[self.iSingleImage],
                        args=[self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]])
        self.df_out_5 = self.adaptiveDecoderBlock(self.trials_prim_dec)
        fname = self.writeFileName("functionDecoder")
        self.save_object(self.df_out_5, fname, ending='csv')
    else:
        self.move_prog_bar(end_width=milestones[0], n_steps=50, wait_s=0)

    ''' --- 2. Primitive trials ------------------------------------------------'''
    self.Instructions(part_key="PrimitivesMEGR",
                        special_displays=[self.iSingleImage,
                                        self.iSingleImage],
                        args=[self.magicWand,
                            self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]],
                        complex_displays=[self.tInput,
                                        self.drawCue,
                                        self.tCount,
                                        self.tPosition],
                        kwargs=[{"trial": demoCount, "duration": 0.0},
                                {"trial": demoCount, "duration": 0.0},
                                {"trial": demoCount, "duration": 0.0, "demonstration": True},
                                {"trial": demoPosition, "duration": 0.0, "demonstration": True}])
    
    self.df_out_6 = self.adaptiveBlock(self.trials_prim_MEG,
                                        streak_goal=goal_streak_p)
    fname = self.writeFileName("primitiveTrials")
    self.save_object(self.df_out_6, fname, ending='csv')
    
    ''' --- 3. Binary trials ------------------------------------------------'''
    self.Instructions(part_key="BinariesMEGR",
                        special_displays=[self.iSingleImage,
                                        self.iSingleImage],
                        args=[self.magicWand,
                            self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]],
                        complex_displays=[self.tInput,
                                        self.drawCue],
                        kwargs=[{"trial": demoBin, "duration": 0.0},
                                {"trial": demoBin, "duration": 0.0}])
    self.df_out_7 = self.adaptiveBlock(self.trials_bin_MEG,
                                        cue_duration=0.9, decrease=False,
                                        streak_goal=goal_streak_b)                          

    # Finalization
    fname = self.writeFileName("compositionalTrials")
    self.save_object(self.df_out_7, fname, ending='csv')
    self.move_prog_bar(end_width=1, n_steps=50, wait_s=0)
    self.Instructions(part_key="ByeBye")
    self.add2meta("t_end", data.getDateStr())
    self.win.close()
Session2(exp)
exp.win.close()