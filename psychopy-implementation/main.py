#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run this file to launch the experiment
"""
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(screen=1, fullscr=False)
Exp.dialogue_box(show=True, participant=1)
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar()

# Start Experiment
if Exp.expInfo["session"] in ['1', '2']:
    eval(f"Exp.Session{Exp.expInfo['session']}()")
else:
    raise ValueError('A session with this number does not exist')

Exp.win.close()
