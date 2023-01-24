#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 27 11:03:16 2022

@author: alex
"""

from psychopy import core
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

# Initialize
Exp = Experiment()
Exp.init_window(screen=1)
Exp.init_progbar()


# Progbar shenanigans
Exp.draw_background()
Exp.win.flip()
core.wait(2)
Exp.move_prog_bar(end_width=Exp.start_width + 5*Exp.progbar_inc, wait_s=0)
core.wait(2)
Exp.move_prog_bar(end_width=0, wait_s=0)
core.wait(2)


# Finish
Exp.win.close()
