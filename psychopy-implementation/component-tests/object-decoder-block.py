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
exp.init_progbar()

# Run Object Decoder block 
trial0 = {'trial_type': 'object_decoder',
         'input_disp': np.array([None, 'B', None, None]),
         'is_catch_trial': False,
         'correct_resp': None,
         'jitter': -0.027}

trial1 = {'trial_type': 'object_decoder',
         'input_disp': np.array(['A', None, None, None]),
         'is_catch_trial': True,
         'target': 'A',
         'correct_resp': True,
         'jitter': 0.027}
exp.objectDecoderTrial(trial0, fixation_duration=0.3 + trial0["jitter"],)
exp.objectDecoderTrial(trial1, fixation_duration=0.3 + trial1["jitter"],)

exp.win.close()
