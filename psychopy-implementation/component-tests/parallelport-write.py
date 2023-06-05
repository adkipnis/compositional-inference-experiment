# -*- coding: utf-8 -*-
"""
Created on Fri May 27 15:29:59 2022

@author: external
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

# Initialize
exp = Experiment()
exp.init_interface()

# Test setData
exp.port_out.setData(0)
exp.port_out.setData(8)

# Test send trigger
exp.send_trigger("trial")
r = exp.port_out.readData()
print(r==1)


# Test methods that use this as a subroutine
# init session
exp.dialogue_box(show=False, participant=1, session=1, meg=True)
exp.init_window(screen=0, fullscr=True)
exp.load_trials()
exp.render_visuals()

# actual test
exp.drawFixation()
r = exp.port_out.readData()
print(r==2)

exp.win.close()