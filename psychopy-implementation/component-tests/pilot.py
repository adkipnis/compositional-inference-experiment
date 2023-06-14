import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from ExperimentTools import Experiment

expOpts = {"show": False,
           "participant": 1,
           "session": 1,
           "meg": False,
           "test_mode": True}
winOpts = {"screen": 0,
           "fullscr": True}

# Initialize
exp = Experiment()
exp.dialogue_box(**expOpts)
exp.init_window(**winOpts)
exp.load_trials()
exp.render_visuals()

# Session 1
exp.Session1()
exp.win.close()

# Session 2
expOpts.update({"session": 2})
exp.dialogue_box(**expOpts)
exp.init_window(**winOpts)
exp.Session2()
exp.win.close()
