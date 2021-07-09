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
from psychopy.hardware import keyboard

# set directories
# main_dir = os.path.dirname(os.path.abspath(__file__))
# main_dir = r"C:\Users\Alex\Desktop\Hub\psychopy-implementation"
main_dir = "/home/alex/Documents/12. Semester - MPI/Compositional Inference Experiment/compositional-inference/psychopy-implementation/"
os.chdir(main_dir)
stim_dir = os.path.join(main_dir, "stimuli")
trial_list_dir = os.path.join(main_dir, "trial-lists")

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
    rect_pos = np.empty((set_size, 2), dtype=float)
    for i in range(set_size):
        rect_pos[i] = [center_pos[0] + radius * np.sin(i * angle),
                       center_pos[1] + radius * np.cos(i * angle)]
    return rect_pos

# Trial Components ------------------------------------------------------------
def tFixation():
    fixation.draw()
    win.flip()
    core.wait(0.3)

def setCue(key, mode = "visual"):
    if mode == "visual":
        cue = vcue_dict[key]
    elif mode == "textual":
        cue = tcue_dict[key]
    elif mode == "random":
        if np.random.randint(0, 2) == 1:
            cue = vcue_dict[key]
        else:
            cue = tcue_dict[key]
    return cue


def tMapcue(trial, mode = "visual", with_background = False):
    assert mode in ["visual", "textual", "random"],\
        "Chosen cue mode not implemented."
    if with_background:
        rect.pos = center_pos
        rect.size = center_size
        rect.draw()           
    cue = setCue(trial.map[0], mode = mode)
    cue.draw()
    win.flip()
    core.wait(0.5)


def tDisplay(trial):
    # draw rectangles
    rect.size = normal_size
    for pos in rect_pos:
            rect.pos = pos
            rect.draw()
    
    # draw stimuli
    for i in range(set_size):
        stim = stim_dict[trial.input_disp[i]]
        stim.pos = rect_pos[i]
        stim.draw()
    win.flip()
    IRClock = core.Clock()
    core.wait(1) 
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
            if thisKey == 'space': 
                intermediateRT = IRClock.getTime()
                intermediateResp = 1
            elif thisKey in ['escape']:
                core.quit()  # abort experiment
        event.clearEvents()
    return(intermediateRT)
   

def tCount(trial):
    rect.pos = center_pos
    rect.lineColor = [0, 0.5, 0]
    rect.size = center_size
    rect.draw()
    rect.size = normal_size
    rect.lineColor = [-0.6, -0.6, -0.6]
    stim = stim_dict[trial.target]
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


def tPosition(trial):
    # position cues
    for i in range(len(rect_pos)):
        rect.pos = rect_pos[i]
        if trial.target == i:
            rect.lineColor = [0, 0.5, 0]
            qm.pos = rect_pos[i]
        rect.draw()
        rect.lineColor = [-0.6, -0.6, -0.6]
    qm.draw()
            
    # response options
    for i in range(len(resp_pos)):
        rect.pos = resp_pos[i]
        rect.draw()
        resp = stim_dict[trial.resp_options[i]]
        resp.pos = resp_pos[i]
        resp.draw()


def tTestresponse(TestClock, respKeys, return_numeric = True):
    testResp = None
    while testResp == None:
        allKeys = event.waitKeys()
        for thisKey in allKeys:
            if thisKey in respKeys: 
                testRT = TestClock.getTime()
                if return_numeric:
                    testResp = np.where(respKeys == thisKey)[0][0]
                else:
                    testResp = thisKey
            elif thisKey in ['escape']:
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
    category_pos = rectangularGrindPositions(
        center_pos = [0, 0], h_dist = 10, dim = [2, 3])                     # TODO: make dim dependent on len(categories)

    # draw categories
    for i in range(len(categories)):
        rect.pos = category_pos[i]
        rect.draw()
        stim = stim_dict[categories[i]]
        stim.pos = category_pos[i]
        stim.draw()
    win.flip()


