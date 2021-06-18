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
from psychopy import core, visual, gui, data, event
from psychopy.tools.filetools import toFile


# set directories
main_dir = "/mnt/win10/Users/Alex/Desktop/Hub/psychopy-experiment/"
stim_dir = os.path.join(main_dir, "stimuli")
trial_list_dir = os.path.join(main_dir, "trial-lists")

# get participant id
expInfo = {'ID':'#'}
expInfo['dateStr'] = data.getDateStr()  # add the current time

# present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title = 'Primitive Blocks', fixed = ['dateStr'])
if dlg.OK:
    toFile('participantParams.pickle', expInfo)
else:
    core.quit()  # the user hit cancel so exit

# load triallists and adapt setup to their parameters
trials_prim = pd.read_pickle(
    os.path.join(trial_list_dir, "trials_prim.pkl"))
trials_prim = trials_prim[0:3]
set_size = len(trials_prim.input_disp[0])
n_cats = len(np.unique(trials_prim.input_disp.to_list()))
n_resp = len(trials_prim.resp_options[0])
map_names = np.unique(trials_prim.map.to_list())

# set positions #TODO: adaptive positions
resp_keys = np.array(['d', 'f', 'j', 'k'])
center_pos = [0, 5]
center_size = [8, 8]
normal_size = [6, 6]
rect_hpos = [-10 , 0 , 10] 
rect_vpos = [10, 0]
rect_pos = np.transpose([np.tile(rect_hpos, len(rect_vpos)),
                           np.repeat(rect_vpos, len(rect_hpos))])
resp_hpos = [-15, -5, 5, 15]
resp_vpos = [-10]
resp_pos = np.transpose([np.tile(resp_hpos, len(resp_vpos)),
                           np.repeat(resp_vpos, len(resp_hpos))])

# make a text file to save data
fileName = 'data' + os.sep + expInfo['ID'] + '_' + expInfo['dateStr']
dataFile = open(fileName + '.csv', 'w')
dataFile.write('intermediateRT, testRT, testResp\n')

# create the trial handler
trials = data.TrialHandler(
    trials_prim.to_dict('records'), 1, method='sequential')

# create window
win = visual.Window(
    [1920, 1080],
    allowGUI = True,
    fullscr = True,
    color = [0.85, 0.85, 0.85],
    monitor = 'testMonitor',
    units = 'deg')

rect = visual.Rect(
    win = win,
    units = "deg",
    width = 6,
    height = 6,
    fillColor = [0.5, 0.5, 0.5],
    lineColor = [-0.6, -0.6, -0.6])

fixation = visual.GratingStim(win, color = -0.9, colorSpace = 'rgb',
                              pos = center_pos, mask = 'circle', size = 0.2)

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
                                                size = center_size)})
    
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
                     color= [-0.9, -0.9, -0.9])    

# and some handy clocks to keep track of time
globalClock = core.Clock()


# loop through trial list
for trial in trials:
    # 1. Fixation
    fixation.draw()
    win.flip()
    core.wait(0.3)
    
    # 2. Map Cue
    cue = vcue_dict[trial.map[0]]
    cue.draw()
    win.flip()
    core.wait(0.5)
    
    # 3. Display Family
    # draw rectangles
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
    
    # 4. Transformation Display
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
    trials.addData('intermediateRT', intermediateRT)
    
    # 5. Empty Display
    win.flip()
    core.wait(0.3)
    
    # 6. Test Display
    TestClock = core.Clock()
    # 6.A Count
    if trial.test_type == 'count':
        rect.pos = center_pos
        rect.lineColor = [0, 0.9, 0]
        rect.size = center_size
        rect.draw()
        stim = stim_dict[trial.target]
        stim.pos = center_pos
        stim.size = center_size
        stim.draw()
        for i in range(len(resp_pos)):
            rect.pos = resp_pos[i]
            rect.draw()
            resp = count_dict[str(i)]
            resp.pos = resp_pos[i]
            resp.draw()
    
    # 6.B Position    
    elif trial.test_type == 'position':
        # position cues
        for i in range(len(rect_pos)):
            rect.pos = rect_pos[i]
            if trial.target == i:
                rect.lineColor = [0, 0.5, 0]
                qm.pos = rect_pos[i]
            else:
                rect.lineColor = [-0.6, -0.6, -0.6]
            rect.draw()
        qm.draw()
        
        # options
        for i in range(len(resp_pos)):
            rect.pos = resp_pos[i]
            rect.draw()
            resp = stim_dict[trial.resp_options[i]]
            resp.pos = resp_pos[i]
            resp.draw()
    rect.size = normal_size
    
    win.flip()
    
    # get intermediate response
    testResp = None
    while testResp == None:
        allKeys = event.waitKeys()
        for thisKey in allKeys:
            if thisKey in resp_keys: 
                testRT = TestClock.getTime()
                testResp = np.where(resp_keys == thisKey)[0][0]
            elif thisKey in ['escape']:
                core.quit()  # abort experiment
        event.clearEvents()      
    trials.addData('testRT', testRT)
    trials.addData('testResp', testResp)
    dataFile.write('%.4f,%.4f,%i\n' %(intermediateRT, testRT, testResp))
    core.wait(0.5)
dataFile.close()
trials.saveAsPickle(fileName)
win.close()
