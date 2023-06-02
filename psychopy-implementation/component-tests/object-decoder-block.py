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
exp.dialogue_box(show=False, participant=1, session=1, test_mode=False)
exp.init_window(screen=1, fullscr=True)
exp.load_trials()
exp.render_visuals()

n_trials = 6
exp.init_progbar(milestones=[1.])
exp.progbar_inc = 1/n_trials

# Start decoder block
exp.adaptiveDecoderBlock(
    exp.trials_obj_dec[:n_trials],
    fixation_duration=0.3,
    pause_between_runs=True,
    decoderType="object",
    )

exp.win.close()
