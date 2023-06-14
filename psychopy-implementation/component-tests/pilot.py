import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

# Initialize
exp = Experiment()
exp.dialogue_box(
    show=False,
    participant=1,
    session=1,
    meg=False,
    test_mode=False,
    )
exp.init_window(screen=0, fullscr=True)
exp.load_trials()
exp.render_visuals()

# Session 1
exp.Session1()
exp.win.close()

# Session 2
exp.init_window(screen=0, fullscr=True)
exp.session = 2
exp.Session2()
exp.win.close()
