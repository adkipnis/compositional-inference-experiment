# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:29:59 2022

@author: external
"""

# from psychopy import core
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_interface()

# Test
Exp.port_out.setData(0)
Exp.port_out.setData(8)
#Exp.port_out.readData()

# Start Trial: 1
# stimulus onset