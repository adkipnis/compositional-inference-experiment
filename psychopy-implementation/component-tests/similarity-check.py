#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 17:23:14 2022

@author: akipnis
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(screen = 1, fullscr = True)
Exp.dialoguebox(show = False)
Exp.load_trials()
Exp.render_visuals(check_similarity = True)
Exp.init_progbar(bar_pos = [0, 15])
Exp.win.mouseVisible = True

# Run similarity rating task
trial_list_1 = Exp.CueSimilarityTest(
    Exp.vcue_full,
    pos_1 = [-5, Exp.center_pos[1]],
    pos_2 = [5, Exp.center_pos[1]]) 

trial_list2 = Exp.CueSimilarityTest(
    Exp.tcue_full,
    pos_1 = [sum(x) for x in zip(Exp.center_pos, [0, 6])],
    pos_2 = [sum(x) for x in zip(Exp.center_pos, [0, 0])])

Exp.win.close()
