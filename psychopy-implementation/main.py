#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run this file to launch the experiment
"""
from ExperimentTools import Experiment

# Initialize
exp = Experiment()
exp.dialogue_box(show=True, participant='', session=1, test_mode=False)
exp.init_window(screen=1, fullscr=True)
exp.load_trials()
exp.render_visuals()

# Start experiment
if exp.expInfo['session'] in [1, 2]:
    eval(f"exp.Session{exp.expInfo['session']}()")
else:
    raise ValueError('A session with this number does not exist')
    exp.win.close()
