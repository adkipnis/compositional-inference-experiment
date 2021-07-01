#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 18:57:59 2021

@author: alex
"""
import os
import pickle  
import pandas as pd

stim_dir = os.path.dirname(os.path.abspath(__file__))
tcue_list = pd.read_csv(stim_dir + os.sep + "spell_names.csv").columns.tolist()
nMaps = len(tcue_list)

# Navigation

# Story
Story = ["You are a mage apprentice, preparing for your Alteration classes.",
         "Luckily, you own a copy of the famous book series"\
             " 'Principles of Alteration Magic', written by Jade Philbertine.",
         0,
         "The first volume lists the following transmutable objects:",
         1,
         "With the correct spell, some of them can be transmuted into others!",
         "Here you see an example of an unknown spell:",
         2,
         "Note, that these spells have an area effect: If you cast it on one"\
             " point, all susceptible objects around it will be transmuted.",
         3,
         "Each spell has a name. Philbertine provides a cheat-sheet of the "
             + str(nMaps) + " beginner spells.",
         "You decide to study them first."
    ]
    

# PracticeCues
PracticeCues = ["In the following task, you will learn"]

# Store as Dictionary
instructions ={  
  "lang": "Eng",  
  "exp": "CompInf",
  "Story": Story,
  "PracticeCues": PracticeCues
}  

with open('instructions_en.pkl', 'wb') as handle:
    pickle.dump(instructions, handle, protocol=pickle.HIGHEST_PROTOCOL)
