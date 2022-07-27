#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 11:18:02 2022

@author: akipnis
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(screen = 1, fullscr = True)
Exp.dialoguebox(show = False, session = "1")
Exp.expInfo["session"] = "3"
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar(bar_pos = [0, 15])
Exp.win.mouseVisible = False

# Run Cue Practice Session task
Exp.start_width = 0
df_out = Exp.GenericBlock(Exp.trials_prim_dec,
                          mode = "random",
                          durations = [1.0, 3.0, 0.6, 1.0, 0.7],
                          self_paced = True,
                          pause_between_runs = True,
                          feedback = True,
                          runlength = 360,
                          resp_keys = Exp.resp_keys)
Exp.win.close()
