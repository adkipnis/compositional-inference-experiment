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
Exp.init_window(screen = 1, fullscr = True)
Exp.dialoguebox(show = False, session = "1")
Exp.load_trials()
Exp.render_visuals(check_similarity = True)
Exp.init_progbar(bar_pos = [0, 15])

# Run MEG Session task
Exp.Session1(check_similarity = True)
Exp.win.close()
