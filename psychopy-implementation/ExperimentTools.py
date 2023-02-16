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
print("Loading psychopy...")
from psychopy import __version__, core, event, visual, gui, data, monitors
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

        # inputs and dimensions
        self.resp_keys_kb = ["d", "f", "j", "k"]
        self.resp_keys_vpixx = ["2", "1", "up", "left", "4", "right"]
        # Buttons: lMiddlefinger, lIndex, rIndex, rMiddlefinger, lThumb, rThumb
        # Mapping: 0, 1, 2, 3, False, True

        self.center_pos = [0, 5]
        self.center_size = [8, 8]
        self.normal_size = [5, 5]
        self.color_dict = {"light_grey": [0.7, 0.7, 0.7],
                           "mid_grey": [0.0, 0.0, 0.0],
                           "dark_grey": [-0.6, -0.6, -0.6],
                           "black": [-0.9, -0.9, -0.9],
                           "red": [0.8, 0.0, 0.0],
                           "yellow": [1.0, 0.8, 0.0],
                           "green": [0.0, 0.6, 0.0],
                           "blue": [0.2, 0.6, 1.0],
                           "dark_blue": [0.1, 0.3, 1.0],
                           }

    def dialogue_box(self, participant=None, session=1, run_length=180, test_mode=False, meg=False, show_progress=True, show=True, ):
        ''' Show dialogue box to get participant info '''

        if participant is None:
            savefiles = glob.glob(f"{self.data_dir}{os.sep}*.txt")
            names = [0] + [int(os.path.basename(file)[:2])
                           for file in savefiles]
            participant = max(names)+1

        expName = "Alteration Magic School"
        expInfo = {"participant": str(participant).zfill(2),
                   "session": int(session),
                   "MEG": meg,
                   "runLength": run_length,
                   "testMode": test_mode,
                   "showProgress": show_progress,
                   "dateStr": data.getDateStr(format="%Y-%m-%d-%Hh%Mm"),
                   "psychopyVersion": __version__}

        # Dialogue Box
        if show:
            dlg = gui.DlgFromDict(dictionary=expInfo,
                                  sortKeys=False,
                                  title=expName,
                                  fixed=["dateStr", "psychopyVersion", "frameRate"])
            if not dlg.OK:
                core.quit()

        # Save data to this file later
        expInfo["expName"] = "AltMag"
        self.show_progress = expInfo["showProgress"]
        self.test_mode = expInfo["testMode"]
        self.run_length = expInfo["runLength"]
        self.meg = expInfo["MEG"]
        self.meta_fname = f"{self.data_dir}{os.sep}{expInfo['expName']}_id={expInfo['participant']}_start={expInfo['dateStr']}_metadata"
        for key in expInfo:
            self.add2meta(key, expInfo[key])
        self.expInfo = expInfo
        self.exp_clock = core.Clock()

        # Optionally init parallel port
        self.resp_keys = self.resp_keys_kb
        self.use_pp = False

        if expInfo["MEG"]:
            self.init_interface()
            self.use_pp = True
            self.resp_keys = self.resp_keys_vpixx

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
        self.add2meta("frameRate", self.win.getActualFrameRate())

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
        # self.trials_localizer = pickle.load(
        #     open(f"{self.trial_list_dir}{os.sep}{pid}_trials_localizer.pkl", "rb"))

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
        self.n_exposure = 30  # this value should match in GenerateTrialLists
        self.maxn_blocks = 4  # this value should match in GenerateTrialLists

        # Determine_positions
        self.rect_pos = circularGridPositions(
            center_pos=self.center_pos, set_size=self.set_size, radius=7)
        self.resp_pos = rectangularGridPositions(
            center_pos=[0, -10], h_dist=10, dim=(1, 4))
        self.resp_pos_num = rectangularGridPositions(
            center_pos=[0, -9.6], h_dist=10, dim=(1, 4))
        self.cuepractice_pos = rectangularGridPositions(
            center_pos=[0, -8], h_dist=8, dim=(1, self.n_cats))

    def render_visuals(self):
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
            image=glob.glob(f"{self.stim_dir}{os.sep}leftArrow.png")[0])

        self.magicWand = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}magicWand.png")[0])

        self.pauseClock = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}pauseClock.png")[0],
            pos=self.center_pos)

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
                f"{self.stim_dir}{os.sep}philbertine.png")[0])

        self.magicBooks = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}magicBooks.png")[0])

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
                image=keyboard_list[i])
            for i in range(len(keyboard_list))
        }

        print("Rendering cues...")
        # Text cues
        tcue_list = self.mappinglists["tcue"]
        assert len(tcue_list) >= 2*self.n_primitives
        vcue_list = self.mappinglists["vcue"]
        assert len(vcue_list) >= 2*self.n_primitives

        # # use latter half of cues for MEG-Session
        # if self.expInfo["session"] == "3":
        #     tcue_list = np.concatenate((tcue_list[self.n_primitives:],
        #                                 tcue_list[:self.n_primitives]))
        #     vcue_list = np.concatenate((vcue_list[self.n_primitives:],
        #                                 vcue_list[:self.n_primitives]))

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
                pos=self.center_pos)
            for i in range(self.n_primitives)
        }

        print("Rendering stimuli...")
        # Stimuli
        stim_list = self.mappinglists["stim"]
        assert len(stim_list) >= 2*self.n_cats, "Not enough stimuli"
        stim_names = ascii_uppercase[0:len(stim_list)]
        # if self.expInfo["session"] == "3":
        #     stim_names = stim_names[self.n_cats:] + stim_names[:self.n_cats]
        self.stim_dict = {
            stim_names[i]: visual.ImageStim(
                self.win,
                image=stim_list[i])
            for i in range(len(stim_list))
        }


    # Background Components --------------------------------------------------------
    def writeFileName(self, dataset_name):
        return  f"{self.data_dir}{os.sep}{self.expInfo['expName']}_id={self.expInfo['participant']}_start={self.expInfo['dateStr']}_data={dataset_name}"
    
    def add2meta(self, var, val):
        with open(f"{self.meta_fname}.csv", "a") as f:
            f.write(f"{var},{val}\n")
            
    def init_progbar(self, bar_len=None, bar_height=None):
        if bar_len is None:
            bar_len = self.win.size[0]
        if bar_height is None:
            bar_height = self.win.size[1]/64

        self.bar_len = bar_len  # total length
        self.bar_height = bar_height
        self.bar_pos = [0, self.win.size[1]/2 - bar_height/2]
        self.left_corner = self.bar_pos[0] - self.bar_len/2
        self.progBack = visual.Rect(
            self.win,
            units="pix",
            width=self.bar_len,
            height=self.bar_height,
            pos=self.bar_pos,
            fillColor=self.color_dict["light_grey"],
            autoDraw=True)
        self.progTest = visual.Rect(
            self.win,
            units="pix",
            width=0,
            height=self.bar_height,
            pos=self.bar_pos,
            fillColor=self.color_dict["green"],
            autoDraw=True)
        self.start_width = 0.0
        self.progbar_inc = 0.01  # 1% of bar length

    def move_prog_bar_step(self, bar_width_step, flip_win=True):
        # incrementally increase the bar width
        self.progTest.width += bar_width_step
        # re-center it accordingly on X-coordinate
        self.progTest.pos[0] = self.left_corner + self.progTest.width/2
        self.progTest.pos = self.progTest.pos.tolist()
        if flip_win:
            self.win.flip()

    def move_prog_bar(self, start_width=None, end_width=1.0,
                      n_steps=20, wait_s=0.75, flip_win=True):
        if start_width is None:
            start_width = self.start_width

        # Setup starting state of progress bar
        self.progTest.width = start_width * self.progBack.width
        self.progTest.pos[0] = self.left_corner + start_width *\
            self.progBack.width/2
        total_increment = (end_width - start_width) * self.progBack.width
        bar_width_step = total_increment/n_steps

        # First display
        if flip_win:
            self.win.flip()
            core.wait(wait_s)

        if end_width > start_width:
            # Growing
            while self.progTest.width < self.progBack.width * end_width:
                self.move_prog_bar_step(bar_width_step, flip_win=flip_win)
        else:
            # Waning
            while self.progTest.width > self.progBack.width * end_width:
                self.move_prog_bar_step(bar_width_step, flip_win=flip_win)

        # Last bit for completion
        self.move_prog_bar_step(
            self.progBack.width * end_width - self.progTest.width,
            flip_win=flip_win)
        if flip_win:
            core.wait(1.5 * wait_s)
        self.start_width = self.progTest.width / self.progBack.width


    ###########################################################################
    # Instructions
    ###########################################################################
    
    def iSingleImage(self, *args):
        for arg in args:
            arg.pos = [0, 0]
            # arg.size = [10, 10]
            arg.draw()
            self.win.flip()
            core.wait(0.2)

    def iTransmutableObjects(self, *args,):
        categories = list(self.stim_dict.keys())
        categories.sort()
        n_cats = self.n_cats  # alternatively show all using len(categories)
        if n_cats > 4:
            dim = [2, np.ceil(n_cats/2)]
        else:
            dim = [1, n_cats]

        category_pos = rectangularGridPositions(
            center_pos=[0, 0], h_dist=10, dim=dim)

        # draw categories
        for i in range(n_cats):
            self.rect.pos = category_pos[i]
            self.rect.draw()
            stim = self.stim_dict.copy()[categories[i]]
            stim.pos = category_pos[i]
            stim.draw()
        self.win.flip()

    def iSpellExample(self, displays):
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
                self.win.flip()
                core.wait(1)
                continue

            cue = self.magicWand
            cue.draw()
            if i == 1:
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
            self.win.flip()
            core.wait(1)
    
    def iNavigate(self, page=0, max_page=99, continue_after_last_page=True,
                  proceed_key="/k", wait_s=3):

        assert proceed_key in ["/k", "/m", "/t", "/e"], "Unkown proceed key"
        left = "a"
        right = "ö"
        finished = False
        testResp = None
        TestClock = core.Clock()

        # get response or wait or something in between
        if proceed_key == "/k":  # keypress
            _, testResp = self.tTestResponse(
                TestClock, [left, right],
                return_numeric=False)
        if proceed_key == "/m":  # meg keypress
            _, testResp = self.tTestResponse(
                TestClock, self.resp_keys_vpixx[-2:],
                return_numeric=False)
        elif proceed_key == "/t":  # time
            core.wait(wait_s)
            testResp = "right"
        elif proceed_key == "/e":  # either
            _, testResp = self.tTestResponse(
                TestClock, [left, right],
                return_numeric=False,
                max_wait=wait_s)
            if testResp is None:
                testResp = right

        # Proceed accordingly
        if testResp in [right, self.resp_keys_vpixx[-1]]:
            if page < max_page-1:
                page += 1
            elif continue_after_last_page:
                finished = True
            else:
                self.nextPrompt.draw()
                self.win.flip()
                _, contResp = self.tTestResponse(TestClock, [left, right],
                                                 return_numeric=False)
                if contResp == right:
                    finished = True
        elif testResp in [left, self.resp_keys_vpixx[-2]] and page > 0:
            page -= 1

        return page, finished
    
    def Instructions(self, part_key="Intro",
                     special_displays=list(),
                     args=list(),
                     complex_displays=list(),
                     kwargs=list(),
                     font="Times New Roman",
                     fontcolor=[-0.9, -0.9, -0.9],
                     log_duration=True,
                     loading_time=1):
        assert part_key in self.instructions.keys(),\
            "No instructions provided for this part"

        self.instruct_stim.font = font
        self.instruct_stim.color = fontcolor

        # Initialize parameters
        finished = False
        Part = self.instructions[part_key]
        page = 0
        self.win.flip()
        self.win.flip()
        if log_duration:
            instructions_clock = core.Clock()
        while not finished:
            page_content, proceed_key, proceed_wait = Part[page]
            if isinstance(page_content, str):
                self.instruct_stim.text = page_content
                self.instruct_stim.draw()
                self.win.flip()
            elif isinstance(page_content, int):
                special_displays[page_content](
                    args[page_content])
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
            self.add2meta(f"duration_{part_key}", duration)
        self.win.flip()
        core.wait(loading_time)

    
    ###########################################################################
    # Cues
    ###########################################################################

    def learnCues(self, cue_center_pos=[0, 2], vert_dist=7,
                  modes=["textual", "visual"]):
        ''' Interactive display for learning cues for all maps, return viewing duration '''
        
        # Init
        self.win.flip()
        finished = False
        cat_center_pos = [0, cue_center_pos[1] - vert_dist]
        page = 0
        category_pos = rectangularGridPositions(
            center_pos=cat_center_pos, h_dist=15, dim=(1, 2))
        stimuli = self.stim_dict.copy()
        learn_clock = core.Clock()

        while not finished:
            # Draw map cue
            map_name = self.map_names[page]
            categories = map_name.split("-")

            for j, mode in enumerate(modes):
                cue, _ = self.setCue(map_name, mode=mode)
                cue.pos = [sum(x) for x in
                           zip(cue_center_pos, [0, (1-j)*vert_dist])]
                cue.draw()

            # Draw corresponding explicit map
            for i, category in enumerate(categories):
                self.rect.pos = category_pos[i]
                self.rect.draw()
                cat = stimuli[category]
                cat.pos = category_pos[i]
                cat.draw()
            self.leftArrow.pos = cat_center_pos
            self.leftArrow.draw()
            self.win.flip()
            core.wait(0.2)

            page, finished = self.iNavigate(
                page=page, max_page=self.n_primitives,
                continue_after_last_page=False)

        return learn_clock.getTime()

    def drawResponseOptions(self, stimuli, resp_options):
        ''' Draw the response options on the screen'''
        self.rect.lineColor = self.color_dict["dark_grey"]
        for i, pos in enumerate(self.cuepractice_pos):
                self.rect.pos = pos
                self.rect.draw()
                resp = stimuli[resp_options[i]]
                resp.pos = pos
                resp.draw()
        self.win.flip(clearBuffer=False)
    
    def redrawAfterResponse(self, stimulus, rectPos=(0,0), stimPos=None, isCorrect=False, isQuick=False):
        ''' Redraw the stimulus after a response has been made and indicate performance via color '''
        if stimPos is None:
            stimPos = rectPos
        
        # set informative border color
        if not isCorrect:
            lc = self.color_dict["red"]
        elif not isQuick:
            lc = self.color_dict["yellow"]
        else:
            lc = self.color_dict["green"]
                    
        # redraw rectangle
        self.rect.lineColor = lc
        self.rect.pos = rectPos
        self.rect.draw()
        self.rect.lineColor = self.color_dict["dark_grey"] #reset
        stimulus.pos = stimPos
        stimulus.draw()
        self.win.flip(clearBuffer=False)
        
    def redrawFeedback(self, stimulus, rectPos=(0,0), stimPos=None):
        ''' Mark the correct response option as feedback '''
        if stimPos is None:
            stimPos = rectPos
        core.wait(1)
        self.rect.pos = rectPos
        self.rect.lineColor = self.color_dict["dark_blue"]
        self.rect.fillColor = self.color_dict["blue"]
        self.rect.draw()
        self.rect.lineColor = self.color_dict["dark_grey"] #reset
        self.rect.fillColor = self.color_dict["light_grey"] #reset
        stimulus.pos = stimPos
        stimulus.draw()
        self.win.flip(clearBuffer=False)
        
    def cuePracticeTrial(self, trial, mode="random", cue_pos=(0, 5), goal_rt=2.0):
        ''' Subroutine for the cue practice trials'''
        # Init
        stimuli = self.stim_dict.copy()
        testResp = ""
        testRespList = []
        testRTList = []
        trial["start_time"] = self.exp_clock.getTime()
        
        # Fixation Cross
        self.drawFixation()
        self.win.flip()
        
        # Map Cue and Response Options
        cue, cue_type = self.setCue(trial.map[0], mode=mode)
        cue.pos = cue_pos
        cue.draw()
        self.drawResponseOptions(stimuli, trial.resp_options)
        
        # Wait for response(s)
        for correctResp in trial.correct_resp:
            if testResp == "NA":
                continue
            testRT, testResp = self.tTestResponse(core.Clock(), self.resp_keys)
            testRTList.append(testRT)
            testRespList.append(testResp)
            self.redrawAfterResponse(stimuli[trial.resp_options[testResp]],
                                     rectPos=self.cuepractice_pos[testResp],
                                     isCorrect=correctResp == testResp,
                                     isQuick=sum(testRTList) <= goal_rt)
        
        # Feedback (if incorrect)
        if trial.correct_resp != testRespList:
            for correctResp in trial.correct_resp:
                self.redrawFeedback(stimuli[trial.resp_options[correctResp]],
                                    rectPos=self.cuepractice_pos[correctResp])
        
        # Save data and clear screen
        trial["emp_resp"] = testRespList
        trial["resp_RT"] = testRTList
        trial["cue_type"] = cue_type
        self.win.flip()
        core.wait(2)
    
    def allMapsLearned(self, streak_goal=5):
        ''' Evaluates the counter dict for the adaptive cue practice'''
        for _map in self.map_names:
            if self.counter_dict[_map] < streak_goal:
                return False
        return True 
    
    def updateCounterDict(self, trial, goal_rt=2.0):
        ''' Updates the counter dict for the adaptive cue practice:
            - reset counter if incorrect response
            - increase counter if quick correct response
        '''
        if trial.correct_resp != trial.emp_resp: 
            self.counter_dict[trial.map[0]] = 0
        elif sum(trial.resp_RT) <= goal_rt:
            self.counter_dict[trial.map[0]] += 1
        # print(f"Map: {trial.map[0]}, Counter: {self.counter_dict[trial.map[0]]}, RTs: {trial.resp_RT}")
    
    def adaptiveCuePractice(self, trials_prim_cue, streak_goal=5, goal_rt=2.0, mode="random"):
        ''' Practice cues until for each map the last streak_goal trials are correct and below the goal_rt'''
        self.counter_dict = {map:0 for map in self.map_names}
        start_width_initial = self.start_width # progbar
        trials = data.TrialHandler(trials_prim_cue, 1, method="sequential")
        out = []
        
        while not self.allMapsLearned(streak_goal=streak_goal) and not trials.finished:
            trial = trials.next()
            self.cuePracticeTrial(trial, mode=mode, goal_rt=goal_rt)
            self.updateCounterDict(trial, goal_rt=goal_rt)
            out.append(trial)
            
            if self.show_progress:
                end_width = start_width_initial + sum(self.counter_dict.values()) * self.progbar_inc
                self.move_prog_bar(end_width=end_width, wait_s=0)
                
        return out
    
    
    ###########################################################################
    # Normal Trials (methods prefaced with "t" may require response)
    ###########################################################################
    
    def drawFixation(self, duration=0.3):
        ''' draw fixation cross'''
        self.fixation.draw()
        self.win.flip()
        if self.use_pp:
            self.send_trigger("fix")
        core.wait(duration)

    def setCue(self, key, mode="random"):
        ''' return cue stimulus for a given mode'''
        # opt: randomize mode
        if mode == "random":
            mode = np.random.choice(["visual", "textual"])
        
        # draw from resp. dict
        if mode == "visual":
            cue = self.vcue_dict.copy()[key]
        elif mode == "textual":
            cue = self.tcue_dict.copy()[key]
        else:
            raise ValueError("Chosen cue mode not implemented.")
        return cue, mode

    def drawCue(self, trial, mode="random", duration=0.5):
        ''' draw cue(s) for a given trial, return the mode'''
        assert mode in ["visual", "textual", "random"],\
            "Chosen cue mode not implemented."
        n_cues = len(trial.map)
        
        # draw each cue
        for i, _map in enumerate(trial.map):
            cue, mode = self.setCue(_map, mode=mode)
            cue.pos = self.center_pos if n_cues == 1 else [sum(x) for x in zip(self.center_pos, [0, (1-i)*6])]
            cue.draw()
        
        # send triggers            
        if self.use_pp:
            self.send_trigger("vcue") if mode == "visual" else self.send_trigger("tcue")
        
        # flip
        self.win.flip()
        core.wait(duration)
        return mode

    def tIndermediateResponse(self, IRClock, min_wait=0.1, max_wait=10.0):
        ''' wait for intermediate response and return RT'''
        core.wait(min_wait)
        while True:
            pressed = event.waitKeys(timeStamped=IRClock, maxWait=max_wait)            
            
            # case: intermediate response is timed but no response is given, yet
            if pressed is None:
                intermediateRT = max_wait
                break
            else:
                thisKey, intermediateRT = pressed[0]      
            
            # case: valid response
            if thisKey == "space":
                break
                
            # case: abort
            elif thisKey == "escape":
                self.add2meta("t_abort", data.getDateStr())
                core.quit()  # abort experiment
        
        return intermediateRT

    def tTestResponse(self, TestClock, respKeys,
                      return_numeric=True, max_wait=np.inf):
        ''' wait for test response in respKeys and return RT and response'''
        testResp, testRT, pressed = None, None, None
        while testResp is None:
            pressed = event.waitKeys(timeStamped=TestClock, maxWait=max_wait)
            
            # case: tTestResponse is timed but no response is given, yet 
            if max_wait < np.inf and pressed is None:
                break
            else:
                thisKey, testRT = pressed[0]
                
                # case: valid response
                if thisKey in respKeys:
                    testResp = respKeys.index(thisKey) if return_numeric else thisKey
                # case: don't know
                elif thisKey == "space":
                    testResp = "NA"
                # case: abort
                elif thisKey == "escape":
                    self.add2meta("t_abort", data.getDateStr())
                    core.quit()  # abort experiment
                    
        return testRT, testResp
    
    def tInput(self, trial, duration=1, self_paced=False):
        ''' draw input stimuli and wait for response if self_paced'''
        # Init
        stimuli = self.stim_dict.copy()
        
        # draw rectangles
        self.rect.size = self.normal_size
        for pos in self.rect_pos:
            self.rect.pos = pos
            self.rect.draw()

        # draw stimuli
        for i in range(self.set_size):
            stim_name = trial.input_disp[i]
            if stim_name is not None:
                stim = stimuli[stim_name]
                stim.pos = self.rect_pos[i]
                stim.draw()
        
        # send trigger
        if self.use_pp:
            self.send_trigger("disp")

        # flip
        self.win.flip()
        if self_paced:
            intermediateRT = self.tIndermediateResponse(core.Clock())
        else:
            core.wait(duration)
            intermediateRT = duration
        return intermediateRT
    
    def tEmptySquares(self, IRClock):
        ''' draw empty squares and wait for response'''
        for pos in self.rect_pos:
            self.rect.pos = pos
            self.rect.draw()
        self.win.flip()
        intermediateRT = self.tIndermediateResponse(IRClock)
        return intermediateRT

    def tPause(self):
        ''' draw pause screen and wait for response'''
        self.pauseClock.draw()
        self.pauseText.draw()
        self.win.flip()
        intermediateRT = self.tIndermediateResponse(core.Clock(), max_wait=360)  # max 6 min break
        self.win.flip()
        core.wait(1)   
        if self.use_pp:
            self.send_trigger("run")
        return intermediateRT

    def drawCountTarget(self, stimulus):
        ''' draw target stimulus for count test'''
        self.rect.pos = self.center_pos
        self.rect.size = self.center_size
        self.rect.draw()
        self.rect.size = self.normal_size #reset size
        stimulus.pos = self.center_pos
        stimulus.draw()
        self.win.flip(clearBuffer=False)
    
    def drawCountResponses(self):
        ''' draw response options for count test'''
        self.rect.lineColor = self.color_dict["dark_grey"]
        for i, pos in enumerate(self.resp_pos):
            self.rect.pos = pos
            self.rect.draw()
            resp = self.count_dict[str(i)]
            resp.pos = self.resp_pos_num[i]
            resp.draw()
        self.win.flip(clearBuffer=False)
    
    def tCount(self, trial, feedback=False, demonstration=False):
        ''' wrapper for count test'''
        # Init
        stimuli = self.stim_dict.copy()
        corResp = trial.correct_resp
        
        # Draw stimuli
        self.drawCountTarget(stimuli[trial.target])
        self.drawCountResponses()
        
        # Send trigger    
        if self.use_pp:
            self.send_trigger("count")
        
        # Get response
        if not demonstration:
            testRT, testResp = self.tTestResponse(core.Clock(), self.resp_keys)
        else:
            # simulate incorrect response
            badoptions = np.array(range(4))
            badoptions = np.delete(badoptions, corResp)
            core.wait(1)
            testRT, testResp = 0, badoptions[0]

        # Feedback
        if feedback:
            # immediate
            self.redrawAfterResponse(self.count_dict[str(testResp)], 
                                     rectPos=self.resp_pos[testResp],
                                     stimPos=self.resp_pos_num[testResp],
                                     isCorrect=corResp == testResp,
                                     isQuick=True)
            # correct solution
            if corResp != testResp:
                self.redrawFeedback(self.count_dict[str(corResp)], 
                                    rectPos=self.resp_pos[corResp],
                                    stimPos=self.resp_pos_num[corResp])
        
        # Clear screen
        self.win.flip()
        core.wait(1)
        return testRT, testResp        

    def drawPositionTarget(self, target_idx):
        ''' draw target stimulus for position test'''
        for i, pos in enumerate(self.rect_pos):
            self.rect.pos = pos
            self.rect.draw()
            if target_idx == i:
                self.qm.pos = pos
                self.qm.draw()
        self.win.flip(clearBuffer=False)
    
    def drawPositionResponses(self, stimuli, resp_options):
        ''' draw response options for position test'''
        for i, pos in enumerate(self.resp_pos):
            self.rect.pos = pos
            self.rect.draw()
            resp = stimuli[resp_options[i]]
            resp.pos = pos
            resp.draw()
        self.win.flip(clearBuffer=False)
    
    def tPosition(self, trial, feedback=False, demonstration=False):
        ''' wrapper for position test'''
        # Init
        stimuli = self.stim_dict.copy()
        corResp = trial.correct_resp

        # Draw stimuli
        self.drawPositionTarget(trial.target)
        self.drawPositionResponses(stimuli, trial.resp_options)
        
        # Send trigger
        if self.use_pp:
            self.send_trigger("position")
        
        # Get response
        if not demonstration:
            testRT, testResp = self.tTestResponse(core.Clock(), self.resp_keys)
        else:
            # simulate incorrect response
            badoptions = np.array(range(4))
            badoptions = np.delete(badoptions, corResp)
            core.wait(1)
            testRT, testResp = 0, badoptions[0]
        
        # Feedback
        if feedback:
            # immediate
            self.redrawAfterResponse(stimuli[trial.resp_options[testResp]], 
                                     rectPos=self.resp_pos[testResp],
                                     isCorrect=corResp == testResp,
                                     isQuick=True)
            # correct solution
            
            if corResp != testResp:
                self.redrawFeedback(stimuli[trial.resp_options[corResp]], 
                                    rectPos=self.resp_pos[corResp])
        
        # Clear screen
        self.win.flip()
        core.wait(1)
        return testRT, testResp        
    
    def genericTrial(self, trial, mode="random", self_paced=True, feedback=True,
                     fixation_duration=0.3, cue_duration=1.0):
        ''' subroutine for generic trials'''
        # Init
        self.win.flip()
        trial["start_time"] = self.exp_clock.getTime()
        
        # Send trigger
        if self.use_pp:
            self.send_trigger("trial_start")
        
        # Fixation
        self.drawFixation(duration=fixation_duration)
            
        # Display input
        display_rt = self.tInput(trial, self_paced=self_paced)

        # Cue
        self.drawFixation()
        mode = self.drawCue(trial, mode=mode, duration=cue_duration)
        
        # Transformation display
        inter_rt = self.tEmptySquares(core.Clock())
        
        # Empty display
        self.win.flip()
        core.wait(1)
        
        # Test display
        testMethod = self.tCount if trial.test_type == "count" else self.tPosition
        test_rt, test_resp = testMethod(trial, feedback=feedback)
        
        # Save data
        trial["display_RT"] = display_rt
        trial["inter_RT"] = inter_rt
        trial["resp_RT"] = test_rt
        trial["emp_resp"] = test_resp
        trial["cue_type"] = mode
        core.wait(1)

    def updateStreak(self, streak, isCorrect):
        ''' update streak counter and progress bar during generic blocks'''
        modifier = 1 if isCorrect else -1
        streak += modifier
        if self.show_progress:
            end_width = self.start_width + modifier * self.progbar_inc
            self.move_prog_bar(end_width=end_width, wait_s=0)
        return streak
    
    def genericBlock(self, trial_df, streak_goal=30, mode="random",
                     fixation_duration=0.3, cue_duration=1.0,
                     self_paced=True, feedback=True, pause_between_runs=True):
        ''' generic block of trials, with streak goal and pause between runs'''
        # Init
        streak = 0
        trials = data.TrialHandler(trial_df, 1, method="sequential")
        out = []
        if pause_between_runs:
            run_number = 1
            timer = core.CountdownTimer(self.run_length)
            if self.use_pp:
                self.send_trigger("run")      
        
        # Run trials until goal is reached
        while streak < streak_goal and not trials.finished:
            trial = trials.next()
            self.genericTrial(trial, mode=mode, self_paced=self_paced, feedback=feedback,
                              fixation_duration=fixation_duration + trial.jitter[0],
                              cue_duration=cue_duration + trial.jitter[1])
            streak = self.updateStreak(streak, trial.correct_resp == trial.emp_resp)
            
            # Pause display between runs
            if pause_between_runs and timer.getTime() <= 0:
                self.tPause()
                timer.reset()
                trial["run_number"] = run_number
                run_number += 1

            out.append(trial)
        return out
                
     
        
    
    # def GenericBlock(self, trial_df, mode="random", i=0, i_step=None,
    #                  self_paced=False, display_this=[1, 2, 3, 4, 5, 6, 7],
    #                  durations=[1.0, 3.0, 0.6, 1.0, 0.7],
    #                  test=True, feedback=False,
    #                  pause_between_runs=True,
    #                  instruction_trial=False):

    #     # create the trial handler and optionally timer
    #     if i_step is None:
    #         i_step = len(trial_df) // self.maxn_blocks
    #     df = trial_df[i:i+i_step].copy()
    #     trials = data.TrialHandler(
    #         df, 1, method="sequential")

    #     # prepare progress bar
    #     n_trials = len(trials.trialList)
    #     trial_number = 1
    #     start_width_initial = self.start_width

    #     if pause_between_runs:
    #         run_number = 1
    #         timer = core.CountdownTimer(self.run_length)
    #         if self.use_pp:
    #             self.send_trigger("run")

    #     # check if jitter is specified
    #     if "jitter" in trials.trialList[0]:
    #         add_jitter = True
    #     else:
    #         jitter = [0.0, 0.0, 0.0]
    #         add_jitter = False

    #     for trial in trials:
    #         if add_jitter:
    #             jitter = trial.jitter
    #         self.win.flip()
    #         trial["start_time"] = self.exp_clock.getTime()
    #         if self.use_pp:
    #             self.send_trigger("trial")

    #         # 1. Fixation
    #         if 1 in display_this:
    #             self.drawFixation(jitter=jitter[0])

    #         # 2. Display Family
    #         if 2 in display_this:
    #             displayRT = self.tInput(trial, 
    #                                     duration=durations[1] + jitter[1],
    #                                     self_paced=self_paced)

    #         # 3. Map Cue
    #         if 3 in display_this:
    #             self.drawFixation()
    #             cue_type = self.drawCue(trial, mode=mode,
    #                                     duration=durations[0] + jitter[2])

    #         if test:
    #             # 4. Transformation Display
    #             if 4 in display_this:
    #                 intermediateRT = self.tEmptySquares(core.Clock())

    #             # 5. Empty Display
    #             if 5 in display_this:
    #                 self.win.flip()
    #                 core.wait(durations[2])

    #             # 6. Test Display
    #             if 6 in display_this:
    #                 if trial.test_type == "count":
    #                     testRT, testResp = self.tCount(
    #                         trial, feedback=feedback)
    #                 elif trial.test_type == "position":
    #                     testRT, testResp = self.tPosition(
    #                         trial, feedback=feedback)

    #                 # Save data
    #                 trial["run_number"] = run_number
    #                 trial["display_RT"] = displayRT
    #                 trial["inter_RT"] = intermediateRT
    #                 trial["emp_resp"] = testResp
    #                 trial["resp_RT"] = testRT
    #                 trial["cue_type"] = cue_type
    #                 core.wait(durations[3])

    #         if self.show_progress and not instruction_trial:
    #             self.move_prog_bar(
    #                 end_width=self.start_width + self.progbar_inc, wait_s=0)

    #         if 7 in display_this:
    #             self.win.flip()
    #             self.win.flip()
    #             core.wait(durations[4])

    #         if pause_between_runs:
    #             if timer.getTime() <= 0:
    #                 # Pause Display
    #                 self.tPause()
    #                 core.wait(1)
    #                 timer.reset()
    #                 run_number += 1
    #                 if self.use_pp:
    #                     self.send_trigger("run")

    #         trial_number += 1
    #     return trials.trialList
    
    def TestPracticeLoop(self, trial_df,
                         min_acc=0.95,
                         mode="random",
                         i=0,
                         i_step=None,
                         durations=[1.0, 3.0, 0.6, 1.0, 0.7],
                         test=True,
                         feedback=False,
                         self_paced=False,
                         pause_between_runs=True):
        mean_acc = 0.0
        df_list = []
        if i_step is None:
            i_step = len(trial_df)//self.maxn_blocks
        while mean_acc < min_acc:
            start_width_initial = self.start_width
            result = self.GenericBlock(trial_df, mode=mode, i=i, i_step=i_step,
                                       durations=durations, test=test, feedback=feedback,
                                       self_paced=self_paced,
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
            i += i_step if i < len(trial_df) else 0
            if mean_acc < min_acc:
                feedbacktype = "Feedback0Test"
            else:
                feedbacktype = "Feedback1"
            self.Instructions(part_key=feedbacktype,
                              special_displays=[self.iSingleImage],
                              args=[accPrompt])
            if mean_acc < min_acc:
                # reset progress bar
                self.move_prog_bar(end_width=start_width_initial)
        df_out = [item for sublist in df_list for item in sublist]
        return df_out

        
    ###########################################################################
    # Introduction Session
    ###########################################################################

    def Session1(self):
        # init session variables
        self.win.mouseVisible = False
        min_acc = 0.9

        # number of trials: 2 * cue practice, 2 * test practice (based on i_step)
        n_trials_total = (len(self.trials_prim_cue) +
                          len(self.trials_prim_prac_p) +
                          len(self.trials_prim_prac_c)) // self.maxn_blocks
        self.progbar_inc = 1/n_trials_total

        # Balance out which cue modality is learned first
        id_is_odd = int(self.expInfo["participant"]) % 2
        first_modality = "visual" if id_is_odd else "textual"
        second_modality = "textual" if id_is_odd else "visual"

        # Balance out which test type is learned first
        first_test = "count" if id_is_odd else "position"
        second_test = "position" if id_is_odd else "count"
        tFirst = self.tCount if id_is_odd else self.tPosition
        tSecond = self.tPosition if id_is_odd else self.tCount
        trials_test_1 = self.trials_prim_prac_c.copy(
        ) if id_is_odd else self.trials_prim_prac_p.copy()
        trials_test_2 = self.trials_prim_prac_p.copy(
        ) if id_is_odd else self.trials_prim_prac_c.copy()

        # Get Demo trials
        demoTrials1 = data.TrialHandler(trials_test_1[:1], 1, method="sequential")
        demoTrials2 = data.TrialHandler(trials_test_2[:1], 1, method="sequential")
        demoTrial1, demoTrial2 = demoTrials1.trialList[0], demoTrials2.trialList[0]
        print("Starting Session 1.")

        ''' --- 1. Initial instructions ---------------------------------------------'''
        # Navigation
        self.Instructions(part_key="Navigation1",
                          special_displays=[self.iSingleImage,
                                            self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardArrows"],
                                self.keyboard_dict["keyBoardEsc"]],
                          font="mono",
                          fontcolor=self.color_dict["mid_grey"])

        # Introduction
        self.Instructions(part_key="Intro",
                          special_displays=[self.iSingleImage,
                                            self.iSingleImage,
                                            self.iSingleImage,
                                            self.iTransmutableObjects,
                                            self.iSpellExample,
                                            self.iSpellExample],
                          args=[self.magicWand,
                                self.magicBooks,
                                self.philbertine,
                                None,
                                [["A", "B", "C", "D"], ["A", "D", "C", "D"]],
                                [["A", "B", "B", "D"], ["A", "D", "D", "D"]]])

        ''' --- 2. Learn Cues --------------------------------------------------------'''
        # Learn first cue type
        self.learnDuration_1 = self.learnCues()
        self.add2meta("learnDuration_1", self.learnDuration_1)

        # Test first cue type
        self.Instructions(part_key="Intermezzo1",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoard4"]])
        self.df_out_1 = self.adaptiveCuePractice(self.trials_prim_cue,
                                                 streak_goal=1 if self.test_mode else 5,
                                                 mode=first_modality)
                                             

        # Learn second cue type
        self.Instructions(part_key="Intermezzo2",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoard4"]])
        self.learnDuration_2 = self.learnCues()
        self.add2meta("learnDuration_2", self.learnDuration_2)
        

        # Test second cue type
        self.df_out_2 = self.adaptiveCuePractice(self.trials_prim_cue[len(self.df_out_1):],
                                                 streak_goal=1 if self.test_mode else 5,
                                                 mode=second_modality)

        # Save cue memory data
        fname = self.writeFileName("cueMemory")
        save_object(self.df_out_1 + self.df_out_2, fname, ending='csv')

        ''' --- 3. Test Types --------------------------------------------------------'''
        # First Test-Type
        self.Instructions(part_key="TestTypes",
                          special_displays=[self.iSingleImage],
                          args=[self.magicWand],
                          complex_displays=[self.GenericBlock],
                          kwargs=[{"trial_df": self.trials_prim_prac_p,
                                   "durations": [1, 3, 0.6, 0, 0],
                                   "i_step": 1,
                                   "instruction_trial": True,
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
                                   "instruction_trial": True,
                                   "test": False},
                                  {"trial_df": trials_test_1,
                                   "display_this": [3, 4],
                                   "durations": [0, 0, 0, 0, 0],
                                   "i_step": 1,
                                   "instruction_trial": True,
                                   "test": False},
                                  {"trial": demoTrial1,
                                   "feedback": False,
                                   "demonstration": True},
                                  {"trial": demoTrial1,
                                   "feedback": True,
                                   "demonstration": True}])

        self.df_out_3 = self.TestPracticeLoop(trials_test_1,
                                              i_step=2 if self.test_mode else None,
                                              min_acc=min_acc,
                                              self_paced=True,
                                              feedback=True,
                                              pause_between_runs=True)

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
                                   "instruction_trial": True,
                                   "test": False},
                                  {"trial": demoTrial2,
                                   "feedback": False,
                                   "demonstration": True},
                                  {"trial": demoTrial2,
                                   "feedback": True,
                                   "demonstration": True}])

        self.df_out_4 = self.TestPracticeLoop(trials_test_2,
                                              i_step=2 if self.test_mode else None,
                                              min_acc=min_acc,
                                              self_paced=True,
                                              feedback=True,
                                              pause_between_runs=True)

        # Save test type data
        fname = self.writeFileName("testPractice")
        save_object(self.df_out_3 + self.df_out_4, fname, ending='csv')

        # Wrap up
        self.move_prog_bar(end_width=1, n_steps=50, wait_s=0)
        self.Instructions(part_key="Bye")
        self.add2meta("t_end", data.getDateStr())
        self.win.close()

    # ###########################################################################
    #  Testing Session
    # ###########################################################################
    def Session2(self):
        # init session variables
        self.win.mouseVisible = False
        min_acc = 0.9
        n_trials_total = (len(self.trials_prim_dec) +
                          len(self.trials_prim_MEG) +
                          len(self.trials_bin_MEG)) // self.maxn_blocks
        self.progbar_inc = 1/n_trials_total

        demoCounts = data.TrialHandler(self.trials_prim_prac_c[0:1], 1, method="sequential")
        demoPositions = data.TrialHandler(self.trials_prim_prac_p[0:1], 1, method="sequential")
        demoCount, demoPosition = demoCounts.trialList[0], demoPositions.trialList[0]

        ''' --- 1. Initial instructions and function decoder ------------------------'''
        # Navigation
        self.Instructions(part_key="Navigation3",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMegBF"] if self.meg else self.keyboard_dict["keyBoardArrows"]],
                          font="mono",
                          fontcolor=self.color_dict["mid_grey"])

        # Introduction & Function Decoder
        self.Instructions(part_key="IntroMEG",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]])

        self.df_out_5 = self.TestPracticeLoop(self.trials_prim_dec,
                                              i_step=2 if self.test_mode else None,
                                              min_acc=min_acc,
                                              test=True,
                                              feedback=True,
                                              self_paced=True)
        fname = self.writeFileName("functionDecoder")
        save_object(self.df_out_5, fname, ending='csv')

        ''' --- 2. Primitive trials ------------------------------------------------'''
        self.Instructions(part_key="PrimitivesMEGR",
                          special_displays=[self.iSingleImage,
                                            self.iSingleImage],
                          args=[self.magicWand,
                                self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]],
                          complex_displays=[self.GenericBlock,
                                            self.GenericBlock,
                                            self.GenericBlock,
                                            self.tCount,
                                            self.tPosition],
                          kwargs=[{"trial_df": self.trials_prim_prac_c,
                                   "display_this": [2],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "instruction_trial": True,
                                   "test": False},
                                  {"trial_df": self.trials_prim_prac_c,
                                   "display_this": [3, 7],
                                   "durations": [1.0, 0.0, 0.0, 0.0, 0.0],
                                   "i_step": 1,
                                   "instruction_trial": True,
                                   "test": False},
                                  {"trial_df": self.trials_prim_prac_c,
                                   "display_this": [4],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                   "instruction_trial": True,
                                   "i_step": 1,
                                   "test": True},
                                  {"trial": demoCount,
                                   "feedback": False,
                                   "demonstration": True},
                                  {"trial": demoPosition,
                                   "feedback": False,
                                   "demonstration": True}])

        self.df_out_6 = self.TestPracticeLoop(self.trials_prim_MEG,
                                              i_step=2 if self.test_mode else None,
                                              min_acc=min_acc,
                                              durations=[1.0, 3.0, 0.6, 1.0, 0.7],
                                              self_paced=True,
                                              pause_between_runs=True)
        fname = self.writeFileName("primitiveTrials")
        save_object(self.df_out_6, fname, ending='csv')
        
        ''' --- 3. Binary trials ------------------------------------------------'''
        self.Instructions(part_key="BinariesMEGR",
                          special_displays=[self.iSingleImage,
                                            self.iSingleImage],
                          args=[self.magicWand,
                                self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]],
                          complex_displays=[self.GenericBlock,
                                            self.GenericBlock,
                                            self.GenericBlock],
                          kwargs=[{"trial_df": self.trials_bin_MEG,
                                   "display_this": [2],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                   "instruction_trial": True,
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_bin_MEG,
                                   "display_this": [3, 7],
                                   "durations": [1.0, 0.0, 0.0, 0.0, 0.0],
                                   "instruction_trial": True,
                                   "i_step": 1,
                                   "test": False},
                                  {"trial_df": self.trials_bin_MEG,
                                   "display_this": [4],
                                   "durations": [0.0, 0.0, 0.0, 0.0, 0.0],
                                   "instruction_trial": True,
                                   "i_step": 1,
                                   "test": True}])
        self.df_out_7 = self.TestPracticeLoop(self.trials_bin_MEG,
                                               i_step=2 if self.test_mode else None,
                                               min_acc=0.75,
                                               durations=[1.5, 3.0, 0.6, 1.0, 0.7],
                                               self_paced=True,
                                               feedback=True,
                                               pause_between_runs=True)

        # Finalization
        fname = self.writeFileName("compositionalTrials")
        save_object(self.df_out_7, fname, ending='csv')
        self.move_prog_bar(end_width=1, n_steps=50, wait_s=0)
        self.Instructions(part_key="ByeBye")
        self.add2meta("t_end", data.getDateStr())
        self.win.close()


# =============================================================================
# Helper Functions
# =============================================================================

# Positions -------------------------------------------------------------------
def rectangularGridPositions(center_pos=[0, 0],
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
    c = np.round(dim[0]/2)
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
