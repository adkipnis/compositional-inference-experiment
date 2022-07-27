#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 14:31:39 2022

@author: alex
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(screen = 1, fullscr = True)
Exp.dialoguebox(show = False, session = "1")
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar(bar_pos = [0, 15])
Exp.win.mouseVisible = False
Exp.start_width = 0
Exp.progbar_inc = 1/2

# Run test practice loop
df_out_3 = Exp.TestPracticeLoop(
    Exp.trials_prim,
    durations = [2.0, 3.0, 0.6, 1.0, 0.7],
    min_acc = 0.95,
    self_paced = True,
    feedback = True,
    pause_between_runs = True,
    runlength = 10)
Exp.win.close()
