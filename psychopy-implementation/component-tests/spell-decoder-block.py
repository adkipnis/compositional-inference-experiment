#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 11:18:02 2022

@author: akipnis
"""
import os, sys
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

# Initialize
exp = Experiment()
exp.dialogue_box(show=False, participant=1, session=1, test_mode=True, run_length=20)
exp.init_window(screen=1, fullscr=True)
exp.load_trials()
exp.render_visuals()

n_trials = 10
exp.init_progbar(milestones=[1.])
exp.progbar_inc = 1/n_trials

# Start decoder block
df_out = exp.adaptiveDecoderBlock(
    exp.trials_prim_dec[:n_trials],
    fixation_duration=0.3,
    pause_between_runs=True,
    decoderType="spell",
    test_goal=n_trials,
    )

# save output and quit
fname = exp.writeFileName("spellDecoder")
exp.save_object(df_out, fname, ending='csv')
exp.win.close()
