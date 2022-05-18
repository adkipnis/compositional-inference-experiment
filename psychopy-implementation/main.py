#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run this file to launch the experiment
"""
from psychopy import core
from ExperimentTools import Experiment

Exp = Experiment()
Exp.init_window(screen = 1)
Exp.dialoguebox()
Exp.load_trials()
Exp.render_visuals()
# Exp.init_progbar()
# Exp.move_prog_bar()
Exp.Session1()
Exp.win.close()
