#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 12:00:24 2021

@author: alex
"""

import os, glob, pickle
from string import ascii_uppercase
import numpy as np
import pandas as pd
from psychopy import core, visual, gui, data, event, logging
from psychopy.tools.filetools import toFile

# set directories
main_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(main_dir)
stim_dir = os.path.join(main_dir, "stimuli")
trial_list_dir = os.path.join(main_dir, "trial-lists")
if not os.path.exists(trial_list_dir):
    exec(open("generate_trial_lists.py").read())
data_dir = os.path.join(main_dir, "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

#=============================================================================
# Helper Functions
#=============================================================================
# Positions ------------------------------------------------------------------
def rectangularGrindPositions(center_pos = [0, 0],
                              v_dist = 10, h_dist = 10, dim = (2, 3)):
    # horizontal positions
    c = np.floor(dim[1]/2)
    if dim[1] % 2 != 0: # odd number of items on vertical tile => center
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
    else: # even number of items on horizontal tile => shift upwards
        rect_vpos = np.arange(-c * v_dist + v_dist/2 + center_pos[1],
                              c * v_dist  - v_dist/2 + center_pos[1] + 1,
                              v_dist).tolist()
    
    # combine
    rect_pos = np.transpose([np.tile(rect_hpos, len(rect_vpos)),
                                np.repeat(rect_vpos, len(rect_hpos))])
    return rect_pos


def circularGridPositions(center_pos = [0, 0], set_size = 6, radius = 10):
    angle = 2*np.pi/set_size
    rect_pos = np.empty((set_size, 2), dtype=float).copy()
    for i in range(set_size):
        rect_pos[i] = [center_pos[0] + radius * np.sin(i * angle),
                       center_pos[1] + radius * np.cos(i * angle)]
    return rect_pos

# Trial Components ------------------------------------------------------------
def tFixation():
    fixation.draw()
    win.flip()
    core.wait(0.3)

def setCue(key, mode = "random"):
    # opt: randomize mode
    if mode == "random":
        if np.random.randint(0, 2) == 1:
            mode = "textual"
        else:
            mode = "visual"
    # draw from resp. dict
    if mode == "visual":
        cue = vcue_dict.copy()[key]
    elif mode == "textual":
        cue = tcue_dict.copy()[key]
    return cue, mode

def tMapcue(trial, mode = "random", 
            # with_background = False,  # would need flexible background 
            duration = 0.5): 
    assert mode in ["visual", "textual", "random"],\
        "Chosen cue mode not implemented."
    # if with_background:
    #     rect.pos = center_pos
    #     rect.size = center_size
    #     rect.draw()
    n_cues = len(trial.map)    
    for i in range(n_cues):
        cue, mode = setCue(trial.map[i], mode = mode)
        if n_cues > 1: # move first cue up and the third cue down 6 degrees
            cue.pos = [sum(x) for x in zip(center_pos, [0, (1-i)*6])] 
        cue.draw()
    win.flip()
    core.wait(duration)
    return mode

def tDisplay(trial, duration = 1):
    # draw rectangles
    rect.size = normal_size
    for pos in rect_pos:
            rect.pos = pos
            rect.draw()
    
    # draw stimuli
    for i in range(set_size):
        stim = stim_dict.copy()[trial.input_disp[i]]
        stim.pos = rect_pos[i]
        stim.draw()
    win.flip()
    IRClock = core.Clock()
    core.wait(duration) 
    return(IRClock)


def tEmpty(trial, IRClock):
    for pos in rect_pos:
            rect.pos = pos
            rect.draw()
    win.flip()
    # get intermediate response
    intermediateResp = None
    while intermediateResp == None:
        allKeys = event.waitKeys()
        for thisKey in allKeys:
            if thisKey == "space": 
                intermediateRT = IRClock.getTime()
                intermediateResp = 1
            elif thisKey in ["escape"]:
                core.quit()  # abort experiment
        event.clearEvents()
    return(intermediateRT)
   

def tCount(trial, feedback = False):
    TestClock = core.Clock()
    for inc in range(2 + feedback*1):
        rect.pos = center_pos
        rect.size = center_size
        rect.draw()
        rect.size = normal_size
        rect.lineColor = color_dict["dark_grey"]
        stim = stim_dict.copy()[trial.target]
        stim.pos = center_pos
        stim.size = center_size
        stim.draw()
        stim.size = normal_size
        for i in range(len(resp_pos)):
            rect.pos = resp_pos[i]
            rect.draw()
            resp = count_dict[str(i)]
            resp.pos = resp_pos[i]
            resp.draw()
        
        # First cycle: Display stimuli
        if inc == 0:
            win.flip()
            continue
        
        # Second cycle: Get test response
        if inc == 1:
            testRT, testResp = tTestresponse(TestClock, resp_keys)
        
        # Third cycle: Feedback                                                     
        # immedeate feedback
        if feedback:
            rect.pos = resp_pos[testResp]
            if trial.correct_resp == testResp:
                rect.lineColor = color_dict["green"]
            else:
                rect.lineColor = color_dict["red"]
            rect.draw()
            rect.lineColor = color_dict["dark_grey"]
            resp = count_dict[str(testResp)]
            resp.pos = resp_pos[testResp]
            resp.draw()
            if inc == 1:
                win.flip()
                continue
        
            # correct solution 
            if trial.correct_resp != testResp:
                corResp = trial.correct_resp
                rect.pos = resp_pos[corResp]
                rect.fillColor = color_dict["blue"]
                rect.draw()
                rect.fillColor = color_dict["light_grey"]
                resp = count_dict[str(corResp)]
                resp.pos = resp_pos[corResp]
                resp.draw()
                core.wait(1)
                if inc == 2:
                    win.flip()        
    return testRT, testResp

def tPosition(trial, feedback = False):
    TestClock = core.Clock()
    for inc in range(2 + feedback*1):
        # position cues
        for i in range(len(rect_pos)):
            rect.pos = rect_pos[i]
            if trial.target == i:
                qm.pos = rect_pos[i]
            rect.draw()
            rect.lineColor = color_dict["dark_grey"]
        qm.draw()
        
        # response options
        for i in range(len(resp_pos)):
            rect.pos = resp_pos[i]
            rect.draw()
            resp = stim_dict.copy()[trial.resp_options[i]]
            resp.pos = resp_pos[i]
            resp.draw()
        
        # First cycle: Display stimuli
        if inc == 0:
            win.flip()
            continue
        
        # Second cycle: Get test response
        if inc == 1:
            testRT, testResp = tTestresponse(TestClock, resp_keys)
        
        # Third cycle: Feedback                                                     
        # immedeate feedback
        if feedback:
            rect.pos = resp_pos[testResp]
            if trial.correct_resp == testResp:
                rect.lineColor = color_dict["green"]
            else:
                rect.lineColor = color_dict["red"]
            rect.draw()
            rect.lineColor = color_dict["dark_grey"]
            resp = stim_dict.copy()[trial.resp_options[testResp]]
            resp.pos = resp_pos[testResp]
            resp.draw()
            if inc == 1:
                win.flip()
                continue
        
        # correct solution 
            if trial.correct_resp != testResp:
                corResp = trial.correct_resp
                rect.pos = resp_pos[corResp]
                rect.fillColor = color_dict["blue"]
                rect.draw()
                rect.fillColor = color_dict["light_grey"]
                resp = stim_dict.copy()[trial.resp_options[corResp]]
                resp.pos = resp_pos[corResp]
                resp.draw()
                core.wait(1)
                if inc == 2:
                    win.flip()
    return testRT, testResp
            

def tTestresponse(TestClock, respKeys, return_numeric = True,
                  max_wait = np.inf):
    testResp = None
    testRT = None
    while testResp is None:
        allKeys = event.waitKeys(maxWait = max_wait)
        if allKeys is None and max_wait < np.inf:
            break
        else:
            for thisKey in allKeys:
                if thisKey in respKeys: 
                    testRT = TestClock.getTime()
                    if return_numeric:
                        testResp = np.where(respKeys == thisKey)[0][0]
                    else:
                        testResp = thisKey
                elif thisKey in ["escape"]:
                    core.quit()  # abort experiment
            event.clearEvents()      
    return(testRT, testResp)


def iSingleImage(*args):
    for arg in args:
        arg.pos = [0, 0]
        # arg.size = [10, 10]
        arg.draw()
        win.flip()
        core.wait(0.2)


def iTransmutableObjects(*args):
    categories = list(stim_dict.keys())
    if len(categories) > 4:
        dim = [2, np.ceil(len(categories)/2)]
    else:
        dim = [1, len(categories)]
        
    category_pos = rectangularGrindPositions(
        center_pos = [0, 0], h_dist = 10, dim = dim)

    # draw categories
    for i in range(len(categories)):
        rect.pos = category_pos[i]
        rect.draw()
        stim = stim_dict.copy()[categories[i]]
        stim.pos = category_pos[i]
        stim.draw()
    win.flip()


def iSpellExample(*displays, show_output = True):
    # Input Display
    for i in range(2):
        rect_pos = circularGridPositions(center_pos = [0, 0],
                                 set_size = len(displays[0]), radius = 8)
        for j in range(len(displays[0])):
            rect.pos = rect_pos[j]
            rect.draw()
            stim = stim_dict.copy()[displays[0][j]]
            stim.pos = rect_pos[j]
            stim.draw()
        if i == 0:
            win.flip()
            core.wait(1)
            continue
        
        cue = magicWand
        cue.height = 2
        cue.draw()
        if i == 1:
            win.flip()
            core.wait(1)
    
    if show_output:
        # Output Display
        rect_pos = circularGridPositions(center_pos = [0, 0],
                                     set_size = len(displays[1]), radius = 8)
        for j in range(len(displays[1])):
            rect.pos = rect_pos[j]
            rect.draw()
            stim = stim_dict.copy()[displays[1][j]]
            stim.pos = rect_pos[j]
            stim.draw()
        win.flip()
        core.wait(1)
 

def iNavigate(page = 0, max_page = 99, continue_after_last_page = True,
              proceed_key = "/k", wait_s = 3):
    
    assert proceed_key in ["/k", "/t", "/e"], "Unkown proceed key"
    finished = False
    testResp = None
    TestClock = core.Clock()
    
    # get response or wait or something in between
    if proceed_key == "/k": #keypress
        _, testResp = tTestresponse(TestClock, ["left", "right", "space"],
                                    return_numeric = False)
    elif proceed_key == "/t": #time
        core.wait(wait_s)
        testResp = "right"
    elif proceed_key == "/e": #either
        _, testResp = tTestresponse(TestClock, ["left", "right", "space"],
                                    return_numeric = False,
                                    max_wait = wait_s)
        if testResp is None:
            testResp = "right"
            
    # Proceed accordingly    
    if testResp == "right":
        if page < max_page-1:
            page +=1
        elif continue_after_last_page:
            finished = True
    elif testResp == "left" and page > 0:
        page -= 1
    elif testResp == "space":
        nextPrompt.draw()
        win.flip()
        _, contResp = tTestresponse(TestClock, ["return", "space"],
                                    return_numeric = False)
        if contResp == "space":
            finished = False
        elif  contResp == "return":
            finished = True  
    return page, finished 
    
# Blocks and Loops-------------------------------------------------------------

def Instructions(part_key = "Intro", special_displays = list(), args = list(),
                 font = "Times New Roman", fontcolor = [-0.9, -0.9, -0.9]):
    assert len(special_displays) == len(args),\
        "Number of special displays must match the number of args"
    assert part_key in instructions.keys(),\
        "No instructions provided for this part"
        
    # Initialize parameters
    finished = False
    Part = instructions[part_key]
    page = 0
    win.flip()
    while not finished:
        page_content = Part[page][0]
        proceed_key = Part[page][1]
        proceed_wait = Part[page][2]
        if type(page_content) is str:
            textStim = visual.TextStim(
                        win,
                        text = page_content,
                        font = font,
                        height = 1.8,
                        wrapWidth = 30,
                        color = fontcolor)
            textStim.draw()
            win.flip()
        elif type(page_content) is int:
            special_displays[page_content](*args[page_content])
        page, finished = iNavigate(page = page, max_page = len(Part),
                                   proceed_key = proceed_key,
                                   wait_s = proceed_wait)
        
              
def LearnCues(center_pos = [0, -6], mode = "random"):
    # Initialize parameters
    win.flip()
    LearnClock = core.Clock()
    finished = False
    page = 0
    category_pos = rectangularGrindPositions(
        center_pos = center_pos, h_dist = 15, dim = (1, 2))
    
    while not finished:
        # Draw map cue
        map_name = map_names[page]
        categories = map_name.split("-")
        cue, _ = setCue(map_name, mode = mode)
        cue.draw()
        
        # Draw corresponding explicit map
        for i in range(len(categories)):
            rect.pos = category_pos[i]
            rect.draw()
            cat = stim_dict.copy()[categories[i]]
            cat.pos = category_pos[i]
            cat.draw()
        leftArrow.pos = center_pos
        leftArrow.draw()
        win.flip()
        core.wait(0.2)
        
        page, finished = iNavigate(page = page, max_page = len(map_names),
                                   continue_after_last_page = False)  
    # Save learning duration
    learnDuration = LearnClock.getTime()       
    return learnDuration    


def PracticeCues(trials_prim_cue, mode = "visual"):
    # create the trial handler
    PracticeCueTrials = data.TrialHandler(
        trials_prim_cue.to_dict("records"), 1, method="sequential")
    testRespSuperList = []
    testRTSuperList = []
    cueTypeList = []
    
    for trial in PracticeCueTrials:
        num_cr = len(trial.correct_resp)
        testRespList = []
        testRTList = []
        j = 0
        cue, cue_type = setCue(trial.map[0], mode = mode)
        cueTypeList.append(cue_type)
        
        # Incrementally display stuff
        for inc in range(3 + 2 * num_cr): 
        
            # 0. Fixation
            if inc == 0: 
                tFixation()
                win.flip()
                continue
            
            # 1. Map Cue
            cue.draw()
            if inc == 1:
                win.flip()
                core.wait(0.5)
                continue
            
            # 2. Response options
            rect.lineColor = color_dict["dark_grey"]
            for i in range(len(cuepractice_pos)):
                rect.pos = cuepractice_pos[i]
                rect.draw()
                resp = stim_dict.copy()[trial.resp_options[i]]
                resp.pos = cuepractice_pos[i]
                resp.draw()
            if inc == 2:
                win.flip()
                continue
            
            # 3. - 3 + num_cr: Immediate Feedback
            if inc in list(range(3, 3 + num_cr)):
                TestClock = core.Clock()
                testRT, testResp = tTestresponse(TestClock, resp_keys_wide)
                testRTList.append(testRT)
                testRespList.append(testResp)
            for i in range(len(testRespList)):
                testResp = testRespList[i]
                rect.pos = cuepractice_pos[testResp]
                if trial.correct_resp[i] == testResp:
                    rect.lineColor = color_dict["green"]
                else:
                    rect.lineColor = color_dict["red"]
                rect.draw()
                rect.lineColor = color_dict["dark_grey"]
                resp = stim_dict.copy()[trial.resp_options[testResp]]
                resp.pos = cuepractice_pos[testResp]
                resp.draw()
            
            if inc in list(range(3, 3 + num_cr)):
                win.flip()
                continue
            
            # 4. If errors were made, draw correct response
            if trial.correct_resp != testRespList:
                core.wait(1)
                for i in range(1 + j):
                    corResp = trial.correct_resp[i]
                    rect.pos = cuepractice_pos[corResp]
                    rect.fillColor = color_dict["blue"]
                    rect.draw()
                    rect.fillColor = color_dict["light_grey"]
                    resp = stim_dict.copy()[trial.resp_options[corResp]]
                    resp.pos = cuepractice_pos[corResp]
                    resp.draw()
            if inc in list(range(3 + num_cr, 3 + 2 * num_cr - 1)):
                j += 1
                win.flip()
                continue
            else:
                testRTSuperList.append(testRTList)
                testRespSuperList.append(testRespList)
                win.flip()
                core.wait(2)
    trials_prim_cue["emp_resp"] = testRespSuperList
    trials_prim_cue["resp_RT"] = testRTSuperList
    trials_prim_cue["cue_type"] = cueTypeList
    return trials_prim_cue
            
    
def GenericBlock(trial_df, mode = "random", i = 0, i_step = None,
                 durations = [0.5, 1, 0.3, 1, 0.7], test = True, feedback = False):
    # create the trial handler
    if i_step is None:  
        i_step = len(trial_df)
    df = trial_df[i:i+i_step].copy()
    trials = data.TrialHandler(
        df.to_dict("records"), 1, method="sequential")
    intermediateRTList = []
    testRespList = []
    testRTList = []
    cueTypeList = []
    
    for trial in trials:
        # 0. Clear display
        win.flip()
        
        # 1. Fixation
        tFixation()
        
        # 2. Map Cue
        cue_type = tMapcue(trial, mode = mode, duration = durations[0])
        
        # 3. Display Family
        IRClock = tDisplay(trial, duration = durations[1])
        
        if test:
            # 4. Transformation Display
            intermediateRT = tEmpty(trial, IRClock)
            trials.addData("intermediateRT", intermediateRT)
        
            # 5. Empty Display
            win.flip()
            core.wait(durations[2])
            
            # 6. Test Display
            if trial.test_type == "count":
                testRT, testResp = tCount(trial, feedback = feedback)
            elif trial.test_type == "position":
                testRT, testResp = tPosition(trial, feedback = feedback)
                
            # 7. Save data
            intermediateRTList.append(intermediateRT)
            testRespList.append(testResp)
            testRTList.append(testRT)
            cueTypeList.append(cue_type)
            core.wait(durations[3])
        win.flip()
        win.flip()
        core.wait(durations[4])
        
    # append trial list with collected data 
    if test:
        df["cue_type"] = cueTypeList
        df["inter_RT"] = intermediateRTList
        df["emp_resp"] = testRespList
        df["resp_RT"] = testRTList
    return df


def CuePracticeLoop(trials_prim_cue, 
                    min_acc = 0.85, mode = "random", i = 0, i_step = 30):
    mean_acc = 0.0
    df_list = []
    while mean_acc < min_acc:
        df = trials_prim_cue[i:i+i_step].copy()
        df_list.append(PracticeCues(df, mode = mode))
        errors = (df.correct_resp == df.emp_resp).to_list()
        mean_acc = np.mean(list(map(int, errors))) # convert to integers
        
        accPrompt = visual.TextStim(
            win, text = str(np.round(mean_acc * 100)) +"%",
            height = 2.5,
            wrapWidth = 30,
            font = "Times New Roman",
            color = color_dict["black"])
        
        # repeat or wrap up
        i += i_step    
        if mean_acc < min_acc:
            feedbacktype = "Feedback0" 
        else: 
            feedbacktype = "Feedback1"  
        Instructions(part_key = feedbacktype,
                 special_displays = [iSingleImage], args = [[accPrompt]])            
    df_out = pd.concat(df_list)
    return df_out


def TestPracticeLoop(trial_df, 
                     min_acc = 0.9, mode = "random", i = 0, i_step = 30,
                     durations = [0.5, 1, 0.3, 1, 0.7], 
                     test = True, feedback = False):
    mean_acc = 0.0
    df_list = []
    while mean_acc < min_acc:
        df = GenericBlock(trial_df, mode = mode, i = i, i_step = i_step,
                 durations = durations, test = test, feedback = feedback)
        df_list.append(df)
        errors = (df.correct_resp == df.emp_resp).to_list()
        mean_acc = np.mean(list(map(int, errors))) # convert to integers
        
        accPrompt = visual.TextStim(
            win, text = str(np.round(mean_acc * 100)) +"%", height = 2.5,
            wrapWidth = 30, font = "Times New Roman",
            color = color_dict["black"])
        
        # repeat or wrap up
        i += i_step    
        if mean_acc < min_acc:
            feedbacktype = "Feedback0" 
        else: 
            feedbacktype = "Feedback1"  
        Instructions(part_key = feedbacktype,
                 special_displays = [iSingleImage], args = [[accPrompt]])            
    df_out = pd.concat(df_list)
    return df_out    


#=============================================================================
# Prepare Experiment
#=============================================================================
# Create main window
win = visual.Window(
    # [2560, 1440],
    [1920, 1080],
    # [800, 600],
    fullscr = False,
    color = [0.85, 0.85, 0.85],
    screen = 1,
    monitor = "testMonitor",
    units = "deg")

# Store info about the experiment session
psychopyVersion = "2021.1.4"
expName = "compositionalInference"
expInfo = {"participant": "01", "session": "01"}
expInfo["dateStr"] = data.getDateStr()  # add the current time
expInfo["psychopyVersion"] = psychopyVersion
expInfo["frameRate"] = win.getActualFrameRate()
if expInfo["frameRate"] != None:
    frameDur = 1.0 / round(expInfo["frameRate"])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

# Dialogue Box
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys = False, title = expName)
if dlg.OK:
    toFile(data_dir + os.sep + expInfo["participant"] +
           "_participantParams.pkl", expInfo)
else:
    core.quit()  # the user hit cancel so exit

# Save data to this file later
fileName = main_dir + os.sep + u"data/%s_%s_%s" %(expInfo["participant"],
                                                  expName, expInfo["dateStr"])
# # Log file for detail verbose info
# logFile = logging.LogFile(fileName + ".log", level = logging.EXP)
# logging.console.setLevel(logging.WARNING) 

# Load instructions
with open(stim_dir + os.sep + "instructions_en.pkl", "rb") as handle:
    instructions = pickle.load(handle)

# Load triallists and adapt setup to their parameters
trials_prim_cue = pd.read_pickle(
    os.path.join(trial_list_dir, expInfo["participant"] +
                 "_trials_prim_cue.pkl"))
trials_prim_prac_c = pd.read_pickle(
    os.path.join(trial_list_dir, expInfo["participant"] +
                 "_trials_prim_prac_c.pkl"))
trials_prim_prac_p = pd.read_pickle(
    os.path.join(trial_list_dir, expInfo["participant"] +
                 "_trials_prim_prac_p.pkl"))
trials_prim = pd.read_pickle(
    os.path.join(trial_list_dir, expInfo["participant"] +
                 "_trials_prim.pkl"))
trials_bin = pd.read_pickle(
    os.path.join(trial_list_dir, expInfo["participant"] +
                 "_trials_bin.pkl"))
    
with open(trial_list_dir + os.sep + expInfo["participant"] +
          "_mappinglists.pkl", "rb") as handle:
    mappinglists = pickle.load(handle)
    
set_size = len(trials_prim.input_disp[0])
n_cats = len(np.unique(trials_prim.input_disp.to_list()))
n_resp = len(trials_prim.resp_options[0])
map_names = np.unique(trials_prim.map.to_list())

# set colors
color_dict = {"light_grey": [0.7, 0.7, 0.7],
              "mid_grey": [0, 0, 0],
              "dark_grey": [-0.6, -0.6, -0.6],
              "black": [-0.9, -0.9, -0.9],
              "red": [1, 0, 0],
              "green": [0, 1, 0],
              "blue": [0, 0, 1]
              }

# set positions 
resp_keys = np.array(["d", "f", "j", "k"])
resp_keys_wide = np.array(["s", "d", "f", "j", "k", "l"])
center_pos = [0, 5]
center_size = [8, 8]
vcue_size = [7, 7]
normal_size = [5, 5]
# rect_pos = rectangularGrindPositions(center_pos, h_dist = 10, dim = (2, 3))
rect_pos = circularGridPositions(center_pos = center_pos,
                                 set_size = set_size, radius = 7)
resp_pos = rectangularGrindPositions(center_pos = [0, -10],
                                     h_dist = 10, dim = (1, 4))
cuepractice_pos = rectangularGrindPositions(center_pos = [0, -8],
                                            h_dist = 8, dim = (1, 6))


#=============================================================================
# Prepare Visual Objects
#=============================================================================

rect = visual.Rect(
    win = win,
    units = "deg",
    width = 6,
    height = 6,
    fillColor = color_dict["light_grey"],
    lineColor = color_dict["dark_grey"])

fixation = visual.GratingStim(
    win, color = -0.9,
    colorSpace = "rgb",
    pos = center_pos,
    mask = "circle",
    size = 0.2)

# Textual cues  
tcue_list = mappinglists["tcue"]
assert len(tcue_list) == len(map_names)
spellname_dict = dict(zip(tcue_list, map_names))
tcue_dict = {}

for i in range(len(map_names)):
    cue_name = map_names[i]
    tcue_dict.update({cue_name:visual.TextStim(win,
                                               text = tcue_list[i],
                                               pos = center_pos,
                                               height = 4,
                                               color = color_dict["black"])})

# Visual cues
vcue_list = glob.glob(stim_dir + os.sep + "c_*.png")
vcue_list = mappinglists["vcue"]
assert len(vcue_list) >= len(map_names)
vcue_dict = {}
for i in range(len(map_names)):
    cue_name = map_names[i]
    vcue_dict.update({cue_name:visual.ImageStim(win,
                                                image = vcue_list[i],
                                                pos = center_pos,
                                                size = vcue_size,
                                                interpolate = True)})
    
# Stimuli
stim_list = mappinglists["stim"]
assert len(stim_list) >= n_cats
stim_dict = {}
for i in range(n_cats):
    stim_name = ascii_uppercase[i]
    stim_dict.update({stim_name:visual.ImageStim(win,
                                                 image=stim_list[i],
                                                 size = normal_size,
                                                 interpolate = True)})

# Count responses
count_dict = {}
for i in range(n_resp):
    count_dict.update({str(i):visual.TextStim(win,
                                             text = str(i),
                                             height = 4,
                                             color= color_dict["black"])})
    
# Keyboard prompts
keyboard_dict = {}
keyboard_list = glob.glob(stim_dir + os.sep + "keyBoard*.png")
for i in range(len(keyboard_list)):
    key_name = os.path.basename(
        os.path.normpath(keyboard_list[i])).split(".")[0]
    keyboard_dict.update({key_name: visual.ImageStim(win,
                                                image = keyboard_list[i],
                                                size = [40, 20],
                                                interpolate = True)})
    
# Misc. Stimuli    
qm = visual.TextStim(win,
                     text = "?",
                     height = 4,
                     color = color_dict["black"])  
    
nextPrompt = visual.TextStim(
    win, text = "Press Spacebar to go back \nor press the Enter key to"\
        " continue to next section.",
    height = 1.5,
    wrapWidth = 30,
    font = "mono",
    color = color_dict["mid_grey"]) 

leftArrow = visual.ImageStim(
    win, image = glob.glob(stim_dir + os.sep + "leftArrow.png")[0],
    size = normal_size, interpolate = True)

magicWand = visual.ImageStim(
    win, image = glob.glob(stim_dir + os.sep + "magicWand.png")[0],
    size = normal_size, interpolate = True)

philbertine = visual.ImageStim(
    win, image = glob.glob(stim_dir + os.sep + "philbertine.png")[0],
    units = "pix",
    size = [400, 400], interpolate = True)

magicBooks = visual.ImageStim(
    win, image = glob.glob(stim_dir + os.sep + "magicBooks.png")[0],
    units = "pix",
    size = [640, 575], interpolate = True)


##############################################################################
# Introduction Session
##############################################################################
# Global clock
globalClock = core.Clock()

# # Navigation
# Instructions(part_key = "Navigation",
#              special_displays = [iSingleImage,
#                                  iSingleImage], 
#              args = [[keyboard_dict["keyBoardArrows"]],
#                      [keyboard_dict["keyBoardEsc"]]],
#              font = "mono",
#              fontcolor = color_dict["mid_grey"])

# # Introduction
# Instructions(part_key = "Intro",
#              special_displays = [iSingleImage,
#                                  iSingleImage,
#                                  iTransmutableObjects,
#                                  iSpellExample,
#                                  iSpellExample], 
#              args = [[magicBooks],
#                      [philbertine],
#                      [None],
#                      [["A", "B", "C", "C", "E", "C"],
#                       ["A", "E", "C", "C", "E", "C"]],
#                      [["B", "A", "C", "B", "B", "D"],
#                       ["E", "A", "C", "E", "E", "D"]]]
#                      )

# ----------------------------------------------------------------------------
# # Balance out which cue modality is learned first
# if int(expInfo["participant"]) % 2 == 0:
#     first_modality = "visual"
#     second_modality = "textual"
# else:
#     first_modality = "textual"
#     second_modality = "visual"
    
# # Cue Memory: First modality
# Instructions(part_key = first_modality + "First",
#              special_displays = [iSingleImage], 
#              args = [[keyboard_dict["keyBoardSpacebar"]]])
# learnDuration = LearnCues(mode = first_modality)                                     
# Instructions(part_key = "Intermezzo1",
#              special_displays = [iSingleImage], 
#              args = [[keyboard_dict["keyBoard6"]]])
# df_out_1 = CuePracticeLoop(trials_prim_cue, 
#                            mode = first_modality, 
#                            i_step = 20
#                            )   

# # Cue Memory: Second modality
# Instructions(part_key = second_modality + "Second")
# learnDuration = LearnCues(mode = second_modality)
# Instructions(part_key = "Intermezzo2")
# df_out_2 = CuePracticeLoop(trials_prim_cue, 
#                            mode = second_modality, 
#                            i = len(df_out_1),
#                            i_step = 20
#                            )

# # Save cue memory data
# pd.concat([df_out_1, df_out_2]).reset_index(drop=True).to_pickle(
#     data_dir + os.sep + expInfo["participant"] + "_" + "cueMemory.pkl") 

# ----------------------------------------------------------------------------
# Balance out which test type is learned first
if int(expInfo["participant"]) % 2 == 0:
    first_test = "count"
    trials_test_1 = trials_prim_prac_c.copy()
    second_test = "position"
    trials_test_2 = trials_prim_prac_p.copy()
else:
    first_test = "position"
    trials_test_1 = trials_prim_prac_p.copy()
    second_test = "count"
    trials_test_2 = trials_prim_prac_c.copy()
    
# Test-Type: Position
Instructions(part_key = "TestTypes",
             special_displays = [iSingleImage], 
             args = [[magicWand]])
GenericBlock(trials_prim_prac_p,
             i_step = 1,
             durations = [1, 3, 0.6, 0, 0],
             test = False)         
Instructions(part_key = first_test + "First",
             special_displays = [iSingleImage], 
             args = [[keyboard_dict["keyBoard4"]]])
df_out_3 = TestPracticeLoop(trials_test_1,
                            i_step = 3,
                            durations = [1, 3, 0.6, 1, 0.7], 
                            feedback = True)
Instructions(part_key = "Faster")
df_out_3 = TestPracticeLoop(trials_test_1,
                            i = len(df_out_3),
                            feedback = True)

# Test-Type: Counting
Instructions(part_key = second_test + "Second")
df_out_4 = TestPracticeLoop(trials_test_2, 
                 i_step = 2, durations = [1, 3, 0.6, 1, 0.7],  feedback = True)
Instructions(part_key = "Faster")
df_out_4 = TestPracticeLoop(trials_test_2, 
                            i = len(df_out_4),
                            feedback = True)

# Save test type data
pd.concat([df_out_3, df_out_4]).reset_index(drop=True).to_pickle(
    data_dir + os.sep + expInfo["participant"] + "_" + "testType.pkl") 

# ----------------------------------------------------------------------------
# Practice: Primitive
Instructions(part_key = "Primitives",
             special_displays = [iSingleImage], 
             args = [[magicWand]])
# GenericBlock(trials_prim, mode = "random")
df_out_5 = TestPracticeLoop(trials_prim,
                            min_acc = 0.8,
                            feedback = True)
# Practice: Binary
Instructions(part_key = "Binaries")
df_out_6 = GenericBlock(trials_bin,
                        i_step = 10,
                        durations = [2, 3, 0.6, 1, 0.7],
                        feedback = True)
Instructions(part_key = "Bye")
win.close()
