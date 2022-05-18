#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Methods for running the compositional inference experiment
"""
import os, sys

class Experiment:
    def __init__(self, main_dir = None):
        # root directory of experiment
        if main_dir is not None: self.main_dir = main_dir
        else: self.main_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.main_dir)
        
        # directory for trial lists, stimuli and instructions
        self.trial_list_dir = os.path.join(self.main_dir, "trial-lists")
        if not os.path.exists(self.trial_list_dir): import generate_trial_lists
        self.stim_dir = os.path.join(self.main_dir, "stimuli")
        sys.path.insert(0, './stimuli')
        import instructions_en
        
        # data dir
        self.data_dir = os.path.join(self.main_dir, "data")
        if not os.path.exists(self.data_dir): os.makedirs(self.data_dir)
    

# Exp = Experiment(main_dir = "/kyb/rg/akipnis/Nextcloud/Code/compositional-inference/psychopy-implementation")
Exp = Experiment()