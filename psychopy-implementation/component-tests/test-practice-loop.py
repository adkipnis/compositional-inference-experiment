#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 14:31:39 2022

@author: alex
"""
# from psychopy import core
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(res = [1900, 1080], screen = 1, fullscr = False)
Exp.dialoguebox(show = False, session = "1")
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar(bar_pos = [0, 15])
Exp.win.mouseVisible = False
Exp.start_width = 0
Exp.progbar_inc = 1/2

# Run test practice loop
df_out_3 = Exp.TestPracticeLoop(
    Exp.trials_prim_prac_c,
    min_acc = 0.95,
    self_paced = True,
    feedback = True,
    pause_between_runs = True,
    runlength = 10)
Exp.win.close()
