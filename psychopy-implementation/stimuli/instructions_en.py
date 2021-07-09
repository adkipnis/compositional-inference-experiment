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
Navigation = [0,
              "Don't worry, there is no shame in going back pages.",
              "In this first session, you will learn the basics of the task"\
                  " which you will later perform in the MEG.",
              # "You can press the spacebar to skip to the next section:",
              # 1,
              "If for some reason you need to abort the experiment, you can"\
                  " do so by pressing Esc:",
              1,
              "Please be careful not to press this key by accident!",
              "Finally, if you have any questions, please ask the examiner.",
              "Now, the experiment begins...",
              ""]
# Introduction
Intro = ["You are a mage apprentice, preparing for your Alteration classes.",
         "Luckily, you own a copy of the famous book series"\
             " 'Principles of Alteration Magic', written by Philbertine.",
         0,
         "The introductory chapter lists the following beginner objects:",
         1,
         "With the correct spell, each of them can be transformed into another!",
         "Here you see an example of such an alteration spell:",
         2,
         "Note, that these spells have an area effect: If you cast it,"\
             " all susceptible objects will be transformed.",
         3,
         "Each spell has a specific name. Philbertine provides a cheat-sheet"\
             " of the " + str(nMaps) + " beginner spells.",
         "You decide to spend a couple of minutes to study them.",
         "When you are done with studying, you may press the spacebar:",
         4,
         "Ready?"
    ]
    

# Before textual practice
Intermezzo1 = ["Now that you have committed these spells to your memory, you"\
                   " want to make sure you remember them correctly.",
               "In her wise anticipation, Philbertine provides you with a"\
                   " magical practice board.",
               "You will first see the spell name. Then you need to select the"\
                   " two corresponding objects:",
               "(1) The object which is susceptible to the spell, and (2) the"\
                   " object into which it is transformed.",
               "You choose the objects using the marked keys on your keyboard:",
               0,
               "These keys will correspond to your options from left to right.",
               "Ready?"]

# Practice accuracy too bad, repeat:
Feedback0 = [0,
             "You feel like you can do better, so you decide to train a"\
                 " little more."]
Feedback1 = [0,
             "This is good, you are confident to make the next step..."]

# Before visual practice
NowVisual = ["You have now learned the names of the basic spells.",
             "In reality, you sometimes need to cast a spell without saying"\
                 " it out loud.",
             "In fact, each spell also has a specific symbol.",
             "Yes, you can also cast spells by focusing on that symbol"\
                 " in your mind.",
             "You decide to spend a couple more minutes to study these...",
             "When you are done with studying, you may press the spacebar.",
             "Ready?"]

Intermezzo2 = ["Now that you have committed these spells to your memory, you"\
                   " want to make sure you remember them correctly.",
               "Again, Philbertine provides you with a magical practice board.",
               "The instructions are completely analogous to the previous"\
                   " practice board.",
               "Ready?"]
    
# Store as Dictionary
instructions ={  
  "lang": "Eng",  
  "exp": "CompInf",
  "Navigation": Navigation,
  "Intro": Intro,
  "Intermezzo1": Intermezzo1,
  "Intermezzo2": Intermezzo2,
  "Feedback0": Feedback0,  
  "Feedback1": Feedback1,
  "NowVisual": NowVisual
}  

with open('instructions_en.pkl', 'wb') as handle:
    pickle.dump(instructions, handle, protocol=pickle.HIGHEST_PROTOCOL)
