#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 15:51:19 2022

@author: akipnis
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from psychopy import data
from ExperimentTools import Experiment
import numpy as np


# Initialize
exp = Experiment()
exp.dialogue_box(show=True, participant=1, session=1, test_mode=False)
exp.init_window(screen=0, fullscr=True)
exp.load_trials()
exp.render_visuals()
exp.init_progbar()

# Run Cue Practice Session task
def Session1(self):
    # init session variables
    self.win.mouseVisible = False
    streak_goal = 2 if self.test_mode else 10 # per map
    n_trials = [self.n_primitives * streak_goal//2, # cue practice
                self.n_primitives * streak_goal//2,
                self.n_primitives * streak_goal, # test practice
                self.n_primitives * streak_goal]
    n_total = sum(n_trials)
    milestones = np.cumsum(n_trials)/n_total
    self.init_progbar(milestones=milestones[:-1])
    self.progbar_inc = 1/n_total
    
    # Balance out which cue modality is learned first
    id_is_odd = int(self.expInfo["participant"]) % 2
    first_modality = "visual" if id_is_odd else "textual"
    second_modality = "textual" if id_is_odd else "visual"

    # Balance out which test type is learned first
    first_test = "count" if id_is_odd else "position"
    second_test = "position" if id_is_odd else "count"
    tFirst = self.tCount if id_is_odd else self.tPosition
    tSecond = self.tPosition if id_is_odd else self.tCount
    trials_test_1 = self.trials_prim_prac_c.copy() if id_is_odd else self.trials_prim_prac_p.copy()
    trials_test_2 = self.trials_prim_prac_p.copy() if id_is_odd else self.trials_prim_prac_c.copy()

    # Get Demo trials
    demoTrials1 = data.TrialHandler(trials_test_1[:1], 1, method="sequential")
    demoTrials2 = data.TrialHandler(trials_test_2[:1], 1, method="sequential")
    demoTrial1, demoTrial2 = demoTrials1.trialList[0], demoTrials2.trialList[0]
    print("Starting Session 1.")

    ''' --- 1. Initial instructions ---------------------------------------------'''
    # Navigation
    self.Instructions(part_key="Navigation1",
                        special_displays=[self.iSingleImage,
                                        self.iSingleImage],
                        args=[self.keyboard_dict["keyBoardArrows"],
                            self.keyboard_dict["keyBoardEsc"]],
                        font="mono",
                        fontcolor=self.color_dict["mid_grey"])

    # Introduction
    self.Instructions(part_key="Intro",
                        special_displays=[self.iSingleImage,
                                        self.iSingleImage,
                                        self.iSingleImage,
                                        self.iTransmutableObjects,
                                        self.iSpellExample,
                                        self.iSpellExample],
                        args=[self.magicWand,
                            self.magicBooks,
                            self.philbertine,
                            None,
                            [["A", "B", "C", "D"], ["A", "D", "C", "D"]],
                            [["A", "B", "B", "D"], ["A", "D", "D", "D"]]])

    ''' --- 2. Learn Cues --------------------------------------------------------'''
    # Learn first cue type
    self.learnDuration_1 = self.learnCues()
    self.add2meta("learnDuration_1", self.learnDuration_1)

    # Test first cue type
    self.Instructions(part_key="Intermezzo1",
                        special_displays=[self.iSingleImage,
                                        self.iSingleImage],
                        args=[self.keyboard_dict["keyBoard4"],
                            self.magicChart])
    self.df_out_1 = self.adaptiveCuePractice(self.trials_prim_cue,
                                                streak_goal=streak_goal//2,
                                                mode=first_modality)
    fname = self.writeFileName("cueMemory"+first_modality.capitalize())
    self.save_object(self.df_out_1, fname, ending='csv')

    # Learn second cue type
    self.Instructions(part_key="Intermezzo2",
                        special_displays=[self.iSingleImage],
                        args=[self.keyboard_dict["keyBoard4"]])
    self.learnDuration_2 = self.learnCues()
    self.add2meta("learnDuration_2", self.learnDuration_2)
    

    # Test second cue type
    self.df_out_2 = self.adaptiveCuePractice(self.trials_prim_cue[len(self.df_out_1):],
                                                streak_goal=streak_goal//2,
                                                mode=second_modality)
    fname = self.writeFileName("cueMemory"+second_modality.capitalize())
    self.save_object(self.df_out_2, fname, ending='csv')

    ''' --- 3. Test Types --------------------------------------------------------'''
    # First Test-Type
    self.Instructions(part_key="TestTypes",
                        special_displays=[self.iSingleImage],
                        args=[self.magicWand],
                        complex_displays=[self.genericTrial],
                        kwargs=[{"trial": demoTrial1,
                                "self_paced": False,
                                "skip_test": True}],                          
                        loading_time=0)
    self.Instructions(part_key=first_test + "First",
                        special_displays=[self.iSingleImage,
                                        self.iSingleImage],
                        args=[self.magicChart,
                            self.keyboard_dict["keyBoard4"]],
                        complex_displays=[self.tInput,
                                        self.drawCue,
                                        tFirst,
                                        tFirst],
                        kwargs=[{"trial": demoTrial1, "duration": 0.0},
                                {"trial": demoTrial1, "duration": 0.0},
                                {"trial": demoTrial1, "duration": 0.0, "demonstration": True},
                                {"trial": demoTrial1, "duration": 0.0, "demonstration": True, "feedback": True}])
    self.df_out_3 = self.adaptiveBlock(trials_test_1,
                                        streak_goal=streak_goal)
    fname = self.writeFileName("testPractice"+first_test.capitalize())
    self.save_object(self.df_out_3, fname, ending='csv')
    
    # Second Test-Type
    self.Instructions(part_key=second_test + "Second",
                        special_displays=[self.iSingleImage],
                        args=[self.keyboard_dict["keyBoard4"]],
                        complex_displays=[self.genericTrial,
                                        tSecond,
                                        tSecond],
                        kwargs=[{"trial": demoTrial2, "self_paced": False, "skip_test": True},
                                {"trial": demoTrial2, "duration": 0.0, "demonstration": True},
                                {"trial": demoTrial2, "duration": 0.0, "demonstration": True, "feedback": True}])
    self.df_out_4 = self.adaptiveBlock(trials_test_2,
                                        streak_goal=streak_goal)
    fname = self.writeFileName("testPractice"+second_test.capitalize())
    self.save_object(self.df_out_4, fname, ending='csv')

    # Wrap up
    self.move_prog_bar(end_width=1, n_steps=50, wait_s=0)
    self.Instructions(part_key="Bye")
    self.add2meta("t_end", data.getDateStr())
    self.win.close()
Session1(exp)
exp.win.close()
