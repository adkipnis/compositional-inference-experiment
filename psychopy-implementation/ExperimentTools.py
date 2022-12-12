#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Methods for running the compositional inference experiment
"""
import os
import glob
import pickle
import sys
import csv
from string import ascii_uppercase
import numpy as np
from psychopy import __version__, core, event, visual, gui, data
from psychopy.parallel import ParallelPort


# =============================================================================
# Experiment Class
# =============================================================================
class Experiment:
    def __init__(self, main_dir=None):
        # root directory of experiment
        if main_dir is not None:
            self.main_dir = main_dir
        else:
            self.main_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.main_dir)

        # directory for trial lists, stimuli and instructions
        self.trial_list_dir = os.path.join(self.main_dir, "trial-lists")
        if not os.path.exists(self.trial_list_dir):
            import GenerateTrialLists
        self.stim_dir = os.path.join(self.main_dir, "stimuli")
        sys.path.insert(0, './stimuli')
        import Instructions_EN

        # data dir
        self.data_dir = os.path.join(self.main_dir, "data")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # inputs and dimensions #TODO
        self.resp_keys = np.array(["s", "d", "num_4", "num_5"])
        self.resp_keys_wide = np.array(
            ["a", "s", "d", "num_4", "num_5", "num_6"])
        self.resp_keys_alt = np.array(
            ["s", "d", "j", "k", "left", "right"])
        self.resp_keys_vpixx = np.array(
            ["2", "1", "up", "left", "4", "right"])
        # Buttons: lMiddlefinger, lIndex, rIndex, rMiddlefinger, lThumb, rThumb
        # Mapping: 0, 1, 2, 3, False, True
        self.center_pos = [0, 5]
        self.center_size = [8, 8]
        self.vcue_size = [7, 7]
        self.normal_size = [5, 5]
        self.color_dict = {"light_grey": [0.7, 0.7, 0.7],
                           "mid_grey": [0.0, 0.0, 0.0],
                           "dark_grey": [-0.6, -0.6, -0.6],
                           "black": [-0.9, -0.9, -0.9],
                           "red": [0.8, 0.0, 0.0],
                           "green": [0.0, 0.6, 0.0],
                           "blue": [0.2, 0.6, 1.0]
                           }

    def init_window(self, res=None, screen=0, fullscr=False):
        ''' Initialize window '''
        if res is None:
            res = [1920, 1080]
        assert isinstance(res, list), "res must be list of two integers"
        self.win = visual.Window(
            res,
            fullscr=fullscr,
            color=[0.85, 0.85, 0.85],
            screen=screen,
            monitor="testMonitor",
            units="deg")

    def dialogue_box(self, participant=None, session="1", show=True, dev=False):
        ''' Show dialogue box to get participant info '''
        if participant is None:
            savefiles = glob.glob(f"{self.data_dir}{os.sep}*.txt")
            names = [0] + [int(os.path.basename(file)[:2])
                           for file in savefiles]
            participant = max(names)+1

        expName = "Alteration Magic Experiment"
        expInfo = {"participant": str(participant).zfill(2),
                   "session": session,
                   "dateStr": data.getDateStr(),
                   "psychopyVersion": __version__,
                   "frameRate": self.win.getActualFrameRate()}

        # Dialogue Box
        if show:
            dlg = gui.DlgFromDict(dictionary=expInfo,
                                  sortKeys=False,
                                  title=expName,
                                  fixed=["dateStr", "psychopyVersion", "frameRate"])
            if not dlg.OK:
                core.quit()

        # Save data to this file later
        self.file_name = f"{self.data_dir}{os.sep}{expInfo['participant']}_{expName}"
        with open(f"{self.file_name}.txt", 'a') as f:
            f.write(f"t0 = {expInfo['dateStr']}\n")
            f.write(f"session = {expInfo['session']}\n")
        self.expInfo = expInfo
        self.exp_clock = core.Clock()

        # Optionally init parallel port
        if not dev and expInfo["session"] == "3":
            self.init_interface()
            self.use_pp = True
        else:
            self.use_pp = False

    def init_interface(self):
        ''' Initialize parallel port for sending MEG triggers '''
        # set pp to base state
        self.port_out2 = ParallelPort(address="0xd112")
        self.port_out2.setData(8)

        # for sending triggers
        self.port_out = ParallelPort(address="0xd110")
        self.port_out.setData(0)

        # Trigger codes
        self.trigger_dict = {"trial": 1,
                             "fixate": 2,
                             "disp": 3,
                             "vcue": 40,
                             "tcue": 41,
                             "position": 50,
                             "count": 51,
                             "identity": 52,
                             "run": 6}

    def send_trigger(self, trigger_type):
        self.port_out.setData(self.trigger_dict[trigger_type])
        self.port_out.setData(0)

    def load_trials(self):
        print("Loading trials...")
        pid = self.expInfo["participant"]

        # Instructions
        self.instructions = pickle.load(
            open(f"{self.stim_dir}{os.sep}instructions_en.pkl", "rb"))

        #  Localizer trials
        self.trials_localizer = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_localizer.pkl", "rb"))

        self.trials_prim_dec = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim_dec.pkl", "rb"))

        #  Practice trials
        self.trials_prim_cue = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim_cue.pkl", "rb"))

        self.trials_prim_prac_c = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim_prac_c.pkl", "rb"))

        self.trials_prim_prac_p = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim_prac_p.pkl", "rb"))

        # Main trials # TODO make this dependent on session
        self.trials_prim = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim.pkl", "rb"))

        self.trials_bin = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_bin.pkl", "rb"))

        # MEG trials
        self.trials_prim_MEG = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim_MEG.pkl", "rb"))

        self.trials_bin_MEG = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_bin_MEG.pkl", "rb"))

        # Individual mappings for each participant
        self.mappinglists = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_mappinglists.pkl", "rb"))
        self.item_names = [name[2:] for name in self.mappinglists["stim"]]

        # convert mappinglists to file links
        self.mappinglists["stim"] = [f"{self.stim_dir}{os.sep}{name}.png"
                                     for name in self.mappinglists["stim"]]
        self.mappinglists["vcue"] = [f"{self.stim_dir}{os.sep}{name}.png"
                                     for name in self.mappinglists["vcue"]]

        self.set_size = len(self.trials_prim[0]["input_disp"])
        self.n_cats = len(np.unique([trial["input_disp"]
                                     for trial in self.trials_prim]))
        self.n_resp = len(self.trials_prim[0]["resp_options"])
        self.map_names = np.unique([trial["map"]
                                    for trial in self.trials_prim])
        self.n_primitives = len(self.map_names)
        self.n_exposure = 5  # this value should match in GenerateTrialLists
        self.maxn_blocks = 6  # this too

        # Determine_positions
        self.rect_pos = circularGridPositions(
            center_pos=self.center_pos, set_size=self.set_size, radius=7)
        self.resp_pos = rectangularGrindPositions(
            center_pos=[0, -10], h_dist=10, dim=(1, 4))
        self.cuepractice_pos = rectangularGrindPositions(
            center_pos=[0, -8], h_dist=8, dim=(1, self.n_cats))

    def render_visuals(self, check_similarity=False):
        print("Rendering unique visual objects...")

        self.instruct_stim = visual.TextStim(
            self.win,
            text='',
            height=1.8,
            wrapWidth=40)

        self.rect = visual.Rect(
            win=self.win,
            units="deg",
            width=6,
            height=6,
            fillColor=self.color_dict["light_grey"],
            lineColor=self.color_dict["dark_grey"])

        self.fixation = visual.GratingStim(
            self.win, color=-0.9,
            colorSpace="rgb",
            pos=self.center_pos,
            mask="circle",
            size=0.2)

        self.qm = visual.TextStim(self.win,
                                  text="?",
                                  height=4,
                                  color=self.color_dict["black"])

        self.nextPrompt = visual.TextStim(
            self.win,
            text="Navigate 'left' if you are not finished,\notherwise navigate 'right' to continue.",
            height=1.5,
            wrapWidth=40,
            font="mono",
            color=self.color_dict["mid_grey"])

        self.leftArrow = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}leftArrow.png")[0],
            size=self.normal_size, interpolate=True)

        self.magicWand = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}magicWand.png")[0],
            size=self.normal_size, interpolate=True)

        self.pauseClock = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}pauseClock.png")[0],
            pos=self.center_pos,
            size=self.center_size,
            interpolate=True)

        self.pauseText = visual.TextStim(
            self.win,
            text="Short Break.\nContinue?",
            height=1.8,
            pos=[0, -1],
            wrapWidth=30,
            font="Times New Roman",
            color=[-0.9, -0.9, -0.9])

        self.philbertine = visual.ImageStim(
            self.win, image=glob.glob(
                f"{self.stim_dir}{os.sep}philbertine.png")[0],
            units="pix",
            size=[512, 512], interpolate=True)

        self.magicBooks = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}magicBooks.png")[0],
            units="pix",
            size=[512, 512], interpolate=True)

        # Count responses
        self.count_dict = {
            str(i): visual.TextStim(
                self.win,
                text=str(i),
                height=4,
                color=self.color_dict["black"])
            for i in range(self.n_resp)
        }

        # Keyboard prompts
        keyboard_list = glob.glob(f"{self.stim_dir}{os.sep}keyBoard*.png")
        self.keyboard_dict = {
            os.path.basename(os.path.normpath(keyboard_list[i])).split(".")[0]: visual.ImageStim(
                self.win,
                image=keyboard_list[i],
                size=[40, 20],
                interpolate=True)
            for i in range(len(keyboard_list))
        }

        print("Rendering cues...")
        # Text cues
        tcue_list = self.mappinglists["tcue"]
        assert len(tcue_list) >= 2*self.n_primitives
        vcue_list = self.mappinglists["vcue"]
        assert len(vcue_list) >= 2*self.n_primitives

        # use latter half of cues for MEG-Session
        if self.expInfo["session"] == "3":
            tcue_list = np.concatenate((tcue_list[self.n_primitives:],
                                        tcue_list[:self.n_primitives]))
            vcue_list = np.concatenate((vcue_list[self.n_primitives:],
                                        vcue_list[:self.n_primitives]))

        self.tcue_dict = {
            self.map_names[i]: visual.TextStim(
                self.win,
                text=tcue_list[i],
                pos=self.center_pos,
                height=4,
                color=self.color_dict["black"])
            for i in range(self.n_primitives)
        }

        self.vcue_dict = {
            self.map_names[i]: visual.ImageStim(
                self.win,
                image=vcue_list[i],
                pos=self.center_pos,
                size=self.vcue_size,
                interpolate=True)
            for i in range(self.n_primitives)
        }

        print("Rendering stimuli...")
        # Stimuli
        stim_list = self.mappinglists["stim"]
        assert len(stim_list) >= 2*self.n_cats, "Not enough stimuli"
        stim_names = ascii_uppercase[0:len(stim_list)]
        if self.expInfo["session"] == "3":
            stim_names = stim_names[self.n_cats:] + stim_names[:self.n_cats]
        self.stim_dict = {
            stim_names[i]: visual.ImageStim(
                self.win,
                image=stim_list[i],
                size=self.normal_size,
                interpolate=True)
            for i in range(len(stim_list))
        }

        if check_similarity:
            print("Rendering stimuli for similarity check...")
            self.ratingScale = visual.RatingScale(
                self.win,
                low=0, high=10,
                pos=[0.0, -0.2],
                marker="slider",
                markerStart=None,
                lineColor="white",
                labels=["0: very similar", "10: very different"],
                stretch=1.25,
                textSize=0.75,
                textFont="mono",
                mouseOnly=False,
                acceptKeys='space',
                scale=None)

            self.tcue_full = {
                tcue_list[i]: visual.TextStim(
                    self.win,
                    text=tcue_list[i],
                    pos=self.center_pos,
                    height=4,
                    color=self.color_dict["black"])
                for i in range(len(tcue_list))
            }

            self.vcue_full = {
                vcue_list[i][-5]: visual.ImageStim(
                    self.win,
                    image=vcue_list[i],
                    pos=self.center_pos,
                    size=self.vcue_size,
                    interpolate=True)
                for i in range(len(vcue_list))
            }

    # Background Components --------------------------------------------------------

    def init_progbar(self, bar_len=15.0, bar_height=0.35, bar_pos=[0, 10]):
        self.bar_len = bar_len  # total length
        self.bar_height = bar_height
        self.bar_pos = bar_pos
        # self.bar_pos = self.center_pos
        self.left_corner = self.bar_pos[0] - self.bar_len/2
        self.progBack = visual.Rect(
            self.win,
            width=self.bar_len,
            height=self.bar_height,
            pos=self.bar_pos,
            fillColor=self.color_dict["light_grey"])
        self.progTest = visual.Rect(
            self.win,
            width=0.01,
            height=self.bar_height,
            pos=self.bar_pos,
            fillColor=self.color_dict["green"])

    def draw_background(self):
        self.progBack.length = self.bar_len
        self.progBack.draw()
        self.progTest.draw()

    def move_prog_bar_step(self, bar_width_step, win_flip=True):
        # incrementally increase the bar width
        self.progTest.width += bar_width_step
        # re-center it accordingly on X-coordinate
        self.progTest.pos[0] = self.left_corner + self.progTest.width/2
        self.progTest.pos = self.progTest.pos.tolist()
        self.draw_background()
        if win_flip:
            self.win.flip()

    def move_prog_bar(self, start_width=0, end_width=1,
                      n_steps=100, wait_s=0.75, win_flip=True):
        # Setup starting state of progress bar
        self.progTest.width = start_width * self.progBack.width
        self.progTest.pos[0] = self.left_corner + start_width *\
            self.progBack.width/2
        bar_width_step = self.bar_len/n_steps

        # First display
        self.draw_background()
        if win_flip:
            self.win.flip()
            core.wait(wait_s)

        # Growing
        while self.progTest.width < self.progBack.width * end_width:
            self.move_prog_bar_step(bar_width_step, win_flip=win_flip)

        # Last bit for completion
        self.move_prog_bar_step(
            self.progBack.width * end_width - self.progTest.width,
            win_flip=win_flip)
        if win_flip:
            core.wait(1.5 * wait_s)
        return self.progTest.width / self.progBack.width

    # Trial Components --------------------------------------------------------
    def tFixation(self, duration=0.3, jitter=0.0):
        if self.use_pp:
            self.send_trigger("fix")
        self.fixation.draw()
        self.win.flip()
        core.wait(duration + jitter)

    def setCue(self, key, mode="random"):
        # opt: randomize mode
        if mode == "random":
            if np.random.randint(0, 2) == 1:
                mode = "textual"
            else:
                mode = "visual"
        # draw from resp. dict
        if mode == "visual":
            cue = self.vcue_dict.copy()[key]
        elif mode == "textual":
            cue = self.tcue_dict.copy()[key]
        return cue, mode

    def tMapcue(self, trial, mode="random",
                # with_background = False,  # would need flexible background
                duration=0.5):
        assert mode in ["visual", "textual", "random"],\
            "Chosen cue mode not implemented."
        # if with_background:
        #     rect.pos = center_pos
        #     rect.size = center_size
        #     rect.draw()
        n_cues = len(trial.map)
        for i in range(n_cues):
            cue, mode = self.setCue(trial.map[i], mode=mode)
            if n_cues > 1:  # move first cue up and the third cue down 6 degrees
                cue.pos = [sum(x) for x in zip(self.center_pos, [0, (1-i)*6])]
            else:
                cue.pos = self.center_pos
            cue.draw()
        if self.use_pp:
            if mode == "visual":
                self.send_trigger("vcue")
            elif mode == "textual":
                self.send_trigger("tcue")
        self.win.flip()
        core.wait(duration)
        return mode

    def getIR(self, IRClock, min_s=0.1, max_s=10):
        # get intermediate response
        intermediateResp = None
        core.wait(min_s)
        while intermediateResp == None and IRClock.getTime() < max_s:
            allKeys = event.waitKeys()
            for thisKey in allKeys:
                if thisKey in ["right"]:
                    intermediateRT = IRClock.getTime()
                    intermediateResp = 1
                elif thisKey in ["escape"]:
                    with open(self.file_name + ".txt", 'a') as f:
                        f.write("t_a = " + data.getDateStr() + "\n\n")
                    core.quit()  # abort experiment
            event.clearEvents()
        if intermediateResp == None and IRClock.getTime() >= max_s:
            intermediateRT = max_s
        return intermediateRT

    def tDisplay(self, trial, duration=1, self_paced=False):
        # draw rectangles
        self.rect.size = self.normal_size
        for pos in self.rect_pos:
            self.rect.pos = pos
            self.rect.draw()

        # draw stimuli
        for i in range(self.set_size):
            stim_name = trial.input_disp[i]
            if stim_name is not None:
                stim = self.stim_dict.copy()[stim_name]
                stim.pos = self.rect_pos[i]
                stim.draw()
        if self.use_pp:
            self.send_trigger("disp")
        self.win.flip()
        if self_paced:
            intermediateRT = self.getIR(core.Clock())
        else:
            core.wait(duration)
            intermediateRT = duration
        return intermediateRT

    def tEmpty(self, trial, IRClock):
        for pos in self.rect_pos:
            self.rect.pos = pos
            self.rect.draw()
        self.win.flip()
        intermediateRT = self.getIR(IRClock)
        return intermediateRT

    def tPause(self):
        self.draw_background()
        self.pauseClock.draw()
        self.pauseText.draw()
        self.win.flip()
        intermediateRT = self.getIR(core.Clock(), max_s=360)  # max 6 min break
        self.win.flip()
        return intermediateRT

    def tCount(self, trial, feedback=False, demonstration=False,
               resp_keys=None):
        if resp_keys is None:
            if self.expInfo["session"] == "3":
                resp_keys = self.resp_keys_vpixx
            else:
                resp_keys = self.resp_keys
        TestClock = core.Clock()
        for inc in range(2 + feedback*1):
            self.rect.pos = self.center_pos
            self.rect.size = self.center_size
            self.rect.draw()
            self.rect.size = self.normal_size
            self.rect.lineColor = self.color_dict["dark_grey"]
            stim = self.stim_dict.copy()[trial.target]
            stim.pos = self.center_pos
            stim.size = self.center_size
            stim.draw()
            stim.size = self.normal_size
            for i in range(len(self.resp_pos)):
                self.rect.pos = self.resp_pos[i]
                self.rect.draw()
                resp = self.count_dict[str(i)]
                resp.pos = self.resp_pos[i]
                resp.draw()

            # First cycle: Display stimuli
            if inc == 0:
                if self.use_pp:
                    self.send_trigger("count")
                self.win.flip()
                continue

            # Second cycle: Get test response
            if inc == 1:
                if not demonstration:
                    testRT, testResp = self.tTestresponse(
                        TestClock, resp_keys)
                else:
                    badoptions = np.array(range(4))
                    badoptions = np.delete(badoptions, trial.correct_resp)
                    core.wait(1)
                    testRT, testResp = 0, badoptions[0]

            # Third cycle: Feedback
            # immedeate feedback
            if feedback:
                if type(testResp) in [int, np.int64]:
                    self.rect.pos = self.resp_pos[testResp]
                    if trial.correct_resp == testResp:
                        self.rect.lineColor = self.color_dict["green"]
                    else:
                        self.rect.lineColor = self.color_dict["red"]
                    self.rect.draw()
                    self.rect.lineColor = self.color_dict["dark_grey"]
                    resp = self.count_dict[str(testResp)]
                    resp.pos = self.resp_pos[testResp]
                    resp.draw()
                if inc == 1:
                    self.win.flip()
                    continue

                # correct solution
                if trial.correct_resp != testResp:
                    corResp = trial.correct_resp
                    self.rect.pos = self.resp_pos[corResp]
                    self.rect.fillColor = self.color_dict["blue"]
                    self.rect.draw()
                    self.rect.fillColor = self.color_dict["light_grey"]
                    resp = self.count_dict[str(corResp)]
                    resp.pos = self.resp_pos[corResp]
                    resp.draw()
                    core.wait(1)
                    if inc == 2:
                        self.win.flip()
        return testRT, testResp

    def tPosition(self, trial, feedback=False, demonstration=False,
                  resp_keys=None):
        if resp_keys is None:
            if self.expInfo["session"] == "3":
                resp_keys = self.resp_keys_vpixx
            else:
                resp_keys = self.resp_keys
        TestClock = core.Clock()
        for inc in range(2 + feedback*1):
            # position cues
            for i in range(len(self.rect_pos)):
                self.rect.pos = self.rect_pos[i]
                if trial.target == i:
                    self.qm.pos = self.rect_pos[i]
                self.rect.draw()
                self.rect.lineColor = self.color_dict["dark_grey"]
            self.qm.draw()

            # response options
            for i in range(len(self.resp_pos)):
                self.rect.pos = self.resp_pos[i]
                self.rect.draw()
                resp = self.stim_dict.copy()[trial.resp_options[i]]
                resp.pos = self.resp_pos[i]
                resp.draw()

            # First cycle: Display stimuli
            if inc == 0:
                if self.use_pp:
                    self.send_trigger("position")
                self.win.flip()
                continue

            # Second cycle: Get test response
            if inc == 1:
                if not demonstration:
                    testRT, testResp = self.tTestresponse(
                        TestClock, resp_keys)
                else:
                    badoptions = np.array(range(4))
                    badoptions = np.delete(badoptions, trial.correct_resp)
                    core.wait(1)
                    testRT, testResp = 0, badoptions[0]

            # Third cycle: Feedback
            # immedeate feedback
            if feedback:
                if type(testResp) in [int, np.int64]:
                    self.rect.pos = self.resp_pos[testResp]
                    if trial.correct_resp == testResp:
                        self.rect.lineColor = self.color_dict["green"]
                    else:
                        self.rect.lineColor = self.color_dict["red"]
                    self.rect.draw()
                    self.rect.lineColor = self.color_dict["dark_grey"]
                    resp = self.stim_dict.copy()[trial.resp_options[testResp]]
                    resp.pos = self.resp_pos[testResp]
                    resp.draw()
                if inc == 1:
                    self.win.flip()
                    continue

            # correct solution
                if trial.correct_resp != testResp:
                    corResp = trial.correct_resp
                    self.rect.pos = self.resp_pos[corResp]
                    self.rect.fillColor = self.color_dict["blue"]
                    self.rect.draw()
                    self.rect.fillColor = self.color_dict["light_grey"]
                    resp = self.stim_dict.copy()[trial.resp_options[corResp]]
                    resp.pos = self.resp_pos[corResp]
                    resp.draw()
                    core.wait(1)
                    if inc == 2:
                        self.win.flip()
        return testRT, testResp

    def tLocalizer(self, trial, duration=2):
        if trial.type == "item":
            stim = self.stim_dict.copy()[trial.content]
            stim.size = self.center_size
        else:
            stim, _ = self.setCue(trial.content, mode=trial.type)

        for i in range(2):
            stim.pos[i] = self.center_pos[i] + \
                trial.pos[i] * self.center_size[i]
        stim.pos = stim.pos.tolist()
        stim.draw()
        if self.use_pp:
            self.send_trigger("cue")
        self.win.flip()
        core.wait(duration)

    def tSimilarity(self, stim_1, stim_2, pos_1, pos_2):
        self.ratingScale.reset()
        while self.ratingScale.noResponse:
            stim_1.pos = pos_1
            stim_1.draw()
            stim_2.pos = pos_2
            stim_2.draw()
            self.ratingScale.draw()
            self.win.flip()
        rating = self.ratingScale.getRating()
        RT = self.ratingScale.getRT()
        return rating, RT

    def tTestresponse(self, TestClock, respKeys, return_numeric=True,
                      max_wait=np.inf):
        testResp = None
        testRT = None
        while testResp is None:
            pressedKeys = event.waitKeys(maxWait=max_wait)
            if pressedKeys is None and max_wait < np.inf:
                break
            else:
                for thisKey in pressedKeys:
                    testRT = TestClock.getTime()
                    if thisKey in respKeys:
                        if return_numeric:
                            testResp = np.where(respKeys == thisKey)[0][0]
                        else:
                            testResp = thisKey
                    elif thisKey in ["right"]:
                        testResp = "NA"
                    elif thisKey == "escape":
                        with open(self.file_name + ".txt", 'a') as f:
                            f.write("t_a = " + data.getDateStr() + "\n\n")
                        core.quit()  # abort experiment
                event.clearEvents()
        return testRT, testResp

    def iSingleImage(self, *args, show_background=True):
        for arg in args:
            arg.pos = [0, 0]
            # arg.size = [10, 10]
            arg.draw()
            if show_background:
                self.draw_background()
            self.win.flip()
            core.wait(0.2)

    def iTransmutableObjects(self, *args, show_background=True):
        if show_background:
            self.draw_background()
        categories = list(self.stim_dict.keys())
        categories.sort()
        n_cats = self.n_cats  # alternatively show all using len(categories)
        if n_cats > 4:
            dim = [2, np.ceil(n_cats/2)]
        else:
            dim = [1, n_cats]

        category_pos = rectangularGrindPositions(
            center_pos=[0, 0], h_dist=10, dim=dim)

        # draw categories
        for i in range(n_cats):
            self.rect.pos = category_pos[i]
            self.rect.draw()
            stim = self.stim_dict.copy()[categories[i]]
            stim.pos = category_pos[i]
            stim.draw()
        self.win.flip()

    def iSpellExample(self, displays, show_background=True):
        # Input Display
        for i in range(2):
            rect_pos = circularGridPositions(center_pos=[0, 0],
                                             set_size=len(displays[0]), radius=8)
            for j in range(len(displays[0])):
                self.rect.pos = rect_pos[j]
                self.rect.draw()
                stim = self.stim_dict.copy()[displays[0][j]]
                stim.pos = rect_pos[j]
                stim.draw()
            if i == 0:
                if show_background:
                    self.draw_background()
                self.win.flip()
                core.wait(1)
                continue

            cue = self.magicWand
            cue.draw()
            if i == 1:
                if show_background:
                    self.draw_background()
                self.win.flip()
                core.wait(1)

        if len(displays) > 1:
            # Output Display
            rect_pos = circularGridPositions(center_pos=[0, 0],
                                             set_size=len(displays[1]),
                                             radius=8)
            for j in range(len(displays[1])):
                self.rect.pos = rect_pos[j]
                self.rect.draw()
                stim = self.stim_dict.copy()[displays[1][j]]
                stim.pos = rect_pos[j]
                stim.draw()
            if show_background:
                self.draw_background()
            self.win.flip()
            core.wait(1)

    def iNavigate(self, page=0, max_page=99, continue_after_last_page=True,
                  proceed_key="/k", wait_s=3):

        assert proceed_key in ["/k", "/m", "/t", "/e"], "Unkown proceed key"
        finished = False
        testResp = None
        TestClock = core.Clock()

        # get response or wait or something in between
        if proceed_key == "/k":  # keypress
            _, testResp = self.tTestresponse(
                TestClock, ["left", "right"],
                return_numeric=False)
        if proceed_key == "/m":  # meg keypress
            _, testResp = self.tTestresponse(
                TestClock, self.resp_keys_vpixx[-2:],
                return_numeric=False)
        elif proceed_key == "/t":  # time
            core.wait(wait_s)
            testResp = "right"
        elif proceed_key == "/e":  # either
            _, testResp = self.tTestresponse(
                TestClock, ["left", "right"],
                return_numeric=False,
                max_wait=wait_s)
            if testResp is None:
                testResp = "right"

        # Proceed accordingly
        if testResp in ["right", self.resp_keys_vpixx[-1]]:
            if page < max_page-1:
                page += 1
            elif continue_after_last_page:
                finished = True
            else:
                self.nextPrompt.draw()
                self.win.flip()
                _, contResp = self.tTestresponse(TestClock, ["left", "right"],
                                                 return_numeric=False)
                if contResp == "right":
                    finished = True
        elif testResp in ["left", self.resp_keys_vpixx[-2]] and page > 0:
            page -= 1

        return page, finished

    # Blocks and Loops---------------------------------------------------------
    def Instructions(self, part_key="Intro",
                     special_displays=list(),
                     args=list(),
                     complex_displays=list(),
                     kwargs=list(),
                     font="Times New Roman",
                     fontcolor=[-0.9, -0.9, -0.9],
                     show_background=True,
                     log_duration=True,
                     loading_time=2):
        assert part_key in self.instructions.keys(),\
            "No instructions provided for this part"

        self.instruct_stim.font = font
        self.instruct_stim.color = fontcolor

        # Initialize parameters
        finished = False
        Part = self.instructions[part_key]
        page = 0
        if show_background:
            self.draw_background()
        self.win.flip()
        self.win.flip()
        if log_duration:
            instructions_clock = core.Clock()
        while not finished:
            page_content, proceed_key, proceed_wait = Part[page]
            # page_content = Part[page][0]
            # proceed_key = Part[page][1]
            # proceed_wait = Part[page][2]
            if isinstance(page_content, str):
                self.instruct_stim.text = page_content
                self.instruct_stim.draw()
                if show_background:
                    self.draw_background()
                self.win.flip()
            elif isinstance(page_content, int):
                special_displays[page_content](
                    args[page_content],
                    show_background=show_background)
            elif isinstance(page_content, float):
                complex_displays[int(page_content)](
                    **kwargs[int(page_content)])
                if complex_displays[int(page_content)].__name__ in\
                        ["tPosition", "tCount"]:
                    if "feedback" not in kwargs[int(page_content)].keys():
                        self.win.flip()
                    elif not kwargs[int(page_content)]["feedback"]:
                        self.win.flip()
            page, finished = self.iNavigate(page=page, max_page=len(Part),
                                            proceed_key=proceed_key,
                                            wait_s=proceed_wait)
        if log_duration:
            duration = instructions_clock.getTime()
            with open(f"{self.file_name}.txt", 'a') as f:
                f.write(f"duration_{part_key} = {duration}\n")
        self.win.flip()
        core.wait(loading_time)

    def LearnCues(self, cue_center_pos=[0, 2], vert_dist=7,
                  modes=["textual", "visual"]):
        # Initialize parameters
        self.win.flip()
        finished = False
        cat_center_pos = [0, cue_center_pos[1] - vert_dist]
        page = 0
        category_pos = rectangularGrindPositions(
            center_pos=cat_center_pos, h_dist=15, dim=(1, 2))

        LearnClock = core.Clock()
        while not finished:
            # Draw map cue
            map_name = self.map_names[page]
            categories = map_name.split("-")

            for j in range(len(modes)):
                cue, _ = self.setCue(map_name, mode=modes[j])
                cue.pos = [sum(x) for x in
                           zip(cue_center_pos, [0, (1-j)*vert_dist])]
                cue.draw()

            # Draw corresponding explicit map
            for i in range(len(categories)):
                self.rect.pos = category_pos[i]
                self.rect.draw()
                cat = self.stim_dict.copy()[categories[i]]
                cat.pos = category_pos[i]
                cat.draw()
            self.leftArrow.pos = cat_center_pos
            self.leftArrow.draw()
            self.win.flip()
            core.wait(0.2)

            page, finished = self.iNavigate(
                page=page, max_page=self.n_primitives,
                continue_after_last_page=False)
        # Save learning duration
        learnDuration = LearnClock.getTime()
        return learnDuration

    def PracticeCues(self, trials_prim_cue, mode="visual", cue_pos=[0, 5],
                     resp_keys=None):

        assert self.n_cats in [4, 6], "unusual number of unique objects,"\
            "cannot set response keys"
        if resp_keys is None:
            if self.n_cats == 4:
                resp_keys = self.resp_keys
            elif self.n_cats == 6:
                resp_keys = self.resp_keys_wide

        # create the trial handler
        trials = data.TrialHandler(
            trials_prim_cue, 1, method="sequential")

        for trial in trials:
            trial["start_time"] = self.exp_clock.getTime()
            num_cr = len(trial.correct_resp)
            testRespList = []
            testRTList = []
            j = 0
            cue, cue_type = self.setCue(trial.map[0], mode=mode)
            cue.pos = cue_pos

            # Incrementally display stuff
            for inc in range(3 + 2 * num_cr):

                # 0. Fixation
                if inc == 0:
                    self.tFixation()
                    self.win.flip()
                    continue

                # 1. Map Cue
                cue.draw()
                if inc == 1:
                    self.win.flip()
                    core.wait(0.5)
                    continue

                # 2. Response options
                self.rect.lineColor = self.color_dict["dark_grey"]
                for i in range(len(self.cuepractice_pos)):
                    self.rect.pos = self.cuepractice_pos[i]
                    self.rect.draw()
                    resp = self.stim_dict.copy()[trial.resp_options[i]]
                    resp.pos = self.cuepractice_pos[i]
                    resp.draw()
                if inc == 2:
                    self.win.flip()
                    continue

                # 3. - 3 + num_cr: Immediate Feedback
                if inc in list(range(3, 3 + num_cr)):
                    TestClock = core.Clock()
                    testRT, testResp = self.tTestresponse(
                        TestClock, resp_keys)
                    testRTList.append(testRT)
                    testRespList.append(testResp)
                for i in range(len(testRespList)):
                    testResp = testRespList[i]
                    self.testResp = testResp
                    if testResp != "NA":
                        self.rect.pos = self.cuepractice_pos[testResp]
                        if trial.correct_resp[i] == testResp:
                            self.rect.lineColor = self.color_dict["green"]
                        else:
                            self.rect.lineColor = self.color_dict["red"]
                        self.rect.draw()
                        self.rect.lineColor = self.color_dict["dark_grey"]
                        resp = self.stim_dict.copy(
                        )[trial.resp_options[testResp]]
                        resp.pos = self.cuepractice_pos[testResp]
                        resp.draw()

                if inc in list(range(3, 3 + num_cr)):
                    self.win.flip()
                    continue

                # 4. If errors were made, draw correct response
                if trial.correct_resp != testRespList:
                    core.wait(1)
                    for i in range(1 + j):
                        corResp = trial.correct_resp[i]
                        self.rect.pos = self.cuepractice_pos[corResp]
                        self.rect.fillColor = self.color_dict["blue"]
                        self.rect.draw()
                        self.rect.fillColor = self.color_dict["light_grey"]
                        resp = self.stim_dict.copy(
                        )[trial.resp_options[corResp]]
                        resp.pos = self.cuepractice_pos[corResp]
                        resp.draw()
                if inc in list(range(3 + num_cr, 3 + 2 * num_cr - 1)):
                    j += 1
                    self.win.flip()
                    continue
                else:
                    trial["emp_resp"] = testRespList
                    trial["resp_RT"] = testRTList
                    trial["cue_type"] = cue_type
                    self.win.flip()
                    core.wait(2)

        return trials.trialList

    def GenericBlock(self, trial_df, mode="random", i=0, i_step=None,
                     self_paced=False, display_this=[1, 2, 3, 4, 5, 6, 7],
                     durations=[1.0, 3.0, 0.6, 1.0, 0.7],
                     test=True, feedback=False,
                     pause_between_runs=True, runlength=360,
                     resp_keys=None):
        if resp_keys is None:
            resp_keys = self.resp_keys

        # create the trial handler and optionally timer
        if i_step is None:
            i_step = len(trial_df)
        df = trial_df[i:i+i_step].copy()
        trials = data.TrialHandler(
            df, 1, method="sequential")

        # prepare progress bar
        n_trials = len(trials.trialList)
        trial_number = 1
        start_width_initial = self.start_width

        if pause_between_runs:
            run_number = 1
            timer = core.CountdownTimer(runlength)
            if self.use_pp:
                self.send_trigger("run")

        # check if jitter is specified
        if "jitter" not in trials.trialList[0].keys():
            jitter = [0.0, 0.0, 0.0]
            add_jitter = False
        else:
            add_jitter = True

        for trial in trials:
            if add_jitter:
                jitter = trial.jitter
            self.win.flip()
            trial["start_time"] = self.exp_clock.getTime()
            if self.use_pp:
                self.send_trigger("trial")

            # 1. Fixation
            if 1 in display_this:
                self.tFixation(jitter=jitter[0])

            # 2. Display Family
            if 2 in display_this:
                displayRT = self.tDisplay(trial,
                                          duration=durations[1] + jitter[1],
                                          self_paced=self_paced)

            # 3. Map Cue
            if 3 in display_this:
                self.tFixation()
                cue_type = self.tMapcue(trial, mode=mode,
                                        duration=durations[0] + jitter[2])

            if test:
                # 4. Transformation Display
                if 4 in display_this:
                    intermediateRT = self.tEmpty(trial, core.Clock())

                # 5. Empty Display
                if 5 in display_this:
                    self.win.flip()
                    core.wait(durations[2])

                # 6. Test Display
                if 6 in display_this:
                    if trial.test_type == "count":
                        testRT, testResp = self.tCount(trial,
                                                       feedback=feedback,
                                                       resp_keys=resp_keys)
                    elif trial.test_type == "position":
                        testRT, testResp = self.tPosition(trial,
                                                          feedback=feedback,
                                                          resp_keys=resp_keys)

                    # Save data
                    trial["run_number"] = run_number
                    trial["display_RT"] = displayRT
                    trial["inter_RT"] = intermediateRT
                    trial["emp_resp"] = testResp
                    trial["resp_RT"] = testRT
                    trial["cue_type"] = cue_type
                    core.wait(durations[3])

            if 7 in display_this:
                self.win.flip()
                self.win.flip()
                core.wait(durations[4])

            if pause_between_runs:
                if timer.getTime() <= 0:
                    # Update Progress Bar
                    progbar_inc_tmp = trial_number/n_trials * self.progbar_inc
                    self.start_width = self.move_prog_bar(
                        start_width=self.start_width,
                        end_width=start_width_initial + progbar_inc_tmp,
                        n_steps=2, wait_s=0, win_flip=False)

                    # Pause Display
                    self.tPause()
                    timer.reset()
                    run_number += 1
                    if self.use_pp:
                        self.send_trigger("run")

            trial_number += 1
        return trials.trialList

    def CuePracticeLoop(self, trials_prim_cue, first_modality, second_modality,
                        min_acc=0.90, mode="random", i=0, i_step=None,
                        show_cheetsheet=True):
        mean_acc = 0.0
        df_list = []
        if i_step is None:
            i_step = self.n_exposure * self.maxn_blocks
        while mean_acc < min_acc and i+i_step <= len(trials_prim_cue):
            df = trials_prim_cue[i:i+i_step].copy()
            result = self.PracticeCues(df, mode=mode)
            df_list.append(result)
            errors = [trial["correct_resp"] == trial["emp_resp"]
                      for trial in result]
            mean_acc = np.mean(list(map(int, errors)))  # convert to integers

            accPrompt = visual.TextStim(
                self.win, text=str(np.round(mean_acc * 100)) + "%",
                height=2.5,
                wrapWidth=30,
                font="Times New Roman",
                color=self.color_dict["black"])

            # repeat or wrap up
            i += i_step
            if mean_acc < min_acc:
                feedbacktype = "Feedback0"
            else:
                feedbacktype = "Feedback1"
            self.Instructions(part_key=feedbacktype,
                              special_displays=[self.iSingleImage],
                              args=[accPrompt])
            if show_cheetsheet and mean_acc < min_acc:
                self.LearnCues()
            core.wait(2)
        df_out = [item for sublist in df_list for item in sublist]
        return df_out

    def TestPracticeLoop(self, trial_df,
                         min_acc=0.9, mode="random", i=0, i_step=None,
                         durations=[1.0, 3.0, 0.6, 1.0, 0.7],
                         test=True, feedback=False, self_paced=False,
                         pause_between_runs=True, runlength=360):
        mean_acc = 0.0
        df_list = []
        if i_step is None:
            i_step = self.n_exposure * self.maxn_blocks  # length of one loop
        while mean_acc < min_acc:
            result = self.GenericBlock(trial_df, mode=mode, i=i, i_step=i_step,
                                       durations=durations, test=test, feedback=feedback,
                                       self_paced=self_paced, runlength=runlength,
                                       pause_between_runs=pause_between_runs)
            df_list.append(result)
            errors = [trial["correct_resp"] == trial["emp_resp"]
                      for trial in result]
            mean_acc = np.mean(list(map(int, errors)))  # convert to integers

            accPrompt = visual.TextStim(
                self.win, text=str(np.round(mean_acc * 100)) + "%", height=2.5,
                wrapWidth=30, font="Times New Roman",
                color=self.color_dict["black"])

            # repeat or wrap up
            i += i_step
            if mean_acc < min_acc:
                feedbacktype = "Feedback0Test"
            else:
                feedbacktype = "Feedback1"
            self.Instructions(part_key=feedbacktype,
                              special_displays=[self.iSingleImage],
                              args=[accPrompt])
        df_out = [item for sublist in df_list for item in sublist]
        return df_out

    def LocalizerBlock(self, trial_df, durations=[2.0, 2.0, 2.0, 1.0],
                       resp_keys=[]):
        # create the trial handler
        self.trials = data.TrialHandler(
            trial_df, 1, method="sequential")

        for trial in self.trials:
            self.win.flip()
            if self.use_pp:
                self.send_trigger("trial")
            trial["start_time"] = self.exp_clock.getTime()

            # 1. Fixation
            self.tFixation()

            # 2. Display stimulus
            self.tLocalizer(trial, duration=durations[0])

            # 3. Empty Display
            self.win.flip()
            core.wait(durations[1])

            # 4. Catch Trial Query
            if trial.catch:

                # Prepare query
                if trial.type == "item":
                    # transform alphabetical to numeric
                    name_index = ord(trial.query_stim) - 65
                    name = self.item_names[name_index]
                    text = "Was the previous item a\n" + name + "?"
                else:
                    text = "Was the previous cue equivalent to..."

                # Display query text
                textStim = visual.TextStim(
                    self.win,
                    text,
                    font="Times New Roman",
                    color=self.color_dict["black"],
                    height=1.8,
                    pos=self.center_pos,
                    wrapWidth=40)
                textStim.draw()
                self.win.flip()
                if self.use_pp:
                    self.send_trigger("identity")
                # core.wait(durations[2])

                # For Cue trials, display display cue of other type
                if trial.type != "item":
                    stim, _ = self.setCue(trial.content,
                                          mode=trial.query_type)
                    stim.pos = self.center_pos
                    stim.draw()
                    self.win.flip()

                # Get response
                TestClock = core.Clock()
                testRT, testResp = self.tTestresponse(
                    TestClock, resp_keys)
                self.win.flip()

                # Interpret response according to mapping in self.resp_keys_vpixx / self.resp_keys_alt
                if testResp == 4:
                    testResp = False
                elif testResp == 5:
                    testResp = True

                core.wait(durations[3])
            else:
                testResp = None
                testRT = None

            # Save data
            trial["emp_resp"] = testResp
            trial["resp_RT"] = testRT

        # calculate accuracy
        correct_responses = [trial["emp_resp"] == trial["cor_resp"]
                             for trial in self.trials if trial.catch]
        accuracy = sum(correct_responses) / len(correct_responses)

        return self.trials.triallist, accuracy

    def LocalizerLoop(self, durations=[2.0, 2.0, 2.0, 1.0], min_acc=0.8,
                      resp_keys=[]):
        # Localizer Block
        df_out, acc = self.LocalizerBlock(self.trials_localizer,
                                          durations=durations,
                                          resp_keys=resp_keys)
        # fname = self.data_dir + os.sep + self.expInfo["participant"] + "_" +\
        #     self.expInfo["dateStr"] + "_" + "localizer_MEG"

        # Conditionally repeat or stop experiment
        if acc < min_acc:
            self.Instructions(part_key="BadLocalizer",
                              special_displays=[self.iSingleImage],
                              args=[self.keyboard_dict["keyBoardMegNY"]],
                              show_background=False)
            self.trials_localizer2 = np.random.permutation(
                self.trials_localizer).tolist()
            df_out_again, acc_2 = self.LocalizerBlock(self.trials_localizer2,
                                                      durations=durations,
                                                      resp_keys=resp_keys)
            # save_object(self.df_out_8 + self.df_out_8_again,
            #             fname, ending = 'csv')
            if acc_2 < min_acc:
                self.Instructions(part_key="DropOut",
                                  show_background=False)
                with open(self.file_name + ".txt", 'a') as f:
                    f.write("t_a = " + data.getDateStr() + "\n\n")
                core.quit()
            else:
                df_out = df_out + df_out_again
        # else:
            # save_object(self.df_out_8, fname, ending = 'csv')
        self.start_width = self.move_prog_bar(
            start_width=0,
            end_width=self.progbar_inc)

        return df_out

    def CueSimilarityTest(self, cue_dict, pos_1=[-5, 0], pos_2=[5, 0]):
        # Prepare visual comparisons
        stim_names = list(cue_dict.keys())
        unique_pairs = []
        for i in range(len(stim_names)):
            for j in range(i, len(stim_names)):
                unique_pairs.append((stim_names[i], stim_names[j]))
        unique_pairs = np.random.permutation(unique_pairs)

        # Perform visual comparisons
        triallist = []
        for pair in unique_pairs:
            stim_1 = cue_dict[pair[0]]
            stim_2 = cue_dict[pair[1]]
            rating, RT = self.tSimilarity(stim_1, stim_2, pos_1, pos_2)
            triallist.append({"cue_1": pair[0],
                              "cue_2": pair[1],
                              "dissimilarity": rating,
                              "RT": RT})
            self.win.flip()
            core.wait(0.5)
        return triallist

    ###########################################################################
    # Introduction Session
    ###########################################################################
    def Session1(self, check_similarity=False):
        # globalClock = core.Clock()
        n_experiment_parts = 5
        self.progbar_inc = 1/n_experiment_parts

        # Similarity Task
        if check_similarity:
            self.df_sim1 = self.CueSimilarityTest(
                self.vcue_full,
                pos_1=[-5, self.center_pos[1]],
                pos_2=[5, self.center_pos[1]])
            core.wait(1)
            self.df_sim2 = self.CueSimilarityTest(
                self.tcue_full,
                pos_1=[sum(x) for x in zip(self.center_pos, [0, 6])],
                pos_2=[sum(x) for x in zip(self.center_pos, [0, 0])])

            fname = self.data_dir + os.sep + self.expInfo["participant"] + "_" + \
                self.expInfo["dateStr"] + "_" + "similarity"
            save_object(self.df_sim1 + self.df_sim2, fname, ending='csv')

        # Navigation
        self.win.mouseVisible = False
        self.Instructions(part_key="Navigation1",
                          special_displays=[self.iSingleImage,
                                            self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardArrows"],
                                self.keyboard_dict["keyBoardEsc"]],
                          font="mono",
                          fontcolor=self.color_dict["mid_grey"],
                          show_background=False)

        # Introduction
        self.Instructions(part_key="Intro",
                          special_displays=[self.iSingleImage,
                                            self.iSingleImage,
                                            self.iTransmutableObjects,
                                            self.iSpellExample,
                                            self.iSpellExample],
                          args=[self.magicBooks,
                                self.philbertine,
                                None,
                                [["A", "B", "C", "D"], ["A", "D", "C", "D"]],
                                [["A", "B", "B", "D"], ["A", "D", "D", "D"]]])

        # -------------------------------------------------------------------
        # Balance out which cue modality is learned first
        if int(self.expInfo["participant"]) % 2 == 0:
            first_modality = "visual"
            second_modality = "textual"
        else:
            first_modality = "textual"
            second_modality = "visual"

        # Learn first cue type
        self.learnDuration_1 = self.LearnCues()
        with open(self.file_name + ".txt", 'a') as f:
            f.write("learnDuration_1 = " + str(self.learnDuration_1) + "\n")
        self.start_width = self.move_prog_bar(
            start_width=0,
            end_width=self.progbar_inc)

        # Test first cue type
        self.Instructions(part_key="Intermezzo1",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoard" + str(self.n_cats)]])
        self.df_out_1 = self.CuePracticeLoop(
            self.trials_prim_cue, first_modality, second_modality,
            mode=first_modality)
        self.start_width = self.move_prog_bar(
            start_width=self.start_width,
            end_width=self.start_width + self.progbar_inc)

        # Learn second cue type
        self.Instructions(part_key="Intermezzo2",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoard" + str(self.n_cats)]])
        self.learnDuration_2 = self.LearnCues()
        with open(self.file_name + ".txt", 'a') as f:
            f.write("learnDuration_2 = " + str(self.learnDuration_2) + "\n")

        # Test second cue type
        self.df_out_2 = self.CuePracticeLoop(
            self.trials_prim_cue, first_modality, second_modality,
            mode=second_modality,
            i=len(self.df_out_1))
        self.start_width = self.move_prog_bar(
            start_width=self.start_width,
            end_width=self.start_width + self.progbar_inc)

        # Save cue memory data
        fname = self.data_dir + os.sep + self.expInfo["participant"] + "_" + \
            self.expInfo["dateStr"] + "_" + "cueMemory"
        save_object(self.df_out_1 + self.df_out_2, fname, ending='csv')

        # ---------------------------------------------------------------------
        # Balance out which test type is learned first
        if int(self.expInfo["participant"]) % 2 == 0:
            first_test = "count"
            tFirst = self.tCount
            trials_test_1 = self.trials_prim_prac_c.copy()
            second_test = "position"
            tSecond = self.tPosition
            trials_test_2 = self.trials_prim_prac_p.copy()
        else:
            first_test = "position"
            tFirst = self.tPosition
            trials_test_1 = self.trials_prim_prac_p.copy()
            second_test = "count"
            tSecond = self.tCount
            trials_test_2 = self.trials_prim_prac_c.copy()

        # Get Demo trials
        demoTrials1 = data.TrialHandler(
            trials_test_1[0:1], 1, method="sequential")
        demoTrial1 = demoTrials1.trialList[0]
        demoTrials2 = data.TrialHandler(
            trials_test_2[0:1], 1, method="sequential")
        demoTrial2 = demoTrials2.trialList[0]

        # First Test-Type
        self.Instructions(part_key="TestTypes",
                          special_displays=[self.iSingleImage],
                          args=[self.magicWand],
                          complex_displays=[self.GenericBlock],
                          kwargs=[{"trial_df": self.trials_prim_prac_p,
                                   "durations": [1, 3, 0.6, 0, 0],
                                   "i_step": 1,
                                   "test": False}],
                          loading_time=0)
        self.Instructions(part_key=first_test + "First",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoard4"]],
                          complex_displays=[self.GenericBlock, self.GenericBlock,
                                            tFirst, tFirst],
                          kwargs=[{"trial_df": trials_test_1,
                                   "display_this": [2],
                                   "durations": [0, 0, 0, 0, 0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": trials_test_1,
                                   "display_this": [3, 4],
                                   "durations": [0, 0, 0, 0, 0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial": demoTrial1,
                                   "feedback": False,
                                   "demonstration": True},
                                  {"trial": demoTrial1,
                                   "feedback": True,
                                   "demonstration": True}])

        start_width_before_block = self.start_width.copy()
        self.df_out_3 = self.TestPracticeLoop(trials_test_1,
                                              # i_step = 5, # for testing
                                              min_acc=0.95,
                                              self_paced=True,
                                              feedback=True,
                                              pause_between_runs=True,
                                              runlength=360)
        self.start_width = self.move_prog_bar(
            start_width=self.start_width,
            end_width=start_width_before_block + self.progbar_inc)

        # Second Test-Type
        self.Instructions(part_key=second_test + "Second",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoard4"]],
                          complex_displays=[
                              self.GenericBlock, tSecond, tSecond],
                          kwargs=[{"trial_df": trials_test_2,
                                   "display_this": [2, 3],
                                   "durations": [0, 2, 0, 0, 0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial": demoTrial2,
                                   "feedback": False,
                                   "demonstration": True},
                                  {"trial": demoTrial2,
                                   "feedback": True,
                                   "demonstration": True}])
        self.df_out_4 = self.TestPracticeLoop(trials_test_2,
                                              # i_step = 5, # for testing
                                              min_acc=0.95,
                                              self_paced=True,
                                              feedback=True,
                                              pause_between_runs=True,
                                              runlength=360)
        self.move_prog_bar(start_width=self.start_width,
                           end_width=1)

        # Save test type data
        fname = self.data_dir + os.sep + self.expInfo["participant"] + "_" +\
            self.expInfo["dateStr"] + "_" + "testType"
        save_object(self.df_out_3 + self.df_out_4, fname, ending='csv')

        self.Instructions(part_key="Bye")
        with open(self.file_name + ".txt", 'a') as f:
            f.write("t_n = " + data.getDateStr() + "\n\n")
        self.win.close()

    ###########################################################################
    # Training Session
    ###########################################################################
    def Session2(self):
        self.win.mouseVisible = False
        n_experiment_parts = 3
        self.progbar_inc = 1/n_experiment_parts

        # Navigation
        self.Instructions(part_key="Navigation2",
                          special_displays=[self.iSingleImage,
                                            self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardArrows"],
                                self.keyboard_dict["keyBoardEsc"]],
                          font="mono",
                          fontcolor=self.color_dict["mid_grey"],
                          show_background=False)

        # Introduction
        self.Instructions(part_key="IntroAdvanced",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoard" + str(self.n_cats)]])

        # Cue memory
        self.df_out_5 = self.CuePracticeLoop(
            self.trials_prim_cue, "visual", "textual",
            mode="random")
        self.start_width = self.move_prog_bar(start_width=0,
                                              end_width=0 + self.progbar_inc)

        # Save cue memory data
        fname = self.data_dir + os.sep + self.expInfo["participant"] + "_" +\
            self.expInfo["dateStr"] + "_" + "cueMemoryRefresher.csv"
        save_object(self.df_out_5, fname, ending='csv')

        # Reminder of the test types
        demoCounts = data.TrialHandler(self.trials_prim_prac_c[0:1], 1,
                                       method="sequential")
        demoCount = demoCounts.trialList[0]
        demoPositions = data.TrialHandler(self.trials_prim_prac_p[0:1], 1,
                                          method="sequential")
        demoPosition = demoPositions.trialList[0]

        self.Instructions(part_key="TestTypesReminder",
                          special_displays=[
                              self.iSingleImage, self.iSingleImage],
                          args=[self.magicWand, self.keyboard_dict["keyBoard4"]],
                          complex_displays=[self.GenericBlock, self.GenericBlock,
                                            self.GenericBlock, self.tCount, self.tPosition],
                          kwargs=[{"trial_df": self.trials_prim_prac_c,
                                   "display_this": [2],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_prim_prac_c,
                                   "display_this": [3, 7],
                                   "durations": [1.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_prim_prac_c,
                                   "display_this": [4],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                  "i_step": 1,
                                   "test": True},
                                  {"trial": demoCount,
                                   "feedback": False,
                                   "demonstration": True},
                                  {"trial": demoPosition,
                                   "feedback": False,
                                   "demonstration": True}],
                          loading_time=0)

        # ---------------------------------------------------------------------
        # Practice: Primitive
        self.Instructions(part_key="Primitives",
                          special_displays=[
                              self.iSingleImage, self.iSingleImage],
                          args=[self.magicWand,
                                self.keyboard_dict["keyBoard4"]])
        start_width_before_block = self.start_width.copy()
        self.df_out_6 = self.TestPracticeLoop(self.trials_prim,
                                              min_acc=0.95,
                                              self_paced=True,
                                              feedback=True,
                                              pause_between_runs=True,
                                              runlength=360)
        self.start_width = self.move_prog_bar(
            start_width=self.start_width,
            end_width=start_width_before_block + self.progbar_inc)

        # Practice: Binary
        self.Instructions(part_key="Binaries",
                          special_displays=[
                              self.iSingleImage, self.iSingleImage],
                          args=[self.magicWand,
                                self.keyboard_dict["keyBoard4"]],
                          complex_displays=[self.GenericBlock, self.GenericBlock,
                                            self.GenericBlock],
                          kwargs=[{"trial_df": self.trials_bin_MEG,
                                   "display_this": [2],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_bin_MEG,
                                   "display_this": [3, 7],
                                   "durations": [1.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_bin_MEG,
                                   "display_this": [4],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                  "i_step": 1,
                                   "test": True}])
        self.df_out_7 = self.TestPracticeLoop(self.trials_bin,
                                              min_acc=0.75,
                                              durations=[
                                                  2.0, 3.0, 0.6, 1.0, 0.7],
                                              self_paced=True,
                                              feedback=True,
                                              pause_between_runs=True,
                                              runlength=360)
        self.move_prog_bar(start_width=self.start_width,
                           end_width=1)

        # Save generic data
        fname = self.data_dir + os.sep + self.expInfo["participant"] + "_" +\
            self.expInfo["dateStr"] + "_" + "generic"
        save_object(self.df_out_6 + self.df_out_7, fname, ending='csv')
        self.Instructions(part_key="Bye")
        with open(self.file_name + ".txt", 'a') as f:
            f.write("t_n = " + data.getDateStr() + "\n\n")
        self.win.close()

    ###########################################################################
    # MEG Session
    ###########################################################################

    def Session3(self, resp_keys="resp_keys_vpixx"):
        self.win.mouseVisible = False
        n_experiment_parts = 4
        self.progbar_inc = 1/n_experiment_parts
        self.start_width = 0
        resp_keys = eval("self." + resp_keys)

        # Part 1
        # Navigation
        self.Instructions(part_key="Navigation3",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMegBF"]],
                          font="mono",
                          fontcolor=self.color_dict["mid_grey"],
                          show_background=False)

        # Introduction
        self.Instructions(part_key="IntroMEG",
                          special_displays=[self.iTransmutableObjects,
                                            self.iSingleImage],
                          args=[None,
                                self.keyboard_dict["keyBoardMegNY"]],
                          show_background=False)

        # Localizer Block
        self.df_out_8 = self.LocalizerLoop(durations=[2.0, 2.0, 2.0, 1.0],
                                           min_acc=0.8,
                                           resp_keys=resp_keys)
        fname = self.data_dir + os.sep + self.expInfo["participant"] + "_" +\
            self.expInfo["dateStr"] + "_" + "localizer_MEG"
        save_object(self.df_out_8, fname, ending='csv')

        # Part 2 #TODO Make practice loop out of this?
        # Primitive Decoder Block
        self.Instructions(part_key="PrimDecMEG1",
                          special_displays=[self.iSingleImage],
                          args=[self.magicWand])
        self.learnDuration_3 = self.LearnCues()
        with open(self.file_name + ".txt", 'a') as f:
            f.write("learnDuration_3= " + str(self.learnDuration_3) + "\n")
        self.Instructions(part_key="PrimDecMEG2",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMeg0123"]])
        start_width_before_block = self.start_width.copy()
        self.df_out_9 = self.GenericBlock(self.trials_prim_dec,
                                          mode="random",
                                          self_paced=True,
                                          pause_between_runs=True,
                                          runlength=360,
                                          feedback=True,
                                          resp_keys=resp_keys)
        self.start_width = self.move_prog_bar(
            start_width=self.start_width,
            end_width=start_width_before_block + self.progbar_inc)
        save_object(self.df_out_9, fname, ending='csv')

        # Part 3
        # Primitive trials
        demoCounts = data.TrialHandler(self.trials_prim_prac_c[0:1], 1,
                                       method="sequential")
        demoCount = demoCounts.trialList[0]
        demoPositions = data.TrialHandler(self.trials_prim_prac_p[0:1], 1,
                                          method="sequential")
        demoPosition = demoPositions.trialList[0]

        self.Instructions(part_key="PrimitivesMEG",
                          special_displays=[
                              self.iSingleImage, self.iSingleImage],
                          args=[self.magicWand,
                                self.keyboard_dict["keyBoardMeg0123"]],
                          complex_displays=[self.GenericBlock, self.GenericBlock,
                                            self.GenericBlock, self.tCount, self.tPosition],
                          kwargs=[{"trial_df": self.trials_prim_prac_c,
                                   "display_this": [2],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_prim_prac_c,
                                   "display_this": [3, 7],
                                   "durations": [1.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_prim_prac_c,
                                   "display_this": [4],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                  "i_step": 1,
                                   "test": True},
                                  {"trial": demoCount,
                                   "feedback": False,
                                   "demonstration": True},
                                  {"trial": demoPosition,
                                   "feedback": False,
                                   "demonstration": True}])

        start_width_before_block = self.start_width.copy()
        self.df_out_10 = self.GenericBlock(self.trials_prim_MEG,
                                           mode="random",
                                           durations=[1.0, 3.0, 0.6, 1.0, 0.7],
                                           self_paced=True,
                                           pause_between_runs=True,
                                           runlength=360,
                                           resp_keys=resp_keys)
        self.start_width = self.move_prog_bar(
            start_width=self.start_width,
            end_width=start_width_before_block + self.progbar_inc)

        # Part 4
        # Binary trials
        self.Instructions(part_key="BinariesMEG",
                          special_displays=[
                              self.iSingleImage, self.iSingleImage],
                          args=[self.magicWand,
                                self.keyboard_dict["keyBoardMeg0123"]])
        self.df_out_11 = self.GenericBlock(self.trials_bin_MEG,
                                           mode="random",
                                           durations=[2.0, 3.0, 0.6, 1.0, 0.7],
                                           self_paced=True,
                                           pause_between_runs=True,
                                           runlength=360,
                                           resp_keys=self.resp_keys_vpixx)
        self.move_prog_bar(start_width=self.start_width, end_width=1)

        # Finalization
        fname = self.data_dir + os.sep + self.expInfo["participant"] + "_" +\
            self.expInfo["dateStr"] + "_" + "generic_MEG"
        save_object(self.df_out_10 + self.df_out_11, fname, ending='csv')

        self.Instructions(part_key="ByeBye")
        with open(self.file_name + ".txt", 'a') as f:
            f.write("t_n = " + data.getDateStr() + "\n\n")
        self.win.close()

    ###########################################################################
    # MEG Session (Version 2)
    ###########################################################################
    def Session3R(self, resp_keys="resp_keys_vpixx"):
        self.win.mouseVisible = False
        n_experiment_parts = 3
        self.progbar_inc = 1/n_experiment_parts
        self.start_width = 0
        resp_keys = eval("self." + resp_keys)

        # Part 1
        # Navigation
        self.Instructions(part_key="Navigation3",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMegBF"]],
                          font="mono",
                          fontcolor=self.color_dict["mid_grey"],
                          show_background=False)

        # Introduction
        self.Instructions(part_key="IntroMEG",
                          special_displays=[self.iTransmutableObjects,
                                            self.iSingleImage],
                          args=[None,
                                self.keyboard_dict["keyBoardMegNY"]],
                          show_background=False)

        # Localizer Block
        self.df_out_8 = self.LocalizerLoop(durations=[2.0, 2.0, 2.0, 1.0],
                                           min_acc=0.8,
                                           resp_keys=resp_keys)
        self.start_width = self.move_prog_bar(
            start_width=self.start_width,
            end_width=self.progbar_inc)
        fname = self.data_dir + os.sep + self.expInfo["participant"] + "_" +\
            self.expInfo["dateStr"] + "_" + "localizer_MEG"
        save_object(self.df_out_8, fname, ending='csv')

        # Part 2
        # Primitive trials
        demoCounts = data.TrialHandler(self.trials_prim_prac_c[0:1], 1,
                                       method="sequential")
        demoCount = demoCounts.trialList[0]
        demoPositions = data.TrialHandler(self.trials_prim_prac_p[0:1], 1,
                                          method="sequential")
        demoPosition = demoPositions.trialList[0]

        self.Instructions(part_key="PrimitivesMEGR",
                          special_displays=[
                              self.iSingleImage, self.iSingleImage],
                          args=[self.magicWand,
                                self.keyboard_dict["keyBoardMeg0123"]],
                          complex_displays=[self.GenericBlock, self.GenericBlock,
                                            self.GenericBlock, self.tCount, self.tPosition],
                          kwargs=[{"trial_df": self.trials_prim_prac_c,
                                   "display_this": [2],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_prim_prac_c,
                                   "display_this": [3, 7],
                                   "durations": [1.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_prim_prac_c,
                                   "display_this": [4],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                  "i_step": 1,
                                   "test": True},
                                  {"trial": demoCount,
                                   "feedback": False,
                                   "demonstration": True},
                                  {"trial": demoPosition,
                                   "feedback": False,
                                   "demonstration": True}])

        start_width_before_block = self.start_width.copy()
        self.df_out_10 = self.TestPracticeLoop(self.trials_prim_MEG,
                                               mode="random",
                                               min_acc=0.95,
                                               durations=[
                                                   1.0, 3.0, 0.6, 1.0, 0.7],
                                               self_paced=True,
                                               feedback=True,
                                               pause_between_runs=True,
                                               runlength=360,
                                               resp_keys=resp_keys)
        self.start_width = self.move_prog_bar(
            start_width=self.start_width,
            end_width=start_width_before_block + self.progbar_inc)

        # Part 3
        # Binary trials
        self.Instructions(part_key="BinariesMEGR",
                          special_displays=[
                              self.iSingleImage, self.iSingleImage],
                          args=[self.magicWand,
                                self.keyboard_dict["keyBoardMeg0123"]],
                          complex_displays=[self.GenericBlock, self.GenericBlock,
                                            self.GenericBlock],
                          kwargs=[{"trial_df": self.trials_bin_MEG,
                                   "display_this": [2],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_bin_MEG,
                                   "display_this": [3, 7],
                                   "durations": [1.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_bin_MEG,
                                   "display_this": [4],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                  "i_step": 1,
                                   "test": True}])
        self.df_out_11 = self.TestPracticeLoop(self.trials_bin_MEG,
                                               mode="random",
                                               min_acc=0.75,
                                               durations=[
                                                   2.0, 3.0, 0.6, 1.0, 0.7],
                                               self_paced=True,
                                               feedback=True,
                                               pause_between_runs=True,
                                               runlength=360,
                                               resp_keys=resp_keys)
        self.move_prog_bar(start_width=self.start_width, end_width=1)

        # Finalization
        fname = self.data_dir + os.sep + self.expInfo["participant"] + "_" +\
            self.expInfo["dateStr"] + "_" + "generic_MEG"
        save_object(self.df_out_10 + self.df_out_11, fname, ending='csv')

        self.Instructions(part_key="ByeBye")
        with open(self.file_name + ".txt", 'a') as f:
            f.write("t_n = " + data.getDateStr() + "\n\n")
        self.win.close()


# =============================================================================
# Helper Functions
# =============================================================================

# Positions -------------------------------------------------------------------
def rectangularGrindPositions(center_pos=[0, 0],
                              v_dist=10, h_dist=10, dim=(2, 3)):
    # horizontal positions
    c = np.floor(dim[1]/2)
    if dim[1] % 2 != 0:  # odd number of items on vertical tile => center
        rect_hpos = np.arange(-c * h_dist + center_pos[0],
                              c * h_dist + 1 + center_pos[0], h_dist).tolist()
    else:
        rect_hpos = np.arange(-c * h_dist + h_dist/2 + center_pos[0],
                              c * h_dist - h_dist/2 + center_pos[0] + 1,
                              h_dist).tolist()

    # vertical positions
    c = np.floor(dim[0]/2)
    if dim[0] % 2 != 0:
        rect_vpos = np.arange(-c * v_dist + center_pos[1],
                              c * v_dist + 1 + center_pos[1], v_dist).tolist()
    else:  # even number of items on horizontal tile => shift upwards
        rect_vpos = np.arange(-c * v_dist + v_dist/2 + center_pos[1],
                              c * v_dist - v_dist/2 + center_pos[1] + 1,
                              v_dist).tolist()

    # combine
    rect_pos = np.transpose([np.tile(rect_hpos, len(rect_vpos)),
                             np.repeat(rect_vpos, len(rect_hpos))])
    return rect_pos


def circularGridPositions(center_pos=[0, 0], set_size=6, radius=10):
    angle = 2*np.pi/set_size
    rect_pos = np.empty((set_size, 2), dtype=float).copy()
    for i in range(set_size):
        rect_pos[i] = [center_pos[0] + radius * np.sin(i * angle),
                       center_pos[1] + radius * np.cos(i * angle)]
    return rect_pos


# Data handling ---------------------------------------------------------------
def readpkl(fname):
    with open(fname) as f:
        listofdicts = [{k: v for k, v in row.items()}
                       for row in csv.DictReader(f, skipinitialspace=True)]
    return listofdicts


def listofdicts2csv(listofdicts, fname):
    # spread dictionary entries which are n-long lists into n separate elements
    keys = listofdicts[0].keys()
    list_keys = []
    # find out which keys point to lists
    for key in keys:
        if type(listofdicts[0][key]) in [set, list, np.ndarray]:
            list_keys.append(key)

    # for each such key, pop it from the dict and add its elements back to dict
    for dictionary in listofdicts:
        for key in list_keys:
            items = dictionary.pop(key)
            newkeys = [key + "_" + str(i) for i in range(len(items))]
            subdictionary = dict(zip(newkeys, items))
            dictionary.update(subdictionary)

    # write to csv
    with open(fname, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(listofdicts)


def save_object(obj, fname, ending='pkl'):
    if ending == 'csv':
        listofdicts2csv(obj, fname + '.csv')
    elif ending == 'pkl':
        with open(fname + '.pkl', "wb") as f:
            pickle.dump(obj, f)
