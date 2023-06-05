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
exp = Experiment()
exp.dialogue_box(show=False, participant=1, session=1, meg=True, test_mode=False)
exp.init_window(screen=0, fullscr=True)
exp.load_trials()
exp.render_visuals()
exp.init_progbar()

# Run Cue Practice Session task
out = exp.adaptiveBlock(exp.trials_prim_prac_c, streak_goal=1)
exp.win.close()
