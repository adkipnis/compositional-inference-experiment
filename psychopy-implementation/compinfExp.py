#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 12:00:24 2021

@author: alex
"""

import os, glob, pickle, sys, csv
from string import ascii_uppercase
import numpy as np
from psychopy import core, visual, gui, data, event, logging
from psychopy.tools.filetools import toFile

# set directories
main_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(main_dir)
trial_list_dir = os.path.join(main_dir, "trial-lists")
if not os.path.exists(trial_list_dir):
    import generate_trial_lists
stim_dir = os.path.join(main_dir, "stimuli")
sys.path.insert(0, './stimuli')
import instructions_en

data_dir = os.path.join(main_dir, "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

#=============================================================================
# Helper Functions
#=============================================================================
def readpkl(fname):
    with open(fname) as f:
        listofdicts = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]
    return listofdicts

def listofdicts2csv(listofdicts, fname):
    keys = listofdicts[0].keys()
    with open(fname, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(listofdicts)

def save_object(obj, fname, ending = 'pkl'):
    if ending == 'csv':
        listofdicts2csv(obj, fname + '.csv')
    elif ending == 'pkl':
        with open(fname + '.pkl', "wb") as f:
            pickle.dump(obj, f)

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

# Background Components -------------------------------------------------------
def draw_background():
    progBack.draw()
    progTest.draw()
    
def move_prog_bar_step(bar_len_step):
    progTest.width += bar_len_step                                              # incrementally increase the bar width 
    progTest.pos[0] = left_corner + progTest.width/2                            # re-center it accordingly on X-coordinate
    progBack.draw()
    progTest.draw()
    win.flip()
    return progTest

def move_prog_bar(start_width = 0, end_width = 1, n_steps = 100, wait_s = 0.75):
    # Setup starting state of progress bar
    progTest = visual.Rect(win, width = start_width * progBack.width,
                           height = bar_height, pos = bar_pos,
                           fillColor = 'green')
    progTest.pos[0] = left_corner + start_width * progBack.width/2
    bar_len_step = bar_len/n_steps
    
    # First display
    progBack.draw()
    progTest.draw()
    win.flip()
    core.wait(wait_s)
    
    # Growing
    while progTest.width < progBack.width * end_width:
        progTest = move_prog_bar_step(bar_len_step)
    
    # Last bit for completion
    progTest = move_prog_bar_step(progBack.width * end_width - progTest.width)
    core.wait(1.5 * wait_s)
    return progTest, progTest.width/progBack.width


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
        else:
            cue.pos = center_pos
        cue.draw()
    win.flip()
    core.wait(duration)
    return mode

def getIR(IRClock):
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
    return intermediateRT
        

def tDisplay(trial, duration = 1, self_paced = False):
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
    if self_paced:
        getIR(IRClock)
    else:
        core.wait(duration) 
    return(IRClock)


def tEmpty(trial, IRClock):
    for pos in rect_pos:
            rect.pos = pos
            rect.draw()
    win.flip()
    intermediateRT = getIR(IRClock)
    return(intermediateRT)
   

def tCount(trial, feedback = False, demonstration = False):
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
            if not demonstration:
                testRT, testResp = tTestresponse(TestClock, resp_keys)
            else:
                badoptions = np.array(range(4))
                np.delete(badoptions, trial.correct_resp)
                core.wait(1)
                testRT, testResp = 0, badoptions[0]
        
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

def tPosition(trial, feedback = False, demonstration = False):
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
            if not demonstration:
                testRT, testResp = tTestresponse(TestClock, resp_keys)
            else:
                badoptions = np.array(range(4))
                np.delete(badoptions, trial.correct_resp)
                core.wait(1)
                testRT, testResp = 0, badoptions[0]
        
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


def iSingleImage(*args, show_background = True):
    for arg in args:
        arg.pos = [0, 0]
        # arg.size = [10, 10]
        arg.draw()
        if show_background: draw_background()
        win.flip()
        core.wait(0.2)


def iTransmutableObjects(*args, show_background = True):
    if show_background: draw_background()
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


def iSpellExample(displays, show_background = True):
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
            if show_background: draw_background()
            win.flip()
            core.wait(1)
            continue
        
        cue = magicWand
        cue.height = 2
        cue.draw()
        if i == 1:
            if show_background: draw_background()
            win.flip()
            core.wait(1)
    
    if len(displays) > 1:
        # Output Display
        rect_pos = circularGridPositions(center_pos = [0, 0],
                                     set_size = len(displays[1]), radius = 8)
        for j in range(len(displays[1])):
            rect.pos = rect_pos[j]
            rect.draw()
            stim = stim_dict.copy()[displays[1][j]]
            stim.pos = rect_pos[j]
            stim.draw()
        if show_background: draw_background()
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

def Instructions(part_key = "Intro",
                 special_displays = list(), 
                 args = list(),
                 complex_displays = list(),
                 kwargs = list(),
                 font = "Times New Roman",
                 fontcolor = [-0.9, -0.9, -0.9],
                 show_background = True):
    assert part_key in instructions.keys(),\
        "No instructions provided for this part"
        
    # Initialize parameters
    finished = False
    Part = instructions[part_key]
    page = 0
    if show_background: draw_background()
    win.flip()
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
            if show_background: draw_background()
            win.flip()
        elif type(page_content) is int:
            special_displays[page_content](args[page_content],
                                           show_background = show_background)
        elif type(page_content) is float:
            complex_displays[int(page_content)](**kwargs[int(page_content)])
        page, finished = iNavigate(page = page, max_page = len(Part),
                                   proceed_key = proceed_key,
                                   wait_s = proceed_wait)
        
              
def LearnCues(cue_center_pos = [0, 2], vert_dist = 7, modes = ["textual", "visual"]):
    # Initialize parameters
    win.flip()
    finished = False
    cat_center_pos =  [0, cue_center_pos[1] - vert_dist]
    page = 0
    category_pos = rectangularGrindPositions(
        center_pos = cat_center_pos, h_dist = 15, dim = (1, 2))
    
    LearnClock = core.Clock()
    while not finished:
        # Draw map cue
        map_name = map_names[page]
        categories = map_name.split("-")
        
        for j in range(len(modes)):
            cue, _ = setCue(map_name, mode = modes[j])
            cue.pos = [sum(x) for x in zip(cue_center_pos, [0, (1-j)*vert_dist])] 
            cue.draw()
        
        # Draw corresponding explicit map
        for i in range(len(categories)):
            rect.pos = category_pos[i]
            rect.draw()
            cat = stim_dict.copy()[categories[i]]
            cat.pos = category_pos[i]
            cat.draw()
        leftArrow.pos = cat_center_pos
        leftArrow.draw()
        win.flip()
        core.wait(0.2)
        
        page, finished = iNavigate(page = page, max_page = len(map_names),
                                   continue_after_last_page = False)  
    # Save learning duration
    learnDuration = LearnClock.getTime()       
    return learnDuration    


def PracticeCues(trials_prim_cue, mode = "visual", cue_pos = [0, 5]):
    # create the trial handler
    PracticeCueTrials = data.TrialHandler(
        trials_prim_cue, 1, method="sequential")
    testRespSuperList = []
    testRTSuperList = []
    cueTypeList = []
    
    for trial in PracticeCueTrials:
        num_cr = len(trial.correct_resp)
        testRespList = []
        testRTList = []
        j = 0
        cue, cue_type = setCue(trial.map[0], mode = mode)
        cue.pos = cue_pos
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
            
    
def GenericBlock(trial_df, mode = "random", i = 0, i_step = None, self_paced = False,
                 display_this = [1, 2, 3, 4, 5, 6, 7], durations = [1, 3, 0.6, 1, 0.7],
                 test = True, feedback = False):    
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
        win.flip()
        
        # 1. Fixation
        if 1 in display_this:
            tFixation()
        
        # 2. Display Family
        if 2 in display_this:
            IRClock = tDisplay(trial, duration = durations[1],
                               self_paced = self_paced)
            
        # 3. Map Cue
        if 3 in display_this:
            tFixation()
            cue_type = tMapcue(trial, mode = mode, duration = durations[0])
        
        if test:
            # 4. Transformation Display
            if 4 in display_this:
                intermediateRT = tEmpty(trial, IRClock)
                trials.addData("intermediateRT", intermediateRT)
        
            # 5. Empty Display
            if 5 in display_this:
                win.flip()
                core.wait(durations[2])
            
            # 6. Test Display
            if 6 in display_this:
                if trial.test_type == "count":
                    testRT, testResp = tCount(trial, feedback = feedback)
                elif trial.test_type == "position":
                    testRT, testResp = tPosition(trial, feedback = feedback)
                
                # Save data
                intermediateRTList.append(intermediateRT)
                testRespList.append(testResp)
                testRTList.append(testRT)
                cueTypeList.append(cue_type)
                core.wait(durations[3])
        
        if 7 in display_this:
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
                    min_acc = 0.95, mode = "random", i = 0, i_step = None,
                    show_cheetsheet = True):
    mean_acc = 0.0
    df_list = []
    if i_step is None:
        i_step = n_exposure * maxn_blocks
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
        if show_cheetsheet and mean_acc < min_acc:
                LearnCues(cue_center_pos = [0, 2], 
                          modes = [first_modality, second_modality])
    df_out = [item for sublist in df_list for item in sublist]
    return df_out


def TestPracticeLoop(trial_df, 
                     min_acc = 0.9, mode = "random", i = 0, i_step = None,
                     durations = [1, 3, 0.6, 1, 0.7], 
                     test = True, feedback = False, self_paced = False):
    mean_acc = 0.0
    df_list = []
    if i_step is None:
        i_step = n_exposure * maxn_blocks
    while mean_acc < min_acc:
        df = GenericBlock(trial_df, mode = mode, i = i, i_step = i_step,
                 durations = durations, test = test, feedback = feedback,
                 self_paced = self_paced)
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
    df_out = [item for sublist in df_list for item in sublist]
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
expInfo = {"participant": "01", "session": "1"}
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
instructions = pickle.load(
    open(stim_dir + os.sep + "instructions_en.pkl", "rb"))


# Load triallists and adapt setup to their parameters

trials_prim_cue = pickle.load(
    open(os.path.join(trial_list_dir, expInfo["participant"] + "_trials_prim_cue.pkl"), "rb" ))

trials_prim_prac_c = pickle.load(
    open(os.path.join(trial_list_dir, expInfo["participant"] + "_trials_prim_prac_c.pkl"), "rb" ))

trials_prim_prac_p = pickle.load(
    open(os.path.join(trial_list_dir, expInfo["participant"] + "_trials_prim_prac_p.pkl"), "rb" ))

trials_prim = pickle.load(
    open(os.path.join(trial_list_dir, expInfo["participant"] + "_trials_prim.pkl"), "rb" ))

trials_bin = pickle.load(
    open(os.path.join(trial_list_dir, expInfo["participant"] + "_trials_bin.pkl"), "rb" ))
    
mappinglists = pickle.load(open(trial_list_dir + os.sep + expInfo["participant"] +
          "_mappinglists.pkl", "rb"))
    
set_size = len(trials_prim[0]["input_disp"])
n_cats = len(np.unique([trial["input_disp"] for trial in trials_prim]))
n_resp = len(trials_prim[0]["resp_options"])
map_names = np.unique([trial["map"] for trial in trials_prim])
n_exposure = 5 # this value should be copied from generate_trial_lists
maxn_blocks = 6 # this value should be copied from generate_trial_lists

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
resp_keys_wide = np.array(["a","s", "d", "num_4", "num_5", "num_6"])
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
assert len(tcue_list) >= len(map_names)
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

# Progress bars
bar_len = 15.0  # total length
bar_height = 0.35
bar_pos = [0, 20]
left_corner = bar_pos[0] - bar_len/2 
progBack = visual.Rect(
    win, width = bar_len, height = bar_height, pos = bar_pos,
    fillColor = color_dict["light_grey"])
progTest = visual.Rect(
    win, width = 0.01, height = bar_height, pos = bar_pos,
    fillColor = "green")

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
def Session1():
    # Global clock
    globalClock = core.Clock()
    win.mouseVisible = False
    n_experiment_parts = 5
    progbar_inc = 1/n_experiment_parts
    start_width = 0
    
    # Navigation
    Instructions(part_key = "Navigation1",
                  special_displays = [iSingleImage,
                                      iSingleImage], 
                  args = [keyboard_dict["keyBoardArrows"],
                          keyboard_dict["keyBoardEsc"]],
                  font = "mono",
                  fontcolor = color_dict["mid_grey"],
                  show_background = False)
    
    # Introduction
    Instructions(part_key = "Intro",
                  special_displays = [iSingleImage,
                                      iSingleImage,
                                      iTransmutableObjects,
                                      iSpellExample,
                                      iSpellExample], 
                  args = [magicBooks,
                          philbertine,
                          None,
                          [["A", "B", "C", "E"], ["A", "E", "C", "E"]],
                          [["A", "B", "B", "E"], ["A", "E", "E", "E"]]])
    
    # ----------------------------------------------------------------------------
    # Balance out which cue modality is learned first
    if int(expInfo["participant"]) % 2 == 0:
        first_modality = "visual"
        second_modality = "textual"
    else:
        first_modality = "textual"
        second_modality = "visual"
    
    # Cue Memory
    Instructions(part_key = "learnCues",
                  special_displays = [iSingleImage], 
                  args = [keyboard_dict["keyBoardSpacebar"]])
    learnDuration_1 = LearnCues(cue_center_pos = [0, 2], 
                                modes = [first_modality, second_modality])           
    progTest, start_width = move_prog_bar(start_width = start_width,
                                          end_width = start_width + progbar_inc)   
                 
    Instructions(part_key = "Intermezzo1",
                 special_displays = [iSingleImage], 
                 args = [keyboard_dict["keyBoard6"]])
    df_out_1 = CuePracticeLoop(trials_prim_cue,
                               min_acc = 0.95,
                               mode = first_modality)   
    progTest, end_width = move_prog_bar(start_width = start_width,
                                        end_width = start_width + progbar_inc)
    
    Instructions(part_key = "Intermezzo2",
                  special_displays = [iSingleImage], 
                  args = [keyboard_dict["keyBoard6"]])
    learnDuration_2 = LearnCues(cue_center_pos = [0, 2], 
                                modes = [first_modality, second_modality])  
    df_out_2 = CuePracticeLoop(trials_prim_cue, 
                               min_acc = 0.95,
                               mode = second_modality, 
                               i = len(df_out_1))
    progTest, start_width = move_prog_bar(start_width = start_width,
                                          end_width = start_width + progbar_inc)         
    
    # Save cue memory data
    fname = data_dir + os.sep + expInfo["participant"] + "_" + expInfo["dateStr"] + "_" +"cueMemory"
    save_object(df_out_1 + df_out_2, fname, ending = 'pkl')
    
    
    # ----------------------------------------------------------------------------
    # Balance out which test type is learned first
    if int(expInfo["participant"]) % 2 == 0:
        first_test = "count"
        tFirst = tCount
        trials_test_1 = trials_prim_prac_c.copy()
        second_test = "position"
        tSecond = tPosition
        trials_test_2 = trials_prim_prac_p.copy()
    else:
        first_test = "position"
        tFirst = tPosition
        trials_test_1 = trials_prim_prac_p.copy()
        second_test = "count"
        tSecond = tCount
        trials_test_2 = trials_prim_prac_c.copy()
    
    # Get Demo trials
    demoTrials1 = data.TrialHandler(
        trials_test_1[0:1].to_dict("records"), 1, method="sequential")
    for demoTrial1 in demoTrials1: True
    demoTrials2 = data.TrialHandler(
        trials_test_2[0:1].to_dict("records"), 1, method="sequential")
    for demoTrial2 in demoTrials2: True
        
    # First Test-Type
    Instructions(part_key = "TestTypes",
                  special_displays = [iSingleImage], 
                  args = [magicWand],
                  complex_displays = [GenericBlock],
                  kwargs = [{"trial_df": trials_prim_prac_p,
                             "durations" : [1, 3, 0.6, 0, 0],
                              "i_step" : 1,
                              "test" : False}])    
        
    
    Instructions(part_key = first_test + "First",
                 special_displays = [iSingleImage], 
                 args = [keyboard_dict["keyBoard4"]],
                 complex_displays = [GenericBlock, GenericBlock, tFirst, tFirst],
                 kwargs = [{"trial_df": trials_test_1,
                            "display_this": [2],
                            "durations" : [0, 0, 0, 0, 0],
                            "i_step" : 1,
                            "test" : False},
                           {"trial_df": trials_test_1,
                            "display_this": [3],
                            "durations" : [0, 0, 0, 0, 0],
                            "i_step" : 1,
                            "test" : False},
                           {"trial": demoTrial1,
                            "feedback": False,
                            "demonstration" : True},
                           {"trial": demoTrial1,
                            "feedback": True,
                            "demonstration" : True}])
    
    
    df_out_3 = TestPracticeLoop(trials_test_1,
                                # i_step = 5,
                                min_acc = 0.95,
                                self_paced = True,
                                feedback = True)
    progTest, start_width = move_prog_bar(start_width = start_width,
                                          end_width = start_width + progbar_inc)  
    
    # Second Test-Type
    Instructions(part_key = second_test + "Second",
                 special_displays = [iSingleImage], 
                 args = [keyboard_dict["keyBoard4"]],
                 complex_displays = [GenericBlock, tSecond, tSecond],
                 kwargs = [{"trial_df": trials_test_2,
                            "display_this": [2, 3],
                            "durations" : [0, 2, 0, 0, 0],
                            "i_step" : 1,
                            "test" : False},
                           {"trial": demoTrial2,
                            "feedback": False,
                            "demonstration" : True},
                           {"trial": demoTrial2,
                            "feedback": True,
                            "demonstration" : True}])
    df_out_4 = TestPracticeLoop(trials_test_2,
                                # i_step = 5,
                                min_acc = 0.95,
                                self_paced = True,
                                feedback = True)
    progTest, start_width = move_prog_bar(start_width = start_width,
                                        end_width = start_width + progbar_inc)  
    
    # Save test type data
    fname = data_dir + os.sep + expInfo["participant"] + "_" + expInfo["dateStr"] + "_" + "testType"
    save_object(df_out_3 + df_out_4, fname, ending = 'pkl')


    Instructions(part_key = "Bye")
    win.close()

##############################################################################
# Training Session
##############################################################################
def Session2():
    # Global clock
    globalClock = core.Clock()
    win.mouseVisible = False
    n_experiment_parts = 4
    progbar_inc = 1/n_experiment_parts
    start_width = 0
    
    # Navigation
    Instructions(part_key = "Navigation2",
                  special_displays = [iSingleImage,
                                      iSingleImage], 
                  args = [keyboard_dict["keyBoardArrows"],
                          keyboard_dict["keyBoardEsc"]],
                  font = "mono",
                  fontcolor = color_dict["mid_grey"],
                  show_background = False)
    
    # Introduction   
    Instructions(part_key = "IntroAdvanced",
                  special_displays = [iSingleImage], 
                  args = [keyboard_dict["keyBoard6"]])
    df_out_5 = CuePracticeLoop(trials_prim_cue, 
                                mode = "random")   
    progTest, start_width = move_prog_bar(start_width = 0,
                                        end_width = 0 + progbar_inc)
             
    # Save cue memory data
    df_out_5.reset_index(drop=True).to_pickle(
        data_dir + os.sep + expInfo["participant"] + "_" + expInfo["dateStr"] +
        "_" +"cueMemoryRefresher.pkl")                                          # TODO Session number in title?
    
    # Reminder of the test types
    demoCounts = data.TrialHandler(
        trials_prim_prac_c[0:1].to_dict("records"), 1, method="sequential")
    for demoCount in demoCounts: True
    demoPositions = data.TrialHandler(
        trials_prim_prac_p[0:1].to_dict("records"), 1, method="sequential")
    for demoPosition in demoPositions: True
    
    Instructions(part_key = "TestTypesReminder",                                
                  special_displays = [iSingleImage, iSingleImage], 
                  args = [magicWand, keyboard_dict["keyBoard4"]],
                  complex_displays = [GenericBlock, GenericBlock, tCount, tPosition],
                  kwargs = [{"trial_df": trials_prim_prac_c,
                             "display_this": [2],
                             "durations" : [0, 0, 0, 0, 0],
                             "i_step" : 1,
                             "test" : False},
                            {"trial_df": trials_prim_prac_c,
                             "display_this": [3],
                             "durations" : [0, 0, 0, 0, 0],
                             "i_step" : 1,
                             "test" : False},
                            {"trial": demoCount,
                             "feedback": False,
                             "demonstration" : True},
                            {"trial": demoPosition,
                             "feedback": False,
                             "demonstration" : True}])
    progTest, start_width = move_prog_bar(start_width = start_width,
                                          end_width = start_width + progbar_inc)  
    # ----------------------------------------------------------------------------
    # Practice: Primitive
    Instructions(part_key = "Primitives",
                  special_displays = [iSingleImage, iSingleImage], 
                  args = [magicWand,
                          keyboard_dict["keyBoard4"]])
    df_out_5 = TestPracticeLoop(trials_prim,
                                min_acc = 0.95,
                                self_paced = True,
                                feedback = True)
    progTest, start_width = move_prog_bar(start_width = start_width,
                                          end_width = start_width + progbar_inc)  
    
    # Practice: Binary
    Instructions(part_key = "Binaries",
                  special_displays = [iSingleImage, iSingleImage], 
                  args = [magicWand,
                         keyboard_dict["keyBoard4"]])
    df_out_6 = GenericBlock(trials_bin,
                            durations = [2, 3, 0.6, 1, 0.7],
                            self_paced = True,
                            feedback = True)
    progTest, start_width = move_prog_bar(start_width = start_width,
                                          end_width = start_width + progbar_inc)  
    
    # Save generic data
    fname = data_dir + os.sep + expInfo["participant"] + "_" + expInfo["dateStr"] + "_" + "generic"
    save_object(df_out_5 + df_out_6, fname, ending = 'pkl')
    
    
    Instructions(part_key = "Bye")
    win.close()

##############################################################################
# Execute
##############################################################################

if expInfo["session"] == '1':
    Session1()
elif expInfo["session"] == '2':
    Session2()
# elif expInfo["session"] == '3':
#     Session3()
else:
    raise ValueError('A session with this number does not exist')