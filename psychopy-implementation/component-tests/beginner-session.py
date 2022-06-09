#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  9 15:51:19 2022

@author: akipnis
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 12:23:50 2022

@author: akipnis
"""

# from psychopy import core
from ExperimentTools import Experiment

# Initialize
try: Exp.win.close()
except: True

Exp = Experiment()
Exp.init_window(screen = 0, fullscr = True)
Exp.dialoguebox(show = False, session = "1")
Exp.load_trials()
Exp.render_visuals()
Exp.init_progbar(bar_pos = [0, 15])
Exp.win.mouseVisible = False

# Run MEG Session task
Exp.Session1()
Exp.win.close()
