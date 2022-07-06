#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 11:18:02 2022

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

# Run Cue Practice Session task
Exp.start_width = 0
df_out = Exp.GenericBlock(Exp.trials_prim, mode = "random", i_step = 5,
                 self_paced = True, feedback = True)
Exp.win.close()
