# -*- coding: utf-8 -*-
"""
Created on Fri May 13 15:18:51 2022

@author: external
"""

import numpy as np
from psychopy import core, visual, event
from psychopy.parallel import ParallelPort

port_in = ParallelPort(address="0xd111") # for receiving button presses
resp_keys = np.array(["s", "d", "num_4", "num_5"])
# mapping of MEG response: b1 = 8, b2 = 16, b3 = 32, b5 = 0   
# arrangement: b2,b1   b3,b5
pp_map = [None]*33
pp_map[16] = resp_keys[0]
pp_map[8] = resp_keys[1]
pp_map[32] = resp_keys[2]
pp_map[0] = resp_keys[3]

def read_pp(base = 128, max_wait = 3):
    clock = core.Clock()
    received = base
    while received == base and clock.getTime() < max_wait:
        received = port_in.readData()
    out = received & 0x78
    print(out)
    return out
        
def tTestresponse(TestClock, respKeys, return_numeric = True,
                  max_wait = np.inf, use_pp = False):
    testResp = None
    testRT = None
    while testResp is None:
        if use_pp:
            response_button = read_pp(max_wait = max_wait)
            allKeys = [pp_map[response_button]]
            print(allKeys)
        else:
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
    
win = visual.Window(
    [1920, 1080],
    fullscr = False,
    color = [0.85, 0.85, 0.85],
    screen = 0,
    monitor = "testMonitor",
    units = "deg")

wait_signal = visual.TextStim(win, text = "Wait",
                           height = 1.8, wrapWidth = 30,
                           color = [-0.9, -0.9, -0.9])
go_signal = visual.TextStim(win, text = "Go!",
                            height = 1.8, wrapWidth = 30,
                            color = [-0.9, -0.9, -0.9])
wait_signal.draw()
win.flip()
core.wait(4) # automatically registers b5 if we wait less?
go_signal.draw()
win.flip()
test_clock = core.Clock()
testRT, testResp = tTestresponse(test_clock, resp_keys, use_pp = True)
win.flip()
core.wait(1)
win.close()
print(testResp)
