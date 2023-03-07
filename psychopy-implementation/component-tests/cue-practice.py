#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 15:38:44 2022

@author: akipnis
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

# Initialize
exp = Experiment()
exp.dialogue_box(show=False, participant=1, session=1, test_mode=False)
exp.init_window(screen=0, fullscr=True)
exp.load_trials()
exp.render_visuals()
exp.init_progbar()

# Run Cue Practice Session task
out = exp.adaptiveCuePractice(exp.trials_prim_cue, streak_goal=1, mode="visual")
exp.win.close()
