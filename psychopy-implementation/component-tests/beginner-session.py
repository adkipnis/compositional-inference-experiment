#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 15:51:19 2022

@author: akipnis
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(res = [1900, 1080], screen = 1, fullscr = False)
Exp.dialoguebox(show = False, session = "1")
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar(bar_pos = [0, 15])
Exp.win.mouseVisible = False

# Run MEG Session task
Exp.Session1()
Exp.win.close()
