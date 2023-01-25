import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment
from psychopy import visual, core

# Initialize
Exp = Experiment()
Exp.init_window([1920, 1080], screen=1, fullscr=False)
Exp.dialogue_box(show=False, participant=1)
Exp.load_trials()
Exp.render_visuals()

for key in Exp.keyboard_dict:
    Exp.keyboard_dict[key].draw()
    Exp.win.flip()
    core.wait(2)