def iSpellExample(*displays):
    # Input Display
    for i in range(2):
        rect_pos = circularGridPositions(center_pos = [0, 0],
                                 set_size = len(displays[0]), radius = 8)
        for j in range(len(displays[0])):
            rect.pos = rect_pos[j]
            rect.draw()
            stim = stim_dict[displays[0][j]]
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
    
    # Output Display
    rect_pos = circularGridPositions(center_pos = [0, 0],
                                 set_size = len(displays[1]), radius = 8)
    for j in range(len(displays[1])):
        rect.pos = rect_pos[j]
        rect.draw()
        stim = stim_dict[displays[1][j]]
        stim.pos = rect_pos[j]
        stim.draw()
    win.flip()
    core.wait(1)
 

def iNavigate(page = 0, max_page = 99, continue_after_last_page = True,
              proceed_key = '/k', wait_s = 3):
    
    assert proceed_key in ['/k', '/t'], "Unkown proceed key"
    finished = False
    testResp = None
    TestClock = core.Clock()
    
    # get response or wait or something in between
    if proceed_key == '/k': #keypress
        _, testResp = tTestresponse(TestClock, ['left', 'right', 'space'],
                                    return_numeric = False)
    elif proceed_key == '/t': #time
        core.wait(wait_s)
        testResp = 'right'
    # elif proceed_key == '/e': #either
    #     while TestClock.getTime() < wait_s:
    #         _, testResp = tTestresponse(TestClock, ['left', 'right', 'space'],
    #                                 return_numeric = False)
    #         if testResp is not None:
    #             break
    #     if testResp is None:
    #         testResp = 'right'
            
    # Proceed accordingly    
    if testResp == 'right':
        if page < max_page-1:
            page +=1
        elif continue_after_last_page:
            finished = True
    elif testResp == 'left' and page > 0:
        page -= 1
    elif testResp == 'space':
        nextPrompt.draw()
        win.flip()
        _, contResp = tTestresponse(TestClock, ['return', 'space'],
                                    return_numeric = False)
        if contResp == 'space':
            finished = False
        elif  contResp == 'return':
            finished = True  
    return page, finished 
    
# Blocks ----------------------------------------------------------------------

def Instructions(part_key = 'Intro', special_displays = list(), args = list(),
                 font = "Times New Roman", fontcolor = [-0.9, -0.9, -0.9]):
    assert len(special_displays) == len(args),\
        "Number of special displays must match the number of args"
    assert part_key in instructions.keys(),\
        "No instructions provided for this part"
        
    # Initialize parameters
    finished = False
    Part = instructions[part_key]
    page = 0
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
        
              
def LearnCues(center_pos = [0, -6], mode = "visual"):
    # Initialize parameters
    LearnClock = core.Clock()
    finished = False
    page = 0
    category_pos = rectangularGrindPositions(
        center_pos = center_pos, h_dist = 15, dim = (1, 2))
    
    while not finished:
        # Draw map cue
        map_name = map_names[page]
        categories = map_name.split('-')
        cue = setCue(map_name, mode = mode)
        cue.draw()
        
        # Draw corresponding explicit map
        for i in range(len(categories)):
            rect.pos = category_pos[i]
            rect.draw()
            cat = stim_dict[categories[i]]
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
        trials_prim_cue.to_dict('records'), 1, method='sequential')
    testRespSuperList = []
    testRTSuperList = []
    
    for trial in PracticeCueTrials:
        num_cr = len(trial.correct_resp)
        testRespList = []
        testRTList = []
        j = 0
        # Incrementally display stuff
        for inc in range(3 + 2 * num_cr): 
        
            # 0. Fixation
            if inc == 0: 
                tFixation()
                win.flip()
                continue
            
            # 1. Map Cue
            cue = setCue(trial.map[0], mode = mode)
            cue.draw()
            if inc == 1:
                win.flip()
                core.wait(0.5)
                continue
            
            # 2. Response options
            rect.lineColor = [-0.6, -0.6, -0.6]
            for i in range(len(cuepractice_pos)):
                rect.pos = cuepractice_pos[i]
                rect.draw()
                resp = stim_dict[trial.resp_options[i]]
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
                    rect.lineColor = [0, 1, 0]
                else:
                    rect.lineColor = [1, 0, 0]
                rect.draw()
                resp = stim_dict[trial.resp_options[testResp]]
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
                    rect.lineColor = [0, 0, 1]
                    rect.draw()
                    resp = stim_dict[trial.resp_options[corResp]]
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
    trials_prim_cue['emp_resp'] = testRespSuperList
    trials_prim_cue['resp_RT'] = testRTSuperList
    return trials_prim_cue


