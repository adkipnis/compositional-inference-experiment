#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 10:55:28 2022

@author: alex
"""

# from psychopy import core
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(screen = 1)
Exp.dialoguebox(show = False)
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar(bar_pos = [0, 15])
Exp.win.mouseVisible = False

# Run localizer task
Exp.LocalizerBlock(Exp.trials_localizer)
Exp.win.close()
