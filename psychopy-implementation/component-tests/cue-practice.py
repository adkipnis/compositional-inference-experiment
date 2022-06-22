#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 15:38:44 2022

@author: akipnis
"""

# from psychopy import core
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(screen = 0, fullscr = True)
Exp.dialoguebox(show = False, session = "1")
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar(bar_pos = [0, 15])
Exp.win.mouseVisible = False

# Run Cue Practice Session task
df_out = Exp.CuePracticeLoop(Exp.trials_prim_cue, "visual", "textual",
                             mode = "textual", i_step = 10)
Exp.win.close()
