# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:58:02 2022

@author: external
"""

# from psychopy import core
from ExperimentTools import Experiment
from psychopy import event

# Initialize
Exp = Experiment()
Exp.init_window(screen = 0)
Exp.init_interface()

# Test
allKeys = event.waitKeys(maxWait = 10)
print(allKeys)
Exp.win.close()
