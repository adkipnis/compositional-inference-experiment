#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 10:55:28 2022

@author: alex
"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

# Initialize
exp = Experiment()
exp.dialogue_box(show=False, participant=1, session=1, meg=False, test_mode=False)
exp.init_window(screen=1, fullscr=True)
exp.load_trials()
exp.render_visuals()
exp.init_progbar()

# Run localizer task
df_out = exp.adaptiveDecoderBlock(exp.trials_obj_dec[:2], decoderType="object")
fname = exp.writeFileName("objectDecoder")
exp.save_object(df_out, fname, ending='csv')
exp.win.close()
