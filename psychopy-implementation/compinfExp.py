#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 12:00:24 2021

@author: alex
"""

import os, glob
from string import ascii_uppercase
import numpy as np
import pandas as pd
from psychopy import core, visual, gui, data, event, logging
from psychopy.tools.filetools import toFile
from psychopy.hardware import keyboard

# set directories
main_dir = os.path.dirname(os.path.abspath(__file__))
# main_dir = r"C:\Users\Alex\Desktop\Hub\psychopy-implementation"
# main_dir = "/home/alex/Documents/12. Semester - MPI/Compositional Inference Experiment/compositional-inference/psychopy-implementation/"
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


def tMapcue(trial):
    # rect.pos = center_pos
    # rect.size = center_size
    # rect.draw()
    if np.random.randint(0, 2) == 1:
        cue = vcue_dict[trial.map[0]]
    else:
        cue = tcue_dict[trial.map[0]]
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
    core.wait(3) 
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
    

# Blocks ----------------------------------------------------------------------
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


def LearnCues(center_pos = [0, -6]):
    # Initialize parameters
    still_learning = True
    page = 0
    category_pos = rectangularGrindPositions(
        center_pos = center_pos, h_dist = 15, dim = (1, 2))
    
    while still_learning:
        # Draw map cue
        map_name = map_names[page]
        categories = map_name.split('-')
        cue = vcue_dict[map_name]
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
        
        # Flip through displays
        TestClock = core.Clock()
        _, testResp = tTestresponse(TestClock, ['left', 'right', 'space'],
                                    return_numeric = False)
        if testResp == 'right':
            if page < len(map_names)-1:
                page +=1
        elif testResp == 'left' and page > 0:
            page -= 1
        elif testResp == 'space':
            ruReady.draw()
            win.flip()
            _, contResp = tTestresponse(TestClock, ['return', 'space'],
                                        return_numeric = False)
            if contResp == 'space':
                continue
            elif  contResp == 'return':
                still_learning = False


def PracticeCues(trials_prim_cue):
    # create the trial handler
    trials = data.TrialHandler(
        trials_prim_cue.to_dict('records'), 1, method='sequential')
    
    for trial in trials:
        num_cr = len(trial.correct_resp)
        testRespList = []
        
        # Incrementally display stuff
        for inc in range(3 + num_cr): 
        
            # 0. Fixation
            if inc == 0: 
                tFixation()
                win.flip()
                continue
            
            # 1. Map Cue 
            cue = vcue_dict[trial.map[0]]
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
            
            # 3. Feedback
            TestClock = core.Clock()
            _, testResp = tTestresponse(TestClock, resp_keys_wide)
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
            if inc in list(range(3, 3 + num_cr - 1)):
                win.flip()
                continue
            else:
                win.flip()
                core.wait(1)
 
        
#=============================================================================
# Prepare Experiment
#=============================================================================

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
cuepractice_pos = rectangularGrindPositions(center_pos = [0, -10],
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
assert len(tcue_list) >= len(map_names)
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
                                                size = cue_size)})
    
# create stimuli
stim_list = glob.glob(stim_dir + os.sep + "s_*.png")
stim_list = np.random.permutation(stim_list)
assert len(stim_list) >= n_cats
stim_dict = {}
for i in range(n_cats):
    stim_name = ascii_uppercase[i]
    stim_dict.update({stim_name:visual.ImageStim(win,
                                                 image=stim_list[i],
                                                 size = normal_size)})

# create count responses
count_dict = {}
for i in range(n_resp):
    count_dict.update({str(i):visual.TextStim(win,
                                             text = str(i),
                                             height = 4,
                                             color= [-0.9, -0.9, -0.9])})
qm = visual.TextStim(win,
                     text = '?',
                     height = 4,
                     color = [-0.9, -0.9, -0.9])  

ruReady = visual.TextStim(win,
                          text = 'Press Spacebar to practice longer\n or continue with Enter key',
                          height = 1.5,
                          wrapWidth = 30,
                          color = [-0.9, -0.9, -0.9]) 

leftArrow = visual.ImageStim(
    win, image = glob.glob(stim_dir + os.sep + "leftArrow.png")[0],
    size = normal_size)

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
thisExp = data.ExperimentHandler(
    name = expName, version='', extraInfo = expInfo, runtimeInfo = None,
    originPath = os.path.abspath(__file__),
    savePickle = True, saveWideText = True,
    dataFileName = fileName)

# Log file for detail verbose info
logFile = logging.LogFile(fileName + '.log', level = logging.EXP)
logging.console.setLevel(logging.WARNING) 
# this outputs to the screen, not a file


# and some handy clocks to keep track of time
globalClock = core.Clock()

# Introduction

# Pre-Practice: Learn Cues
LearnClock = core.Clock()
LearnCues()
learnDuration = LearnClock.getTime()

# Practice Block: Cue-Map-Pairs
PracticeCues(trials_prim_cue)

# Block: Primitives
GenericBlock(trials_prim)

dataFile.close()

win.close()
