from ExperimentTools import Experiment
from psychopy import visual
# import os, glob

# Initialize
Exp = Experiment()
Exp.init_window(screen=1, fullscr=False)
Exp.dialogue_box(show=False, participant=1)
Exp.load_trials()
Exp.render_visuals()

stim = Exp.leftArrow
stim.draw()
Exp.win.flip()