def PracticeLoop(min_acc = 0.9, mode = "textual", i = 1, i_step = 30):
    mean_acc = 0.0
    while mean_acc < min_acc:
        df = trials_prim_cue[i:i+i_step].copy()
        df = PracticeCues(df, mode = mode)                                     # TODO: Save Data with Time Stamp
        errors = (df.correct_resp == df.emp_resp).to_list()
        mean_acc = np.mean(list(map(int, errors))) # convert to integers
        
        accPrompt = visual.TextStim(
            win, text = str(mean_acc * 100) +"%", height = 2.5, wrapWidth = 30,
                font = "Times New Roman", color = [-0.9, -0.9, -0.9])
        
        # repeat or wrap up
        i += i_step    
        if mean_acc < min_acc:
            feedbacktype = 'Feedback0' 
        else: 
            feedbacktype = 'Feedback1'  
        Instructions(part_key = feedbacktype,
                 special_displays = [iSingleImage], args = [[accPrompt]])            
    return i
    
        
def GenericBlock(trial_df):
    # create the trial handler
    trials = data.TrialHandler(
        trial_df.to_dict('records'), 1, method='sequential')

    for trial in trials:
        # 1. Fixation
        tFixation()
        
        # 2. Map Cue
        tMapcue(trial)
        
        # 3. Display Family
        IRClock = tDisplay(trial)
        
        # 4. Transformation Display
        intermediateRT = tEmpty(trial, IRClock)
        trials.addData('intermediateRT', intermediateRT)
        
        # 5. Empty Display
        win.flip()
        core.wait(0.3)
        
        # 6. Test Display
        TestClock = core.Clock()
        if trial.test_type == 'count':
            tCount(trial)   
        elif trial.test_type == 'position':
            tPosition(trial)
        rect.size = normal_size
        win.flip()
        
        # get test response
        testRT, testResp = tTestresponse(TestClock, resp_keys)
        trials.addData('testRT', testRT)
        trials.addData('testResp', testResp)
        dataFile.write('%.4f,%.4f,%i\n' %(intermediateRT, testRT, testResp))
        core.wait(0.5)
    trials.saveAsPickle(fileName)
    
#=============================================================================
# Prepare Experiment
#=============================================================================

# load instructions
with open(stim_dir + os.sep + 'instructions_en.pkl', 'rb') as handle:
    instructions = pickle.load(handle)

# load triallists and adapt setup to their parameters
trials_prim_cue = pd.read_pickle(
    os.path.join(trial_list_dir, "trials_prim_cue.pkl"))
trials_prim = pd.read_pickle(
    os.path.join(trial_list_dir, "trials_prim.pkl"))
set_size = len(trials_prim.input_disp[0])
n_cats = len(np.unique(trials_prim.input_disp.to_list()))
n_resp = len(trials_prim.resp_options[0])
map_names = np.unique(trials_prim.map.to_list())

