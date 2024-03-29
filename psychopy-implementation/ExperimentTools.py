#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Methods for running the compositional inference experiment
"""
print("Loading psychopy...")
from psychopy.parallel import ParallelPort
from psychopy import __version__, core, event, visual, gui, data, monitors
import os
import glob
import inspect
import pickle
import copy
import sys
import csv
from string import ascii_uppercase
import numpy as np


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
        self.instruction_mode = False # indicates if currently instructions are shown

        # data dir
        self.data_dir = os.path.join(self.main_dir, "data")
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # inputs and dimensions
        self.resp_keys_kb = ["d", "f", "j", "k", "a", "ö"]
        self.resp_keys_vpixx = ["2", "1", "up", "left", "4", "right"]
        # Buttons: lMiddlefinger, lIndex, rIndex, rMiddlefinger, lThumb, rThumb
        # Mapping: 0, 1, 2, 3, False/left, True/right

        self.center_pos = [0, 5]
        self.double_cue_positions_visual = [[0, 8], [0, 2]]
        self.double_cue_positions_textual = [[0, 7], [0, 3]]
        self.center_size = [8, 8]
        self.normal_size = [5, 5]
        self.color_dict = {"superwhite" : [1.0, 1.0, 1.0],
                           "white": [0.9, 0.9, 0.9],
                           "instructions": [0.8, 0.8, 0.8],
                           "light_grey": [0.7, 0.7, 0.7],
                           "light_grey2": [0.6, 0.6, 0.6],
                           "mid_grey": [0.0, 0.0, 0.0],
                           "dark_grey": [-0.6, -0.6, -0.6],
                           "black": [-0.9, -0.9, -0.9],
                           "red": [0.8, 0.0, 0.0],
                           "yellow": [1.0, 0.8, 0.0],
                           "dark_yellow": [0.8, 0.6, 0.0],
                           "green": [0.0, 0.6, 0.0],
                           "blue": [0.2, 0.6, 1.0],
                           "dark_blue": [0.1, 0.3, 1.0],
                           }

        # Trigger codes
        self.trigger_dict = {"trial_od": 11, # object decoder
                             "trial_cp": 12, # cue practice
                             "trial_sd": 13, # spell decoder
                             "trial_g": 14, # generic 
                             "trial_an": 15, # autonomous
                             "end_trial": 10,
                             "display": 2,
                             "visual": 30,
                             "textual": 31,
                             "squares": 4,
                             "test_pos": 50,
                             "test_count": 51,
                             "test_catch": 52,
                             "test_spell": 53,
                             "pause": 6,
                             "run": 7,}


    def dialogue_box(self, participant=None, session=1, run_length=300, test_mode=False, meg=False, show_progress=True, show=True, ):
        ''' Show dialogue box to get participant info '''

        if participant is None:
            savefiles = glob.glob(f"{self.data_dir}{os.sep}*.txt")
            names = [0] + [int(os.path.basename(file)[:2])
                           for file in savefiles]
            participant = max(names)+1

        expName = "Alteration Magic School"
        expInfo = {"participant": str(participant).zfill(2),
                   "session": int(session),
                   "age": "",
                   "gender (f/m/d)": "",
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
        if self.test_mode:
            self.run_length /= 10
        self.meg = expInfo["MEG"]
        self.meta_fname = f"{self.data_dir}{os.sep}{expInfo['expName']}_id={expInfo['participant']}_start={expInfo['dateStr']}_metadata"
        for key in expInfo:
            self.add2meta(key, expInfo[key])
        self.expInfo = expInfo
        self.exp_clock = core.Clock()

        # set response keys according to device
        self.use_pp = False
        self.resp_keys = self.resp_keys_kb
        self.proceedKey = "space"
        
        if expInfo["MEG"]:
            self.use_pp = True
            self.resp_keys = self.resp_keys_vpixx
            self.proceedKey = self.resp_keys_vpixx[-1]
            self.init_interface()

        # response keys for main task
        self.resp_keys_4 = self.resp_keys[:-2]


    def init_window(self, res=None, screen=0, fullscr=False):
        ''' Initialize window '''
        if res is None:
            res = [1920, 1080]
        assert isinstance(res, list), "res must be list of two integers"
        self.win = visual.Window(
            res,
            fullscr=fullscr,
            color=self.color_dict["instructions"],
            screen=screen,
            monitor="testMonitor",
            units="deg")
        self.add2meta("frameRate", self.win.getActualFrameRate())
        self.drawList = []
        self.currentMode = "visual" # init cue modality


    def init_interface(self):
        ''' Initialize parallel port for sending MEG triggers '''
        # set pp to base state
        self.port_out2 = ParallelPort(address="0xd112")
        self.port_out2.setData(8)

        # for sending triggers
        self.port_out = ParallelPort(address="0xd110")
        self.port_out.setData(0)

        
    def send_trigger(self, trigger_type):
        # print(f"Trigger: {trigger_type}")
        trigger_code = self.trigger_dict[trigger_type]
        self.port_out.setData(trigger_code)
        self.diodeBack.autoDraw = False
        self.drawAllAndFlip(no_wait=True)
        core.wait(0.05)
        self.port_out.setData(0)
        self.diodeBack.autoDraw = True
        self.drawAllAndFlip(no_wait=True)


    def optionally_send_trigger(self, trigger_type):
        if self.use_pp and not self.instruction_mode:
            self.send_trigger(trigger_type)
        else:
            self.drawAllAndFlip()

    
    def load_trials(self):
        print("Loading trials...")
        pid = self.expInfo["participant"]

        # Instructions
        self.instructions = pickle.load(
            open(f"{self.stim_dir}{os.sep}instructions_en.pkl", "rb"))

        # Object decoder trials
        self.trials_obj_dec = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_obj_dec.pkl", "rb"))

        self.trials_prim_dec = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim_dec.pkl", "rb"))

        # Practice trials
        self.trials_prim_cue = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim_cue.pkl", "rb"))

        self.trials_prim_prac_c = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim_prac_c.pkl", "rb"))

        self.trials_prim_prac_p = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim_prac_p.pkl", "rb"))

        # Main trials
        self.trials_prim = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_prim.pkl", "rb"))

        self.trials_bin = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_binary.pkl", "rb"))
        
        self.trials_auto = pickle.load(
            open(f"{self.trial_list_dir}{os.sep}{pid}_trials_auto.pkl", "rb"))

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
        self.map_names_bin = np.unique(["+".join(trial["map"])
                                        for trial in self.trials_bin],
                                       axis=0)
        self.n_primitives = len(self.map_names)
        self.n_binaries = len(self.map_names_bin)

        # Determine_positions
        self.rect_pos = self.circularGridPositions(
            center_pos=self.center_pos, set_size=self.set_size)
        self.resp_pos = self.dragApartHorizontally(
            self.rectangularGridPositions(center_pos=[0, -7.], h_dist=7, dim=(1, 4)),
            by = 1.)
        self.resp_pos_num = self.dragApartHorizontally(
            self.rectangularGridPositions(center_pos=[0, -6.7], h_dist=7, dim=(1, 4)),
            by = 1.)
        self.cuepractice_pos = self.dragApartHorizontally(
            self.rectangularGridPositions(center_pos=[0, -4.], h_dist=7, dim=(1, self.n_cats)),
            by = 1.)
        self.spell_pos = self.dragApartHorizontally(
            self.rectangularGridPositions(center_pos=self.center_pos, h_dist=9, dim=(1, 4)),
            by = 1.)


    def render_visuals(self):
        print("Rendering unique visual objects...")

        self.instruct_stim = visual.TextStim(
            self.win,
            text='',
            height=1.3,
            font="mono",
            wrapWidth=35,
            pos=self.center_pos)

        self.rect = visual.Rect(
            win=self.win,
            width=self.normal_size[0],
            height=self.normal_size[1],
            fillColor=self.color_dict["light_grey"],
            lineColor=self.color_dict["dark_grey"])
        
        self.diodeBack = visual.Rect(
            win=self.win,
            width=self.win.size[1]/16,
            height=self.win.size[1]/16,
            fillColor=self.color_dict["mid_grey"],
            units="pix",
            pos=[self.win.size[0] * 0.495, -self.win.size[1] * 0.49],
            autoDraw=self.meg,
            )
        
        self.fixation = visual.GratingStim(
            self.win,
            color=-0.9,
            colorSpace="rgb",
            pos=self.center_pos,
            mask="circle",
            size=0.2)

        self.qm = visual.TextStim(self.win,
                                  text="?",
                                  height=4,
                                  color=self.color_dict["black"])
        
        self.match = visual.TextStim(self.win,
                                  text="Okay!",
                                  height=4,
                                  wrapWidth=40,
                                  pos=self.center_pos,
                                  color=self.color_dict["green"])
        
        self.slowmatch = visual.TextStim(self.win,
                                  text="Too slow!",
                                  height=4,
                                  wrapWidth=40,
                                  pos=self.center_pos,
                                  color=self.color_dict["dark_yellow"])
        
        self.nomatch = visual.TextStim(self.win,
                                       text="Inconsistent!",
                                       wrapWidth=40,
                                       height=4,
                                       pos=self.center_pos,
                                       color=self.color_dict["red"])

        self.moreTime = visual.TextStim(
            self.win,
            text="Go back, you need to spend more time on this.",
            height=1.5,
            wrapWidth=40,
            font="mono",
            color=self.color_dict["mid_grey"],
            pos=self.center_pos)

        self.nextPrompt = visual.TextStim(
            self.win,
            text="Navigate 'left' if you are not finished,\notherwise navigate 'right' to continue.",
            height=1.5,
            wrapWidth=40,
            font="mono",
            color=self.color_dict["mid_grey"],
            pos=self.center_pos)

        self.stopPrompt = visual.TextStim(
            self.win,
            text="Unfortunately you did not manage\nto give enough correct responses in time.\n\nPlease contact the experimenter.",
            height=1.5,
            wrapWidth=40,
            font="mono",
            color=self.color_dict["mid_grey"],
            pos=self.center_pos)

        self.leftArrow = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}leftArrow.png")[0])

        self.magicBooks = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}magicBooks.png")[0])

        self.magicChart = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}magicChart.png")[0])

        self.magicWand = visual.ImageStim(
            self.win,
            pos=self.center_pos,
            image=glob.glob(f"{self.stim_dir}{os.sep}magicWand.png")[0])

        self.pauseClock = visual.ImageStim(
            self.win,
            image=glob.glob(f"{self.stim_dir}{os.sep}pauseClock.png")[0],
            pos=self.center_pos)

        self.pauseText = visual.TextStim(
            self.win,
            text="Short Break.\nPress 'next' key to continue.",
            height=1.8,
            wrapWidth=30,
            font="Times New Roman",
            color=[-0.9, -0.9, -0.9])

        self.philbertine = visual.ImageStim(
            self.win, image=glob.glob(
                f"{self.stim_dir}{os.sep}philbertine.png")[0])
        
        self.splash = visual.ImageStim(
            self.win,
            image=glob.glob(
                f"{self.stim_dir}{os.sep}splash.png")[0],
            pos=self.center_pos)

        # Count responses
        self.count_dict = {
            str(i): visual.TextStim(
                self.win,
                text=str(i),
                height=4,
                color=self.color_dict["black"])
            for i in range(self.n_resp)
        }

        # Yes/No responses
        self.yn_dict = {
            True: visual.TextStim(
                self.win,
                text="Y",
                height=4,
                color=self.color_dict["black"]),
            False: visual.TextStim(
                self.win,
                text="N",
                height=4,
                color=self.color_dict["black"])
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
        self.stim_dict = {
            stim_names[i]: visual.ImageStim(
                self.win,
                image=stim_list[i])
            for i in range(len(stim_list))
        }


    # Background Components --------------------------------------------------------
    def dump(self, trials, fname, source_of_difference="structure"):
        if source_of_difference:
            print(f"WARNING: Not all trials have the same {source_of_difference}, pickling instead!")
        with open(fname + ".pkl", "wb") as f:
            pickle.dump(trials, f)
            print(f"Saved {len(trials)} trials to '{fname}.pkl'")
        
        
    def listofdicts2csv(self, trials, fname):
        """ write a list of trialdicts to a csv """
        trials = copy.deepcopy(trials)
        
        try:
            # === data integrity checks ===
            # 1. check if all trials have the same keys, dump otherwise
            unique_keys = trials[0].keys()
            key_check_list = [set(trial.keys()) == set(unique_keys)
                            for trial in trials]
            if not all(key_check_list):
                self.dump(trials, fname, "keys")
                return
                
            # 2. check if all trials have the same item types per key, dump otherwise
            key_types = {key: type(trials[0][key])
                        for key in unique_keys}
            type_check_list = [type(trial[key]) == key_types[key]
                            for trial in trials for key in unique_keys if key != "target"]
            if not all(type_check_list):
                self.dump(trials, fname, "key types")
                return
            
            # === data transformations ===
            # spread out lists and sets to new enumerated keys
            original_keys = list(unique_keys)
            list_keys = [key for key in original_keys
                        if isinstance(trials[0][key], (set, list, np.ndarray))]
            if list_keys:
                new_keys = []
                for trial in trials:
                    for key in list_keys:
                        trial_updates = {f"{key}_{i}": item
                                        for i, item in enumerate(trial[key])}
                        trial.update(trial_updates)
                        new_keys.extend(trial_updates.keys())
                        del trial[key]
                
                # update unique_keys (some trials may have more than others) and sort them in original order
                new_keys = sorted(set(new_keys))
                unique_keys = np.setdiff1d(original_keys, list_keys)
                unique_keys = sorted(np.union1d(unique_keys, new_keys))
        
            # === write to csv ===
            with open(fname + ".csv", "w", newline="") as output_file:
                dict_writer = csv.DictWriter(output_file, unique_keys)
                dict_writer.writeheader()
                dict_writer.writerows(trials)
                print(f"Saved {len(trials)} trials to '{fname}.csv'")
                
        except Exception as e:
            print(e)
            self.dump(trials, fname, "other exception")
            return
            

    def save_object(self, obj, fname, ending='pkl'):
        if ending == 'csv':
            self.listofdicts2csv(obj, fname)
        elif ending == 'pkl':
            self.dump(obj, fname, "")


    def writeFileName(self, dataset_name):
        return f"{self.data_dir}{os.sep}{self.expInfo['expName']}_id={self.expInfo['participant']}_start={self.expInfo['dateStr']}_data={dataset_name}"


    def add2meta(self, var, val):
        with open(f"{self.meta_fname}.csv", "a") as f:
            f.write(f"{var},{val}\n")


    def init_progbar(self, bar_len=None, bar_height=None, milestones=[0.25, 0.5, 0.75]):
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
            autoDraw=self.show_progress)
        self.mileStones = []
        for m in [m-0.5 for m in milestones]:
            self.mileStones.append(visual.Rect(
                self.win,
                units="pix",
                width=self.win.size[1]/256,
                height=self.bar_height,
                pos=[m*bar_len, self.bar_pos[1]],
                fillColor=self.color_dict["light_grey2"],
                autoDraw=self.show_progress))
        self.progTest = visual.Rect(
            self.win,
            units="pix",
            width=0,
            height=self.bar_height,
            pos=self.bar_pos,
            fillColor=self.color_dict["green"],
            autoDraw=self.show_progress)
        self.start_width = 0.0
        self.progbar_inc = 0.01  # 1% of bar length


    def set_progbar_inc(self):
        if not hasattr(self, "inc_queue"):
            raise ValueError("No inc_queue attribute found")
        inc = self.inc_queue.pop(0)
        self.progbar_inc = inc


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

        # Move progress bar
        for _ in range(n_steps):
            self.move_prog_bar_step(bar_width_step, flip_win=flip_win)

        # Last bit for completion
        self.move_prog_bar_step(
            self.progBack.width * end_width - self.progTest.width,
            flip_win=flip_win)
        if flip_win:
            core.wait(1.5 * wait_s)
        self.start_width = self.progTest.width / self.progBack.width


    def setMilestones(self, trial_numbers, weights=None):
        """ set milestones proportional to weighted trial numbers and save the increments for the progress bar """
        if weights is None:
            weights = np.ones(len(trial_numbers))
        trial_numbers = np.array(trial_numbers)
        weights = np.array(weights)
        assert len(trial_numbers) == len(
            weights), "trial_numbers and weights must have the same length"

        tn_weighted = trial_numbers * weights
        n_total = tn_weighted.sum()
        milestones = np.cumsum(tn_weighted)/n_total
        self.inc_queue = (tn_weighted/n_total/trial_numbers).tolist()
        return milestones.tolist()[:-1]
    

    @staticmethod
    def circularGridPositions(center_pos=[0, 0], set_size=6, radius=5.5):
        angle = 2*np.pi/set_size
        rect_pos = np.empty((set_size, 2), dtype=float).copy()
        for i in range(set_size):
            rect_pos[i] = [center_pos[0] + radius * np.sin(i * angle),
                           center_pos[1] + radius * np.cos(i * angle)]
        return rect_pos


    @staticmethod
    def rectangularGridPositions(center_pos=[0, 0], v_dist=10, h_dist=10, dim=(2, 3)):
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
    

    @staticmethod
    def dragApartHorizontally(response_positions, by=1.):
        for pos in response_positions:
            sign = np.sign(pos[0])
            pos[0] += sign * by
        return response_positions


    ###########################################################################
    # Instructions
    ###########################################################################

    def iSingleImage(self, img):
        pos_tmp = img.pos
        img.pos = self.center_pos
        img.draw()
        img.pos = pos_tmp
        self.win.flip()
        core.wait(0.2)


    def iTransmutableObjects(self, none):
        stimuli = self.stim_dict.copy()
        categories = sorted(list(stimuli.keys()))
        n_cats = self.n_cats

        # determine positions
        if n_cats > 4:
            dim = [2, np.ceil(n_cats/2)]
        else:
            dim = [1, n_cats]
        category_pos = self.rectangularGridPositions(
            center_pos=self.center_pos, h_dist=8, dim=dim)

        # draw categories
        for i in range(n_cats):
            self.rect.pos = category_pos[i]
            self.rect.draw()
            stim = stimuli[categories[i]]
            stim.pos = category_pos[i]
            stim.draw()
        self.win.flip()


    def iSpellExample(self, displays):
        assert len(displays) == 2, "displays must be a list of two lists"
        self.drawList = []
        stimuli = self.stim_dict.copy()
        rect_pos = self.circularGridPositions(
            center_pos=self.center_pos, set_size=self.set_size)

        def drawInput(dispNum):
            for i, key in enumerate(displays[dispNum]):
                self.rect.pos = rect_pos[i]
                self.rect.draw()
                stim = stimuli[key]
                stim.pos = rect_pos[i]
                stim.draw()

        # Input display
        self.enqueueDraw(func=drawInput, args=[0,])
        core.wait(1)

        # Let the magic happen
        self.enqueueDraw(func=self.magicWand.draw)
        core.wait(1)

        # Output display
        self.enqueueDraw(func=drawInput, args=[1,])
        core.wait(1)


    def iNavigate(self, page=0, max_page=99, continue_after_last_page=True,
                  proceed_key="/k", wait_s=3, timer=None):

        assert proceed_key in ["/k", "/t", "/e"], "Unkown proceed key"

        left, right = self.resp_keys[-2:]
        skip = "return"
        finished = False
        testResp = None
        TestClock = core.Clock()

        # get response or wait or something in between
        if proceed_key == "/k":  # keypress
            _, testResp = self.tTestResponse(
                TestClock, [left, right],
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
        if testResp == right:
            if page < max_page-1:
                page += 1
            elif continue_after_last_page:
                finished = True
            elif timer is not None and timer.getTime() > 0:
                self.moreTime.draw()
                self.win.flip()
                _, contResp = self.tTestResponse(TestClock, [left, skip],
                                                 return_numeric=False)
                if contResp == skip:
                    finished = True
            else:
                self.nextPrompt.draw()
                self.win.flip()
                _, contResp = self.tTestResponse(TestClock, [left, right],
                                                 return_numeric=False)
                if contResp == right:
                    finished = True
        elif testResp == left and page > 0:
            page -= 1

        return page, finished


    def Instructions(self, part_key="Intro",
                     special_displays=list(),
                     args=list(),
                     complex_displays=list(),
                     kwargs=list(),
                     font="Mono",
                     fontcolor=[-0.8, -0.8, -0.8],
                     log_duration=True,
                     loading_time=1):
        assert part_key in self.instructions.keys(),\
            "No instructions provided for this part"

        # Initialize parameters
        finished = False
        self.instruction_mode = True
        Part = self.instructions[part_key]
        page = 0
        self.win.color = self.color_dict["instructions"]
        self.instruct_stim.font = font
        self.instruct_stim.color = fontcolor
        self.win.clearBuffer()
        self.win.flip()
        if log_duration:
            instructions_clock = core.Clock()

        # Navigate through instructions
        while not finished:
            page_content, proceed_key, proceed_wait = Part[page]

            # draw page content
            if isinstance(page_content, str):
                self.instruct_stim.text = page_content
                self.instruct_stim.draw()
                self.win.flip()
            elif isinstance(page_content, int):
                idx = page_content
                arg = args[idx]
                special_displays[idx](arg)
            elif isinstance(page_content, float):
                idx = int(page_content)
                kwarg = kwargs[idx]
                complex_displays[idx](**kwarg)

            # wait for response
            page, finished = self.iNavigate(page=page,
                                            max_page=len(Part),
                                            proceed_key=proceed_key,
                                            wait_s=proceed_wait)
        if log_duration:
            duration = instructions_clock.getTime()
            self.add2meta(f"duration_{part_key}", duration)
        self.win.color = self.color_dict["white"]
        self.win.flip()
        core.wait(loading_time)
        self.instruction_mode = False

    ###########################################################################
    # Cues
    ###########################################################################

    def drawPracticeCue(self, map_idx, cue_center_pos, vert_dist):
        # Draw map cue
        map_name = self.map_names[map_idx]
        for j, mode in enumerate(["textual", "visual"]):
            cue = self.setCue(map_name, mode=mode)
            cue.pos = [sum(x) for x in
                       zip(cue_center_pos, [0, (1-j)*vert_dist])]
            cue.draw()
        return map_name.split("-")


    def drawMapInstruction(self, categories, category_pos, stimuli):
        for i, category in enumerate(categories):
            self.rect.pos = category_pos[i]
            self.rect.draw()
            cat = stimuli[category]
            cat.pos = category_pos[i]
            cat.draw()
        self.leftArrow.draw()


    def learnCues(self, cue_center_pos=[0, 2], vert_dist=7,
                  min_duration=60):
        ''' Interactive display for learning cues for all maps, return viewing duration '''

        # Init
        self.win.flip()
        finished = False
        page = 0
        self.leftArrow.pos = [0, cue_center_pos[1] - vert_dist]
        category_pos = self.rectangularGridPositions(
            center_pos=self.leftArrow.pos, h_dist=15, dim=(1, 2))
        stimuli = self.stim_dict.copy()
        learn_clock = core.Clock()
        timer = core.CountdownTimer(start=min_duration)

        while not finished:
            # Draw map cue
            categories = self.drawPracticeCue(page, cue_center_pos, vert_dist)

            # Draw corresponding explicit map
            self.drawMapInstruction(categories, category_pos, stimuli)
            self.win.flip()
            core.wait(0.2)

            # Navigate
            page, finished = self.iNavigate(
                page=page, max_page=self.n_primitives,
                continue_after_last_page=False,
                timer=timer)

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

    def redrawAfterResponse(self, stimulus, rectPos=(0, 0), isNeutral=False, isCorrect=False, isQuick=False, stimPos=None):
        ''' Redraw the stimulus after a response has been made and indicate performance via color '''
        if stimPos is None:
            stimPos = rectPos

        # set informative border color
        if isNeutral:
            lc = self.color_dict["dark_blue"]
        elif not isCorrect:
            lc = self.color_dict["red"]
        elif not isQuick:
            lc = self.color_dict["yellow"]
        else:
            lc = self.color_dict["green"]

        # redraw rectangle
        self.rect.lineColor = lc
        self.rect.pos = rectPos
        self.rect.draw()
        self.rect.lineColor = self.color_dict["dark_grey"]  # reset
        stimulus.pos = stimPos
        stimulus.draw()


    def redrawFeedback(self, stimulus, rectPos=(0, 0), stimPos=None, wait_s=0.5):
        ''' Mark the correct response option as feedback '''
        if stimPos is None:
            stimPos = rectPos
        core.wait(wait_s)
        self.rect.pos = rectPos
        self.rect.lineColor = self.color_dict["dark_blue"]
        self.rect.fillColor = self.color_dict["blue"]
        self.rect.draw()
        self.rect.lineColor = self.color_dict["dark_grey"]  # reset
        self.rect.fillColor = self.color_dict["light_grey"]  # reset
        stimulus.pos = stimPos
        stimulus.draw()


    def drawAllAndFlip(self, no_wait=False):
        for func, args in self.drawList:
            if len(args) == 0:
                func()
            else:
                if no_wait:
                    func_args = inspect.getfullargspec(func).args
                    if "wait_s" in func_args:
                        idx = func_args.index("wait_s") - 1
                        if idx < len(args):
                            args[idx] = 0.
                        else:
                            func(*args, wait_s=0.)
                            continue
                func(*args)
        self.win.flip()


    def enqueueDraw(self, func=None, args=[], unroll=True):
        self.drawList += [(func, args)]
        if unroll:
            self.drawAllAndFlip()


    def cuePracticeTrial(self, trial, mode="random", cue_pos=(0, 5), goal_rt=2.5, demonstration=False):
        ''' Subroutine for the cue practice trials'''
        # Init
        self.drawList = []
        self.win.flip()
        stimuli = self.stim_dict.copy()
        testResp = ""
        testRespList = []
        testRTList = []
        trial["start_time"] = self.exp_clock.getTime()
        self.optionally_send_trigger("trial_cp")

        # Fixation Cross
        self.tFixation()

        # Map Cue and Response Options
        if mode == "random":
            mode = np.random.choice(["textual", "visual"])
        cue = self.setCue(trial["map"][0], mode=mode)
        cue.pos = cue_pos
        self.enqueueDraw(func=cue.draw, unroll=False)
        self.enqueueDraw(func=self.drawResponseOptions,
                         args=[stimuli, trial["resp_options"]])
        self.optionally_send_trigger(mode)

        # Optionally terminate demonstration
        if demonstration:
            return
        
        # Wait for response(s)
        for correctResp in trial["correct_resp"]:
            if testResp == 99:
                continue
            testRT, testResp = self.tTestResponse(
                core.Clock(), self.resp_keys_4)
            testRTList.append(testRT)
            testRespList.append(testResp)
            if testResp != 99:
                self.enqueueDraw(func=self.redrawAfterResponse,
                                 args=[stimuli[trial["resp_options"][testResp]],
                                       self.cuepractice_pos[testResp],
                                       False,
                                       correctResp == testResp,
                                       sum(testRTList) <= goal_rt])
        # Feedback (if incorrect)
        if trial["correct_resp"] != testRespList:
            for i, correctResp in enumerate(trial["correct_resp"]):
                self.enqueueDraw(func=self.redrawFeedback,
                                 args=[stimuli[trial["resp_options"][correctResp]],
                                       self.cuepractice_pos[correctResp],
                                       None,
                                       1-i])

        # Save data and clear screen
        trial["emp_resp"] = testRespList
        trial["resp_RT"] = testRTList
        trial["cue_type"] = mode
        self.drawAllAndFlip()
        core.wait(0.2)
        self.optionally_send_trigger("end_trial")


    def streakGoalReached(self, streak_goal=5, keys=[]):
        ''' Evaluates the counter dict for the adaptive cue practice'''
        if len(keys) == 0:
            keys = self.counter_dict.keys()
        for k in keys:
            if self.counter_dict[k] < streak_goal:
                return False
        return True
    

    def streakGoalReachedMultiple(self, streak_goals=[1, 1], key_lists=[[], []]):
        ''' Evaluates the counter dict for the adaptive cue practice'''
        outcomes = []
        for streak_goal, keys in zip(streak_goals, key_lists):
            outcomes += [self.streakGoalReached(streak_goal=streak_goal, keys=keys)]
        return all(outcomes)
    

    def updateCounterDict(self, trial, streak_goal=10, goal_rt=2.0, applicable=True, decrease=True):
        ''' Updates the counter dict for the adaptive generic blocks:
            - increase counter if correct response if below streak goal
            - decrease counter if incorrect response if above 0
        '''
        map_name = "+".join(trial["map"])
        correct = trial["correct_resp"] == trial["emp_resp"]
        fast = trial["resp_RT"] <= goal_rt if isinstance(
            trial["resp_RT"], float) else sum(trial["resp_RT"]) <= goal_rt
        idk = trial["emp_resp"][0] == 99 if isinstance(
            trial["emp_resp"], list) else trial["emp_resp"] == 99

        if idk:
            pass
        elif correct and fast and applicable and self.counter_dict[map_name] < streak_goal:
            self.counter_dict[map_name] += 1
        elif decrease and not correct and self.counter_dict[map_name] > 0:
            self.counter_dict[map_name] -= 1
        print(self.counter_dict)


    def adaptiveCuePractice(self, trials_prim_cue, streak_goal=5, goal_rt=2.5, mode="random"):
        ''' Practice cues until for each map the last streak_goal trials are correct and below the goal_rt'''
        self.counter_dict = {map: 0 for map in self.map_names}
        start_width_initial = self.start_width if self.show_progress else 0. # progbar
        trials = data.TrialHandler(trials_prim_cue, 1, method="sequential")
        out = []

        while not self.streakGoalReached(streak_goal=streak_goal):
            if trials.nRemaining == 0:
                self.terminate(out)

            trial = trials.next()
            # probabilistically skip if this cue has already been mastered
            if self.counter_dict[trial["map"][0]] == streak_goal and np.random.random() > 0.2:
                continue
            self.cuePracticeTrial(trial, mode=mode, goal_rt=goal_rt)
            self.updateCounterDict(trial, streak_goal, goal_rt)
            out.append(trial)

            if self.show_progress:
                end_width = start_width_initial + \
                    sum(self.counter_dict.values()) * self.progbar_inc
                self.move_prog_bar(end_width=end_width, wait_s=0)
        core.wait(1)
        return out


    def terminate(self, out):
        ''' Terminate experiment gracefully'''
        print("Aborting experiment due to lack of trials.")
        self.add2meta("t_abort", data.getDateStr())
        self.stopPrompt.draw()
        self.win.flip()
        self.save_object(out, self.writeFileName("rescuedData"), ending='csv')
        core.wait(10)
        self.win.close()
        core.quit()


    ###########################################################################
    # Normal Trials (methods prefaced with "t" may require response)
    ###########################################################################

    def tFixation(self, duration=0.3):
        ''' draw fixation cross'''
        self.win.flip()
        self.fixation.draw()
        self.win.flip()
        core.wait(duration)
        

    def setCue(self, key, mode):
        ''' return cue stimulus for a given mode'''
        if mode == "visual":
            cue = self.vcue_dict.copy()[key]
        elif mode == "textual":
            cue = self.tcue_dict.copy()[key]
        else:
            raise ValueError("Chosen cue mode not implemented.")
        return cue


    def drawCue(self, trial, mode):
        ''' draw cue(s) for a given trial'''
        n_cues = len(trial["map"])

        # draw each cue
        for i, _map in enumerate(trial["map"]):
            cue = self.setCue(_map, mode)
            if n_cues == 1:
                cue.pos = self.center_pos
            else:
                cue.pos = self.double_cue_positions_visual[i] if mode == "visual" else self.double_cue_positions_textual[i]
            cue.draw()
            

    def tCue(self, trial, mode="random"):
        if mode == "random":
            mode = np.random.choice(["visual", "textual"])
        self.currentMode = mode
            
        self.drawList = []
        
        # draw cue(s)
        self.enqueueDraw(func=self.drawCue, args=[trial, mode], unroll=False)

        # send trigger
        self.optionally_send_trigger(self.currentMode)


    def drawStimuli(self, trial):
        stimuli = self.stim_dict.copy()
        for i in range(self.set_size):
            stim_name = trial["input_disp"][i]
            if stim_name:
                stim = stimuli[stim_name]
                stim.pos = self.rect_pos[i]
                stim.draw()


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
            if thisKey == self.proceedKey:
                break

            # case: abort
            elif thisKey == "escape":
                self.add2meta("t_abort", data.getDateStr())
                self.win.close()
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
                print("tTestResponse timed out")
                testResp = 99
                testRT = max_wait
                break
            else:
                thisKey, testRT = pressed[0]

                # case: valid response
                if thisKey in respKeys:
                    testResp = respKeys.index(
                        thisKey) if return_numeric else thisKey
                # case: don't know
                elif thisKey == self.proceedKey:
                    testResp = 99
                # case: abort
                elif thisKey == "escape":
                    self.add2meta("t_abort", data.getDateStr())
                    self.win.close()
                    core.quit()  # abort experiment

        return testRT, testResp


    def drawEmptySquares(self):
        self.fixation.draw()
        self.rect.size = self.normal_size
        for pos in self.rect_pos:
            self.rect.pos = pos
            self.rect.draw()


    def tEmptySquares(self, IRClock=None):
        ''' draw empty squares and wait for response'''
        self.drawList = []
        
        # draw cue(s)
        self.enqueueDraw(func=self.drawEmptySquares, unroll=False)

        # send trigger
        self.optionally_send_trigger("squares")

        # get response
        if IRClock is None:
            return 0.0
        else:
            return self.tIndermediateResponse(IRClock)
    

    def tInput(self, trial, duration=1.0, self_paced=False):
        ''' draw input stimuli and wait for response if self_paced'''
        self.drawList = []
        
        # draw rectangles
        self.enqueueDraw(func=self.drawEmptySquares, unroll=False)

        # draw stimuli
        self.enqueueDraw(func=self.drawStimuli, args=[trial,], unroll=False)

        # send trigger
        self.optionally_send_trigger("display")
        
        # flip
        if self_paced:
            intermediateRT = self.tIndermediateResponse(core.Clock())
        else:
            core.wait(duration)
            intermediateRT = duration
        return intermediateRT


    def tPause(self):
        ''' draw pause screen and wait for response'''
        self.drawList = []
        self.optionally_send_trigger("pause")
        self.pauseClock.draw()
        self.pauseText.draw()
        self.win.flip()
        intermediateRT = self.tIndermediateResponse(
            core.Clock(), max_wait=float('inf'))
        self.win.flip()
        self.optionally_send_trigger("pause")
        core.wait(0.5)
        return intermediateRT


    def drawCountTarget(self, stimulus):
        ''' draw target stimulus for count test'''
        self.rect.pos = self.center_pos
        self.rect.size = self.center_size
        self.rect.draw()
        self.rect.size = self.normal_size  # reset size
        stimulus.pos = self.center_pos
        stimulus.draw()


    def drawCountResponses(self):
        ''' draw response options for count test'''
        self.rect.lineColor = self.color_dict["dark_grey"]
        for i, pos in enumerate(self.resp_pos):
            self.rect.pos = pos
            self.rect.draw()
            resp = self.count_dict[str(i)]
            resp.pos = self.resp_pos_num[i]
            resp.draw()

    
    def drawSpellOptions(self):
        ''' draw spell response options for autonomous trials'''
        self.rect.lineColor = self.color_dict["dark_grey"]
        self.rect.size = self.center_size
        vcues = list(self.vcue_dict.values()) + [self.qm]
        for vcue, pos in zip(vcues, self.spell_pos):
            self.rect.pos = pos
            self.rect.draw()
            vcue.pos = pos
            vcue.draw()
    

    def drawCatchResponses(self):
        ''' draw response options for one-back test'''
        self.rect.lineColor = self.color_dict["dark_grey"]
        yn_positions_box = self.resp_pos[1:3]
        yn_positions = self.resp_pos_num[1:3]
        for i in range(len(yn_positions)):
            self.rect.pos = yn_positions_box[i]
            self.rect.draw()
            resp = self.yn_dict[bool(i)]
            resp.pos = yn_positions[i]
            resp.draw()

    
    def tSpellOptions(self, demonstration=False, wait_s=0.5):
        ''' wrapper for count test'''
        # Init
        self.drawList = []
        stimuli = list(self.vcue_dict.values()) + [self.qm]
        self.enqueueDraw(func=self.drawSpellOptions, unroll=False)

        # Send trigger
        self.optionally_send_trigger("test_spell")
        
        # Optionally break for demonstration purposes        
        if demonstration:
            return None, None

        # Get response
        testRT, testResp = self.tTestResponse(core.Clock(), self.resp_keys_4)
        
        # Feedback
        if testResp == 99:
            testResp = 3
        if testResp != 99 and testResp is not None:
            self.enqueueDraw(func=self.redrawAfterResponse,
                             args=[stimuli[testResp],
                                   self.spell_pos[testResp],
                                   True,
                                   False,
                                   False,
                                   self.spell_pos[testResp]])
        if testResp == 3:
            testResp = 99
            
        # Wait
        core.wait(wait_s)
        return testRT, testResp
    

    def tCount(self, trial, feedback=False, demonstration=False, duration=1.0, goal_rt=2.0):
        ''' wrapper for count test'''
        # Init
        self.drawList = []
        stimuli = self.stim_dict.copy()
        if feedback:
            corResp = trial["correct_resp"]

        # Draw stimuli
        self.enqueueDraw(func=self.drawCountTarget,
                         args=[stimuli[trial["target"]],],
                         unroll=False)
        self.enqueueDraw(func=self.drawCountResponses, unroll=False)

        # Send trigger
        self.optionally_send_trigger("test_count")

        # Get response
        if demonstration:
            testRT, testResp = 0.0, 99
        else:
            testRT, testResp = self.tTestResponse(core.Clock(), self.resp_keys_4)

        # Feedback
        if feedback:
            # immediate
            if testResp != 99:
                self.enqueueDraw(func=self.redrawAfterResponse,
                                 args=[self.count_dict[str(testResp)],
                                       self.resp_pos[testResp],
                                       False,
                                       corResp == testResp,
                                       testRT <= goal_rt,
                                       self.resp_pos_num[testResp]])

            # correct solution
            if corResp != testResp:
                self.enqueueDraw(func=self.redrawFeedback,
                                 args=[self.count_dict[str(corResp)],
                                       self.resp_pos[corResp],
                                       self.resp_pos_num[corResp]])
        elif testResp != 99:
            self.enqueueDraw(func=self.redrawAfterResponse,
                                 args=[self.count_dict[str(testResp)],
                                       self.resp_pos[testResp],
                                       True,
                                       False,
                                       False,
                                       self.resp_pos_num[testResp]])
        core.wait(duration)
        return testRT, testResp


    def drawPositionTarget(self, target_idx):
        ''' draw target stimulus for position test'''
        for i, pos in enumerate(self.rect_pos):
            self.rect.pos = pos
            self.rect.draw()
            if target_idx == i:
                self.qm.pos = [pos[0], pos[1] + 0.3]
                self.qm.draw()

    def drawPositionResponses(self, stimuli, resp_options):
        ''' draw response options for position test'''
        for i, pos in enumerate(self.resp_pos):
            self.rect.pos = pos
            self.rect.draw()
            resp = stimuli[resp_options[i]]
            resp.pos = pos
            resp.draw()


    def tPosition(self, trial, feedback=False, demonstration=False, duration=1.0, goal_rt=2.0):
        ''' wrapper for position test'''
        # Init
        self.drawList = []
        stimuli = self.stim_dict.copy()
        if feedback:
            corResp = trial["correct_resp"]

        # Draw stimuli
        self.enqueueDraw(func=self.drawPositionTarget,
                         args=[trial["target"],],
                         unroll=False)
        self.enqueueDraw(func=self.drawPositionResponses,
                         args=[stimuli, trial["resp_options"],],
                         unroll=False)
        
        # Send trigger
        self.optionally_send_trigger("test_pos")

        # Get response
        if demonstration:
            testRT, testResp = 0.0, 99
        else:
            testRT, testResp = self.tTestResponse(core.Clock(), self.resp_keys_4)

        # Feedback
        if feedback:
            # immediate
            if testResp != 99:
                self.enqueueDraw(func=self.redrawAfterResponse,
                                 args=[stimuli[trial["resp_options"][testResp]],
                                       self.resp_pos[testResp],
                                       False,
                                       corResp == testResp,
                                       testRT <= goal_rt])
            # correct solution
            if corResp != testResp:
                self.enqueueDraw(func=self.redrawFeedback,
                                 args=[stimuli[trial["resp_options"][corResp]],
                                       self.resp_pos[corResp]])
        elif testResp != 99:
            self.enqueueDraw(func=self.redrawAfterResponse,
                             args=[stimuli[trial["resp_options"][testResp]],
                                   self.resp_pos[testResp],
                                   True,
                                   False,
                                   False])

        core.wait(duration)
        return testRT, testResp


    def genericTrial(self, trial, mode="random", self_paced=True, feedback=True, skip_test=False,
                     fixation_duration=0.3, cue_duration=0.5, goal_rt=2.0):
        ''' subroutine for generic trials'''
        # Init
        self.drawList = []
        self.win.flip()
        trial["start_time"] = self.exp_clock.getTime()
        self.optionally_send_trigger("trial_g")

        # Fixation
        self.tFixation(duration=fixation_duration)

        # Display input
        display_rt = self.tInput(trial, self_paced=self_paced)

        # Cue
        self.tFixation()
        self.tCue(trial, mode=mode)
        core.wait(cue_duration)
        
        # Splash Screen
        self.splash.draw()
        self.win.flip()
        core.wait(0.2)
        
        # Transformation display
        inter_rt = self.tEmptySquares(None if skip_test else core.Clock())

        # End trial for demonstration purposes
        if skip_test:
            return

        # Empty display
        self.win.flip()
        core.wait(0.2)

        # Test display
        testMethod = self.tCount if trial["test_type"] == "count" else self.tPosition
        test_rt, test_resp = testMethod(
            trial, feedback=feedback, goal_rt=goal_rt)
        self.drawAllAndFlip()

        # Save data
        trial["display_RT"] = display_rt
        trial["inter_RT"] = inter_rt
        trial["resp_RT"] = test_rt
        trial["emp_resp"] = test_resp
        trial["cue_type"] = self.currentMode
        core.wait(0.2)
        self.optionally_send_trigger("end_trial")


    def autonomousTrial(self, trial, self_paced=True, fixation_duration=0.3, goal_rt=2.0):
        ''' subroutine for generic trials'''
        # Init
        self.drawList = []
        self.win.flip()
        trial["start_time"] = self.exp_clock.getTime()
        self.optionally_send_trigger("trial_an")

        # Fixation
        self.tFixation(duration=fixation_duration)

        # Display input
        display_rt = self.tInput(trial, self_paced=self_paced)

        # Cue
        self.tFixation()
        self.qm.pos = self.center_pos
        self.qm.draw()
        self.win.flip()
        splash_rt = self.tIndermediateResponse(core.Clock())
        self.splash.draw()
        self.win.flip()
        core.wait(0.2)

        # Transformation display
        inter_rt = self.tEmptySquares(core.Clock())

        # Empty display
        self.win.flip()
        core.wait(0.2)

        # Test display
        testMethod = self.tCount if trial["test_type"] == "count" else self.tPosition
        test_rt, test_resp = testMethod(trial, feedback=False, demonstration=False, goal_rt=goal_rt, duration=0.5)
        self.drawAllAndFlip()
        
        # Choice Display
        if test_resp != 99:
            self.tFixation()
            choice_rt, choice_resp = self.tSpellOptions(demonstration=False, wait_s=0.5)
            self.drawAllAndFlip()
        else:
            choice_rt, choice_resp = 0.0, 99
        
        # Save remaining data
        trial["display_RT"] = display_rt
        trial["splash_RT"] = splash_rt
        trial["inter_RT"] = inter_rt
        trial["resp_RT"] = test_rt
        trial["choice_RT"] = choice_rt
        trial["choice_resp"] = choice_resp
        if choice_resp in range(3):
            cr = trial[f"correct_resp_{choice_resp}"]
            trial["correct_resp"] = np.where(trial["resp_options"] == cr)[0][0]
        else:
            trial["correct_resp"] = 99
        trial["emp_resp"] = test_resp
        core.wait(0.2)
        self.optionally_send_trigger("end_trial")

    
    def autonomousBlock(self, trial_df, pause_between_runs=True, self_paced=True, goal_rt=2.0, correct_goal=10,):
        self.drawList = []
        trials = data.TrialHandler(trial_df, 1, method="sequential")
        out = []
        queue = []
        requeue_counter = 0
        n_correct = 0

        if pause_between_runs:
            run_number = 1
            timer = core.CountdownTimer(self.run_length)
            self.optionally_send_trigger("run")

        while n_correct < correct_goal:
            # Optionally requeue trials
            if trials.nRemaining == 0:
                if len(queue) > 0 and requeue_counter < 2:
                    requeue_counter += 1
                    print(f"No remaining trials, requeue #{requeue_counter}...")
                    trials = data.TrialHandler(queue, 1, method="random")
                    queue = []
                    continue
                else:
                    self.terminate(out)
            
            # Run trial
            trial = trials.next()
            self.autonomousTrial(trial, self_paced=self_paced, goal_rt=goal_rt)

            # Evaluate performance
            correct = trial["correct_resp"] == trial["emp_resp"]
            fast = trial["resp_RT"] <= goal_rt and trial["choice_RT"] <= goal_rt
            idk = trial["emp_resp"] == 99 or trial["choice_resp"] == 99
            
            # Give feedback
            if idk:
                queue += [trial]
            else:
                if correct and fast:
                    self.match.draw()
                    n_correct += 1
                    print(f"Correct! {n_correct}/{correct_goal}")
                else:
                    queue += [trial]
                    if correct:
                        self.slowmatch.draw()
                    else:
                        self.nomatch.draw()
                self.win.flip()
                core.wait(0.4)
                self.win.flip()
            
            # Pause display between runs
            if pause_between_runs:
                trial["run_number"] = run_number
                if timer.getTime() <= 0:
                    self.tPause()
                    timer.reset()
                    run_number += 1
                    self.optionally_send_trigger("run")
                    
            # finally
            out.append(trial)
            core.wait(0.2)
           
        return out
    

    def oneBackTest(self, trial):
        """ display the target object and ask the participant if it is the same as the previous trial """
        self.drawList = []
        no, yes = self.resp_keys[-2:]
        stimuli = self.stim_dict.copy()

        # Draw stimuli
        self.enqueueDraw(func=self.drawCountTarget,
                         args=[stimuli[trial["target"]],],
                         unroll=False)
        self.enqueueDraw(func=self.drawCatchResponses, unroll=False)

        # Send trigger
        self.optionally_send_trigger("test_catch")

        testRT, testResp = self.tTestResponse(
            core.Clock(), [no, yes], return_numeric=False)
        return testRT, testResp == yes


    def objectDecoderTrial(self, trial, fixation_duration=0.3):
        """ Subroutine in which the participant sees an object and may encounter a 1-back task"""
        # Init
        test_rt, test_resp = None, None
        trial["start_time"] = self.exp_clock.getTime()
        self.drawList = []
        self.optionally_send_trigger("trial_od")

        # Fixation
        self.enqueueDraw(func=self.fixation.draw, unroll=False)
        self.enqueueDraw(func=self.drawEmptySquares)
        core.wait(fixation_duration)

        # Display input
        self.enqueueDraw(func=self.drawStimuli, args=[trial,], unroll=False)
        self.optionally_send_trigger("display")
        core.wait(1.0)

        # Catch trial
        if trial["is_catch_trial"]:
            test_rt, test_resp = self.oneBackTest(trial)

        # Save data
        trial["resp_RT"] = test_rt
        trial["emp_resp"] = test_resp
        core.wait(0.5)
        self.optionally_send_trigger("end_trial")


    def generateCounterDict(self, map_type="primitive"):
        ''' Generates a dictionary with the counter for each map'''
        if map_type == "primitive":
            map_names = self.map_names
        elif map_type == "generic":
            map_names = self.map_names_bin
        elif map_type == "all": # concatenate both numpy arrays
            map_names = np.concatenate((self.map_names, self.map_names_bin))
        else:
            raise ValueError("map_type must be one of 'primitive', 'compositional' or 'all'")
        self.counter_dict = {m: 0 for m in map_names}


    def adaptiveBlock(self, trial_df, streak_goal=10, mode="random",
                      fixation_duration=0.3, cue_duration=0.5, goal_rt=2.0,
                      self_paced=True, feedback=True, pause_between_runs=True, decrease=True):
        ''' generic block of trials, with streak goal and pause between runs'''
        self.drawList = []
        start_width_initial = self.start_width if self.show_progress else 0. # progbar
        trials = data.TrialHandler(trial_df, 1, method="sequential")
        self.generateCounterDict(map_type=trials.trialList[0]["map_type"])
        out = []

        if pause_between_runs:
            run_number = 1
            timer = core.CountdownTimer(self.run_length)
            self.optionally_send_trigger("run")

        while not self.streakGoalReached(streak_goal=streak_goal):
            if trials.nRemaining == 0:
                self.terminate(out)

            trial = trials.next()
            # probabilistically skip if this cue has already been mastered
            if self.counter_dict["+".join(trial["map"])] == streak_goal and np.random.random() > 0.2:
                continue

            self.genericTrial(trial, mode=mode, self_paced=self_paced, feedback=feedback,
                              fixation_duration=fixation_duration +
                              trial["jitter"][0],
                              cue_duration=cue_duration + trial["jitter"][1],
                              goal_rt=goal_rt)
            self.updateCounterDict(trial, streak_goal=streak_goal, goal_rt=goal_rt,
                                   decrease=decrease)

            # Update progress bar
            if self.show_progress:
                end_width = start_width_initial + \
                    sum(self.counter_dict.values()) * self.progbar_inc
                self.move_prog_bar(end_width=end_width, wait_s=0)

            # Pause display between runs
            if pause_between_runs:
                trial["run_number"] = run_number
                if timer.getTime() <= 0:
                    self.tPause()
                    timer.reset()
                    run_number += 1
                    self.optionally_send_trigger("run")
            # finally
            out.append(trial)
            core.wait(0.5)
        return out
    

    def adaptiveInterleavedBlock(
        self, trial_df, streak_goals=[1, 1,], mode="random",
        fixation_duration=0.3, cue_durations=[0.5, 1.0,], goal_rt=2.0,
        self_paced=True, feedback=True, pause_between_runs=True, decrease=True):
        ''' interleaved block of trials, with streak goal and pause between runs'''
        self.drawList = []
        start_width_initial = self.start_width if self.show_progress else 0. # progbar
        trials = data.TrialHandler(trial_df, 1, method="random")
        self.generateCounterDict(map_type="all")
        out = []
        queue = []
        requeue_counter = 0

        if pause_between_runs:
            run_number = 1
            timer = core.CountdownTimer(self.run_length)
            self.optionally_send_trigger("run")

        while not self.streakGoalReachedMultiple(streak_goals,
                                                 key_lists=[self.map_names, self.map_names_bin]):
            if trials.nRemaining == 0:
                if len(queue) > 0 and requeue_counter < 2:
                    requeue_counter += 1
                    print(f"No remaining trials, requeue #{requeue_counter}...")
                    trials = data.TrialHandler(queue, 1, method="random")
                    queue = []
                    continue
                else:
                    self.terminate(out)
            trial = trials.next()
            is_primitive = trial["map_type"] == "primitive"
            cue_duration = cue_durations[0] if is_primitive else cue_durations[1]
            streak_goal = streak_goals[0] if is_primitive else streak_goals[1]

            # skip if this cue has already been mastered
            if self.counter_dict["+".join(trial["map"])] == streak_goal:
                print("Skipping mastered spell...")
                queue += [trial]
                continue
            
            self.genericTrial(trial, mode=mode, self_paced=self_paced, feedback=feedback,
                              fixation_duration=fixation_duration + trial["jitter"][0],
                              cue_duration=cue_duration + trial["jitter"][1],
                              goal_rt=goal_rt)
            self.updateCounterDict(trial, streak_goal=streak_goal, goal_rt=goal_rt,
                                   decrease=decrease)

            # Update progress bar
            if self.show_progress:
                end_width = start_width_initial + \
                    sum(self.counter_dict.values()) * self.progbar_inc
                self.move_prog_bar(end_width=end_width, wait_s=0)

            # Pause display between runs
            if pause_between_runs:
                trial["run_number"] = run_number
                if timer.getTime() <= 0:
                    self.tPause()
                    timer.reset()
                    run_number += 1
                    self.optionally_send_trigger("run")
                    
            # finally
            out.append(trial)
            core.wait(0.5)
        return out


    def adaptiveDecoderBlock(self, trial_df,
                             fixation_duration=0.3, cue_duration=0.5, goal_rt=2.0,
                             pause_between_runs=True, test_goal=0, decoderType="spell"):
        ''' block of decoder trials, enqueueing failed trials'''
        assert decoderType in ["spell", "object"]
        self.drawList = []
        if test_goal and not self.test_mode:
            print("WARNING: test goal is only applicable in test mode.")
        start_width_initial = self.start_width if self.show_progress else 0. # progbar
        trials = data.TrialHandler(trial_df, 1, method="sequential")
        succeeded = []
        failed = []
        out = []
        run_number = 1
        
        if pause_between_runs:
            timer = core.CountdownTimer(self.run_length)
            self.optionally_send_trigger("run")

        while trials.nRemaining > 0:
            trial = trials.next()
            trial["run_number"] = run_number

            if decoderType == "spell":
                self.genericTrial(trial, self_paced=True, feedback=True,
                                  fixation_duration=fixation_duration +
                                  trial["jitter"][0],
                                  cue_duration=cue_duration +
                                  trial["jitter"][1],
                                  goal_rt=goal_rt)
            else:
                self.objectDecoderTrial(
                    trial, fixation_duration=fixation_duration + trial["jitter"])

            # Enqueue trials with applicable map according to performance
            out.append(trial)
            correct = trial["correct_resp"] == trial["emp_resp"]

            # Case: spell decoder
            if decoderType == "spell":
                fast = trial["resp_RT"] <= goal_rt
                if trial["applicable"] and not (correct and fast):
                    failed.append(trial)
                    print("# repeat:", len(failed))
                else:
                    succeeded.append(trial)
                    print("# correct:", len(succeeded))
                    
            # Case: object decoder
            elif decoderType == "object":
                if trial["is_catch_trial"] and not correct:
                    failed.append(trial)
                    print("# repeat:", len(failed))
                else:
                    succeeded.append(trial)
                    print("# correct:", len(succeeded))

            # Restart failed trials
            if trials.nRemaining == 0 and len(failed) > 0:
                trials = data.TrialHandler(failed, 1, method="random")
                failed = []

            # Update progress bar
            if self.show_progress:
                end_width = start_width_initial + \
                    len(succeeded) * self.progbar_inc
                self.move_prog_bar(end_width=end_width, wait_s=0)
            if decoderType == "spell":
                core.wait(0.2)

            # During test mode: Terminate if goal is reached
            if self.test_mode and len(out) >= test_goal:
                break
            
            # Pause display between runs
            if pause_between_runs:
                if timer.getTime() <= 0:
                    self.tPause()
                    timer.reset()
                    run_number += 1
                    self.optionally_send_trigger("run")
                    
        return out


    ###########################################################################
    # Introduction Session
    ###########################################################################

    def Session1(self):
        self.win.mouseVisible = False

        # set up probar
        streak_goal = 1 if self.test_mode else 8  # per map
        trial_numbers = [
            len(self.trials_obj_dec) if not self.test_mode else 10,  # object decoder
            self.n_primitives * streak_goal,  # cue practice 1
            self.n_primitives * streak_goal,  # cue practice 2
            self.n_primitives * streak_goal,  # test practice 1
            self.n_primitives * streak_goal,  # test practice 2
            len(self.trials_prim_dec) if not self.test_mode else 6,  # spell decoder
        ]
        milestones = self.setMilestones(
            trial_numbers, weights=[0.1, 1.5, 1.5, 1.0, 1.0, 0.2])
        self.init_progbar(milestones=milestones)

        # Balance out which cue modality is learned first
        id_is_odd = int(self.expInfo["participant"]) % 2  # 1 3 5 ...
        first_modality = "visual" if id_is_odd else "textual"
        second_modality = "textual" if id_is_odd else "visual"
        self.add2meta("first_modality", first_modality)

        # Balance out which test type is learned first
        # 1 2 5 6 ...
        id_is_in_seq = int(self.expInfo["participant"]) % 4 in [1, 2]
        first_test = "count" if id_is_in_seq else "position"
        second_test = "position" if id_is_in_seq else "count"
        self.add2meta("first_test", first_test)
        tFirst = self.tCount if id_is_in_seq else self.tPosition
        tSecond = self.tPosition if id_is_in_seq else self.tCount
        trials_test_0 = self.trials_prim_cue.copy()
        trials_test_1 = self.trials_prim_prac_c.copy() if id_is_in_seq else self.trials_prim_prac_p.copy()
        trials_test_2 = self.trials_prim_prac_p.copy() if id_is_in_seq else self.trials_prim_prac_c.copy()

        # Get Demo trials
        demoTrial0 = data.TrialHandler(trials_test_0[:1], 1, method="sequential").next()
        demoTrial1 = data.TrialHandler(trials_test_1[:1], 1, method="sequential").next()
        demoTrial2 = data.TrialHandler(trials_test_2[:1], 1, method="sequential").next()
        print("Starting Session 1.")

        ''' --- 1. Initial instructions and object decoder ---------------------------'''
        # print("Starting Session 2 with adaptive decoder block.")
        self.set_progbar_inc()

        # Navigation
        self.Instructions(part_key="Navigation1",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMegBF"]
                                if self.meg else self.keyboard_dict["keyBoardArrows"]
                                ],
                          font="mono",
                          fontcolor=self.color_dict["mid_grey"])

        # Object decoder block
        self.Instructions(part_key="objectDecoder",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMegNY"]
                                if self.meg else self.keyboard_dict["keyBoardArrows"]
                                ])
        self.df_out_0 = self.adaptiveDecoderBlock(
            self.trials_obj_dec,
            decoderType="object",
            test_goal=trial_numbers[0],
        )
        fname = self.writeFileName("objectDecoder")
        self.save_object(self.df_out_0, fname, ending='csv')
        self.Instructions(part_key="objectDecoderPost")

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
        print("\nLearning first cue type.")
        self.set_progbar_inc()

        # Learn first cue type
        self.learnDuration_1 = self.learnCues(min_duration=60)
        self.add2meta("learnDuration_1", self.learnDuration_1)

        # Test first cue type
        self.Instructions(part_key="Intermezzo1",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMeg0123"] if self.meg
                                else self.keyboard_dict["keyBoard4"]],
                          complex_displays=[self.cuePracticeTrial],
                          kwargs=[{"trial": demoTrial0, "mode": first_modality, "demonstration": True}],
                          )
        self.df_out_1 = self.adaptiveCuePractice(self.trials_prim_cue,
                                                 streak_goal=streak_goal,
                                                 mode=first_modality)
        fname = self.writeFileName("cueMemory"+first_modality.capitalize())
        self.save_object(self.df_out_1, fname, ending='csv')

        # Learn second cue type
        print("\nLearning second cue type.")
        self.set_progbar_inc()
        self.Instructions(part_key="Intermezzo2",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMeg0123"] if self.meg
                                else self.keyboard_dict["keyBoard4"]],
                          complex_displays=[self.cuePracticeTrial],
                          kwargs=[{"trial": demoTrial0, "mode": second_modality, "demonstration": True}],
                          )
        self.learnDuration_2 = self.learnCues(min_duration=30)
        self.add2meta("learnDuration_2", self.learnDuration_2)

        # Test second cue type
        self.win.flip()
        core.wait(2)
        self.df_out_2 = self.adaptiveCuePractice(self.trials_prim_cue[len(self.df_out_1):],
                                                 streak_goal=streak_goal,
                                                 mode=second_modality)
        fname = self.writeFileName("cueMemory"+second_modality.capitalize())
        self.save_object(self.df_out_2, fname, ending='csv')

        ''' --- 3. Test Types --------------------------------------------------------'''
        # First Test-Type
        print("\nLearning first test type.")
        self.set_progbar_inc()
        self.Instructions(part_key=first_test + "First",
                          special_displays=[self.iSingleImage,
                                            self.tEmptySquares,
                                            self.iSingleImage],
                          args=[self.magicWand,
                                None,
                                self.keyboard_dict["keyBoardMeg0123"] if self.meg
                                else self.keyboard_dict["keyBoard4"]],
                          complex_displays=[self.tInput,
                                            self.tCue,
                                            tFirst],
                          kwargs=[{"trial": demoTrial1, "duration": 0.0},
                                  {"trial": demoTrial1},
                                  {"trial": demoTrial1, "duration": 0.0, "demonstration": True,}],
                          )
        self.df_out_3 = self.adaptiveBlock(trials_test_1, streak_goal=streak_goal)
        fname = self.writeFileName("testPractice"+first_test.capitalize())
        self.save_object(self.df_out_3, fname, ending='csv')

        # Second Test-Type
        print("\nLearning second test type.")
        self.set_progbar_inc()
        self.Instructions(part_key=second_test + "Second",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMeg0123"]
                                if self.meg else self.keyboard_dict["keyBoard4"]],
                          complex_displays=[self.genericTrial,
                                            tSecond],
                          kwargs=[{"trial": demoTrial2, "self_paced": False, "skip_test": True},
                                  {"trial": demoTrial2, "duration": 0.0, "demonstration": True,}])
        self.df_out_4 = self.adaptiveBlock(trials_test_2, streak_goal=streak_goal)
        fname = self.writeFileName("testPractice"+second_test.capitalize())
        self.save_object(self.df_out_4, fname, ending='csv')

        ''' --- 4. Spell Decoder --------------------------------------------------------'''
        print("\nStarting spell decoder trials.")
        self.set_progbar_inc()

        self.Instructions(part_key="spellDecoder",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]])
        self.df_out_5 = self.adaptiveDecoderBlock(
            self.trials_prim_dec,
            test_goal=trial_numbers[-1])
        fname = self.writeFileName("spellDecoder")
        self.save_object(self.df_out_5, fname, ending='csv')

        ''' --- Wrap up --------------------------------------------------------'''
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
        
         # set up probar
        goal_streak_p = 1 if self.test_mode else 20  # single spells
        goal_streak_b = 1 if self.test_mode else 20  # double spells
        trial_numbers = [
            self.n_primitives * goal_streak_p,
            self.n_binaries * goal_streak_b,
            ]
        milestones = self.setMilestones(
            trial_numbers, weights=[1.0, 1.5])
        self.init_progbar(milestones=milestones)
        
        # Demo trials
        demoCount = data.TrialHandler(
            self.trials_prim_prac_c[:1], 1, method="sequential").trialList[0]
        demoPosition = data.TrialHandler(
            self.trials_prim_prac_p[:1], 1, method="sequential").trialList[0]
        demoBin = data.TrialHandler(
            self.trials_bin[:1], 1, method="sequential").trialList[0]
        demoAuto = data.TrialHandler(
            self.trials_auto[:1], 1, method="sequential").trialList[0]

        # Navigation
        self.Instructions(part_key="Navigation3",
                          special_displays=[self.iSingleImage],
                          args=[self.keyboard_dict["keyBoardMegBF"]
                                if self.meg else self.keyboard_dict["keyBoardArrows"]],
                          font="mono",
                          fontcolor=self.color_dict["mid_grey"])
        
        # ''' --- 1. Initial instructions and primitive trials ------------------------'''
        # print("\nStarting adaptive primitive block.")
        # self.set_progbar_inc()
        # self.Instructions(part_key="PrimitivesMEGR",
        #                   special_displays=[self.iSingleImage,
        #                                     self.iSingleImage],
        #                   args=[self.magicWand,
        #                         self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]],
        #                   complex_displays=[self.tInput,
        #                                     self.drawCue,
        #                                     self.tCount,
        #                                     self.tPosition],
        #                   kwargs=[{"trial": demoCount, "duration": 0.0},
        #                           {"trial": demoCount, "duration": 0.0},
        #                           {"trial": demoCount, "duration": 0.0,
        #                               "demonstration": True},
        #                           {"trial": demoPosition, "duration": 0.0, "demonstration": True}])

        # self.df_out_6 = self.adaptiveBlock(self.trials_prim,
        #                                    streak_goal=goal_streak_p)
        # fname = self.writeFileName("primitiveTrials")
        # self.save_object(self.df_out_6, fname, ending='csv')

        # ''' --- 2. Double spell trials ------------------------------------------------'''
        # print("\nStarting adaptive compositional block.")
        # self.set_progbar_inc()
        # self.Instructions(part_key="BinariesMEGR",
        #                   special_displays=[self.iSingleImage,
        #                                     self.iSingleImage],
        #                   args=[self.magicWand,
        #                         self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]],
        #                   complex_displays=[self.tInput,
        #                                     self.drawCue],
        #                   kwargs=[{"trial": demoBin, "duration": 0.0},
        #                           {"trial": demoBin, "duration": 0.0}])
        # self.df_out_7 = self.adaptiveBlock(self.trials_bin,
        #                                    streak_goal=goal_streak_b,
        #                                    cue_duration=1.0)
        # fname = self.writeFileName("compositionalTrials")
        # self.save_object(self.df_out_7, fname, ending='csv')

        
        ''' --- Interleaved spell trials ------------------------------------------------'''
        print("\nStarting adaptive interleaved block.")
        self.Instructions(part_key="InterleavedMEGR",
                          special_displays=[self.iSingleImage,
                                            self.tEmptySquares,
                                            self.iSingleImage],
                          args=[self.magicWand,
                                None,
                                self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]],
                          complex_displays=[self.tInput,
                                            self.tCue,
                                            self.tCount if demoBin["test_type"] == "count" else self.tPosition],
                          kwargs=[{"trial": demoBin, "duration": 0.0},
                                  {"trial": demoBin},
                                  {"trial": demoBin, "duration": 0.0, "demonstration": True,}])
        self.df_out_inter = self.adaptiveInterleavedBlock(
            self.trials_prim + self.trials_bin,
            streak_goals=[goal_streak_p, goal_streak_b], 
            cue_durations=[0.5, 1.0])
        fname = self.writeFileName("interleavedTrials")
        self.save_object(self.df_out_inter, fname, ending='csv')
        
        
        ''' --- Autonomous spell trials ------------------------------------------------'''
        print("\nStarting autonomous block.")
        self.Instructions(part_key="AutonomousMEGR",
                         special_displays=[self.iSingleImage,
                                           self.iSingleImage,
                                           self.tEmptySquares,
                                           self.iSingleImage],
                         args=[self.magicWand,
                               self.qm,
                               None,
                               self.keyboard_dict["keyBoardMeg0123"] if self.meg else self.keyboard_dict["keyBoard4"]],
                         complex_displays=[self.tInput,
                                           self.tCount if demoAuto["test_type"] == "count" else self.tPosition,
                                           self.tSpellOptions,
                                           ],
                         kwargs=[{"trial": demoAuto, "duration": 0.0},
                                 {"trial": demoAuto, "duration": 0.0, "demonstration": True,},
                                 {"demonstration": True},
                                 ])
        
        self.df_out_auto = self.autonomousBlock(self.trials_auto, goal_rt=2.0,
                                                correct_goal = 1 if self.test_mode else 10)
        fname = self.writeFileName("autonomousTrials")
        self.save_object(self.df_out_auto, fname, ending='csv')
                
        
        ''' ---  Finalization '''
        self.move_prog_bar(end_width=1, n_steps=50, wait_s=0)
        self.Instructions(part_key="ByeBye")
        self.add2meta("t_end", data.getDateStr())
        self.win.close()
