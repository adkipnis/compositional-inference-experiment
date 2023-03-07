#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 15:51:19 2022

@author: akipnis
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

exp = Experiment()
exp.dialogue_box(show=False, participant=1, session=1, test_mode=True)
exp.init_window(screen=0, fullscr=True)
exp.load_trials()
exp.render_visuals()
exp.init_progbar()
exp.Session1()
