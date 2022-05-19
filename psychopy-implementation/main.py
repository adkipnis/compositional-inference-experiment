#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run this file to launch the experiment
"""
# from psychopy import core
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(screen = 1)
Exp.dialoguebox()
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar(bar_pos = [0, 15])

# Start Experiment
try:
    if Exp.expInfo["session"] in ['1', '2', '3']:
        eval("Exp.Session" + Exp.expInfo["session"] + "()")
    else:
        raise ValueError('A session with this number does not exist')
except:
    pass
Exp.win.close()
