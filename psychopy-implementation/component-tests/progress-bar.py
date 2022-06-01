#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 11:03:16 2022

@author: alex
"""

# from psychopy import core
from ExperimentTools import Experiment
from psychopy import core

# Initialize
Exp = Experiment()
Exp.init_window(screen = 0)
Exp.dialoguebox(show = False)
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar(bar_pos = [0, 15])

# Prorgbar shenanigans
Exp.draw_background()
Exp.win.flip()
core.wait(2)
Exp.move_prog_bar()
core.wait(2)

# Finish
Exp.win.close()
