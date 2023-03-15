# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:58:02 2022

@author: external
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from psychopy import event, core
from ExperimentTools import Experiment

exp = Experiment()
exp.dialogue_box(show=False, participant=1, session=1, test_mode=True)
exp.init_window(screen=1, fullscr=False)

# Test
allKeys = event.waitKeys(maxWait = 10)
print(allKeys[0])
testRT, testResp = exp.tTestResponse(
    core.Clock(),
    exp.resp_keys #exp.resp_keys_vpixx
    )
print(testResp)
exp.win.close()