# set positions 
resp_keys = np.array(['d', 'f', 'j', 'k'])
resp_keys_wide = np.array(['s', 'd', 'f', 'j', 'k', 'l'])
# dict_keys_to_resp_wide = dict(
#     zip(resp_keys_wide, range(len(resp_keys_wide))))
center_pos = [0, 5]
center_size = [8, 8]
cue_size = [9, 9]
normal_size = [5, 5]
# rect_pos = rectangularGrindPositions(center_pos, h_dist = 10, dim = (2, 3))
rect_pos = circularGridPositions(center_pos = center_pos,
                                 set_size = set_size, radius = 7)
resp_pos = rectangularGrindPositions(center_pos = [0, -10],
                                     h_dist = 10, dim = (1, 4))
cuepractice_pos = rectangularGrindPositions(center_pos = [0, -8],
                                            h_dist = 8, dim = (1, 6))

# create window
win = visual.Window(
    [1920, 1080],
    # [800, 600],
    fullscr = False,
    color = [0.85, 0.85, 0.85],
    screen = 1,
    monitor = 'testMonitor',
    units = 'deg')

rect = visual.Rect(
    win = win,
    units = "deg",
    width = 6,
    height = 6,
    fillColor = [0.7, 0.7, 0.7],
    lineColor = [-0.6, -0.6, -0.6])

fixation = visual.GratingStim(
    win, color = -0.9,
    colorSpace = 'rgb',
    pos = center_pos,
    mask = 'circle',
    size = 0.2)

# create textual cues
tcue_list = pd.read_csv(stim_dir + os.sep + "spell_names.csv").columns.tolist()
tcue_list = np.random.permutation(tcue_list)
assert len(tcue_list) == len(map_names)
spellname_dict = dict(zip(tcue_list, map_names))
tcue_dict = {}
for i in range(len(map_names)):
    cue_name = map_names[i]
    tcue_dict.update({cue_name:visual.TextStim(win,
                                               text = tcue_list[i],
                                               pos = center_pos,
                                               height = 4,
                                               color= [-0.9, -0.9, -0.9])})

# create visual cues
vcue_list = glob.glob(stim_dir + os.sep + "c_*.png")
vcue_list = np.random.permutation(vcue_list)
assert len(vcue_list) >= len(map_names)
vcue_dict = {}
for i in range(len(map_names)):
    cue_name = map_names[i]
    vcue_dict.update({cue_name:visual.ImageStim(win,
                                                image = vcue_list[i],
                                                pos = center_pos,
                                                size = cue_size,
                                                interpolate = True)})
    
# create stimuli
stim_list = glob.glob(stim_dir + os.sep + "s_*.png")
stim_list = np.random.permutation(stim_list)
assert len(stim_list) >= n_cats
stim_dict = {}
for i in range(n_cats):
    stim_name = ascii_uppercase[i]
    stim_dict.update({stim_name:visual.ImageStim(win,
                                                 image=stim_list[i],
                                                 size = normal_size,
                                                 interpolate = True)})

# create count responses
count_dict = {}
for i in range(n_resp):
    count_dict.update({str(i):visual.TextStim(win,
                                             text = str(i),
                                             height = 4,
                                             color= [-0.9, -0.9, -0.9])})
    
# create keyboard prompts
keyboard_dict = {}
keyboard_list = glob.glob(stim_dir + os.sep + "keyBoard*.png")
for i in range(len(keyboard_list)):
    key_name = os.path.basename(
        os.path.normpath(keyboard_list[i])).split('.')[0]
    keyboard_dict.update({key_name: visual.ImageStim(win,
                                                image = keyboard_list[i],
                                                size = [40, 20],
                                                interpolate = True)})
    
# misc. stimuli    
qm = visual.TextStim(win,
                     text = "?",
                     height = 4,
                     color = [-0.9, -0.9, -0.9])  
    
nextPrompt = visual.TextStim(
    win, text = "Press Spacebar to go back \nor press the Enter key to"\
        " continue to next section.",
    height = 1.5,
    wrapWidth = 30,
    font = "mono",
    color = [0, 0, 0]) 

leftArrow = visual.ImageStim(
    win, image = glob.glob(stim_dir + os.sep + "leftArrow.png")[0],
    size = normal_size, interpolate = True)

