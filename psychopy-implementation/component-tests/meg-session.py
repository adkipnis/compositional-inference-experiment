#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 12:23:50 2022

@author: akipnis
"""

# from psychopy import core
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(screen = 1, fullscr = True, res = [2560, 1440])
Exp.dialoguebox(show = False, session = "3", dev = True)
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar(bar_pos = [0, 15])
Exp.win.mouseVisible = False

# Run MEG Session task
Exp.Session3()
Exp.win.close()
