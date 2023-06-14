#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run this file to launch the experiment
"""
from ExperimentTools import Experiment

# Initialize
exp = Experiment()
exp.dialogue_box(
    show=False,
    participant=1,
    session=1,
    meg=True,
    test_mode=False,
    )
exp.init_window(screen=0, fullscr=True)
exp.load_trials()
exp.render_visuals()

# Start experiment
s = exp.expInfo['session']
if s in [1, 2]:
    eval(f"exp.Session{s}()")
else:
    print('A session with this number does not exist.')
    exp.win.close()