magicWand = visual.ImageStim(
    win, image = glob.glob(stim_dir + os.sep + "magicWand.png")[0],
    size = normal_size, interpolate = True)

magicBooks = visual.ImageStim(
    win, image = glob.glob(stim_dir + os.sep + "magicBooks.png")[0],
    units = 'pix',
    size = [640, 575], interpolate = True)

keyBoard6 = visual.ImageStim(
    win, image = glob.glob(stim_dir + os.sep + "keyBoard6.png")[0],
    size = [40, 20], interpolate = True)

#=============================================================================
# Run Experiment
#=============================================================================

# Store info about the experiment session
psychopyVersion = '2021.1.4'
expName = 'compositionalInference'
expInfo = {'participant': '', 'session': '01'}
expInfo['dateStr'] = data.getDateStr()  # add the current time
expInfo['psychopyVersion'] = psychopyVersion
expInfo['frameRate'] = win.getActualFrameRate()
# if expInfo['frameRate'] != None:
#     frameDur = 1.0 / round(expInfo['frameRate'])
# else:
#     frameDur = 1.0 / 60.0  # could not measure, so guess

# Dialogue Box
# dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys = False, title = expName)
# if dlg.OK:
#     toFile('participantParams.pickle', expInfo)
# else:
#     core.quit()  # the user hit cancel so exit

# Text file to save data
fileName = main_dir + os.sep + u'data/%s_%s_%s' %(expInfo['participant'],
                                                  expName, expInfo['dateStr'])
dataFile = open(fileName + '.csv', 'w')
dataFile.write('intermediateRT, testRT, testResp\n')

# ExperimentHandler
# thisExp = data.ExperimentHandler(
#     name = expName, version='', extraInfo = expInfo, runtimeInfo = None,
#     originPath = os.path.abspath(__file__),
#     savePickle = True, saveWideText = True,
#     dataFileName = fileName)

# Log file for detail verbose info
logFile = logging.LogFile(fileName + '.log', level = logging.EXP)
logging.console.setLevel(logging.WARNING) 
# this outputs to the screen, not a file


# and some handy clocks to keep track of time
globalClock = core.Clock()

# Navigation
Instructions(part_key = 'Navigation',
             special_displays = [iSingleImage,
                                 iSingleImage], 
             args = [[keyboard_dict['keyBoardArrows']],
                     [keyboard_dict['keyBoardEsc']]],
             font = "mono",
             fontcolor = [0, 0, 0])

# Introduction
Instructions(part_key = 'Intro',
             special_displays = [iSingleImage,
                                 iTransmutableObjects,
                                 iSpellExample,
                                 iSpellExample,
                                 iSingleImage], 
             args = [[magicBooks],
                     [None],
                     [['A', 'B', 'C', 'C', 'E', 'C'],
                      ['A', 'E', 'C', 'C', 'E', 'C']],
                     [['B', 'A', 'C', 'B', 'B', 'D'],
                      ['E', 'A', 'C', 'E', 'E', 'D']],
                     [keyboard_dict['keyBoardSpacebar']]]
                     )

# Pre-Practice: Learn textual cues and test memory performance
learnDuration = LearnCues(mode = "textual")                                     # TODO: Save Data with Time Stamp
Instructions(part_key = 'Intermezzo1',
             special_displays = [iSingleImage], 
             args = [[keyboard_dict['keyBoard6']]])
i = 1
i = PracticeLoop(min_acc = 0.9, mode = "textual", i = i, i_step = 2)

# Pre-Practice: Learn visual cues and test memory performance    
Instructions(part_key = 'NowVisual')
learnDuration = LearnCues(mode = "visual")
Instructions(part_key = 'Intermezzo2')
i = PracticeLoop(min_acc = 0.9, mode = "visual", i = i, i_step = 2)

# Block: Primitives
GenericBlock(trials_prim)

dataFile.close()

win.close()
