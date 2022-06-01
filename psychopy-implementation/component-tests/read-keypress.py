# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:58:02 2022

@author: external
"""

# from psychopy import core
from ExperimentTools import Experiment
from psychopy import event, core

# Initialize
Exp = Experiment()
Exp.init_window(screen = 1)
# Exp.init_interface()

# Test
allKeys = event.waitKeys(maxWait = 10)
print(allKeys[0])
testRT, testResp = Exp.tTestresponse(
    core.Clock(), Exp.resp_keys_vpixx)
print(testResp)
Exp.win.close()
