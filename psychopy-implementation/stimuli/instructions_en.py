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
os.chdir(stim_dir)
tcue_list = pd.read_csv(stim_dir + os.sep + "spell_names.csv").columns.tolist()
nMaps = len(tcue_list)

def AddProceedKey(instruction_list, proceed_key, indices, wait_s = 3):
    instruction_list_new = instruction_list.copy()
    assert len(instruction_list_new) >= len(indices),\
        "mismatch between number of instructions and provided indices"
    for idx in indices:
        if type(instruction_list[idx]) is list:                                # this allows prespecifying meta info per instruction
            assert len(instruction_list[idx]) == 3, \
                "prespecified meta-info has wrong dimensions"
        else:
            instruction_list_new[idx] = [instruction_list[idx],
                                         proceed_key, wait_s]
    return instruction_list_new

def AddProceedKey2All(instruction_list, proceed_key, wait_s = 3):
    instruction_list_new = AddProceedKey(instruction_list, proceed_key,
                                         list(range(len(instruction_list))),
                                         wait_s)
    return instruction_list_new



# Navigation Introduction
Navigation = [["For the following displays, you can navigate back and forth"\
                   " using the arrow keys:", "/e", 4],
              0,
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
              "Now, the experiment begins..."
              # ["", "/t", 2]
              ]

# Story Introduction 
Intro = ["You are a magic novice, preparing for your Alteration studies.",
         "As you may know, Alteration spells change the world around you.",
         "Luckily, you own a copy of the famous book series"\
             " 'Principles of Alteration Magic'...",
         0,
         "... famously written by Philbertine:",
         1,
         "The introductory chapter lists the following beginner objects:",
         2,
         "With the correct spell, each beginner object can be transformed into "\
             "another beginner object!",
         "Here you see an example of such an alteration spell:",
         3,
         "Note, that these spells have an area effect: If you cast it,"\
             " all susceptible objects will be transformed.",
         4]
    


# Learn Cues
learnCues = ["Each spell has a specific name and symbol. Philbertine provides a"\
                   " cheat-sheet for the " + str(nMaps) + " beginner spells.",
                   "You decide to spend a couple of minutes to study them.",
                   "When you are done with studying, you may press the spacebar:",
                   0,
                   "Ready?"]   
    
# visualFirst = ["Each spell has a specific symbol. Philbertine provides a"\
#                   " cheat-sheet for the " + str(nMaps) + " beginner spells.",
#                   "You decide to spend a couple of minutes to study them.",
#                   "When you are done with studying, you may press the spacebar:",
#                   0,
#                   "Ready?"]    
    
Intermezzo1 = ["Now that you have committed the spell cues to your memory, you"\
                   " want to make sure you remember them correctly.",
               "In her wise anticipation, Philbertine provides you with a"\
                   " magical practice board.",
               "You will first see the spell cue. Then you need to select the"\
                   " two corresponding objects:",
               "(1) The object which is susceptible to the spell, and (2) the"\
                   " object into which it is transformed.",
               "You choose the objects using the marked keys on your keyboard:",
               0,
               "These keys will correspond to your options from left to right.",
               "Ready?"]

# visualSecond = ["You have now learned the names of the basic spells.",
#                    "However, Filbertine writes of the 'Duality' of spells:",
#                    "Each spell has a specific name and symbol.",
#                    "You need to be able to cast a spell after seeing its symbol,",
#                    "so you decide to spend a couple more minutes to study these...",
#                    "When you are done with studying, you may press the spacebar.",
#                    "Ready?"]

# textualSecond = ["You have now learned the symbols of the basic spells.",
#                     "However, Filbertine writes of the 'Duality' of spells:",
#                     "Each spell has a specific name and symbol.",
#                     "You need to be able to cast a spell after seeing its name,",
#                     "so you decide to spend a couple more minutes to study these...",
#                     "When you are done with studying, you may press the spacebar.",
#                     "Ready?"]
    
Intermezzo2 = ["Next you see if you have learned the second type of spell cue"\
                    " correctly.",
                "The next practice board is completely analogous to the previous"\
                    " one.",
                "Ready?"]
    
# Practice accuracy too bad, repeat:
Feedback0 = ["In this training run, your score was:",
             0,
             "You feel like you can do better, so you decide to train a"\
                 " little more."]
Feedback1 = ["In this training run, your score was:", 
             0, 
             "This is good, you are confident to make the next step..."]


    
# Learn Test Types
TestTypes = [0,
             "It is time for some field practice.",
             "You now know the spell names and symbols that prompt you to "\
                 "cast a spell.",
             "You will now practice applying these spells to groups of objects.",
             "Earlier, you saw what effect transformation spells had.",
             "For the following trials, you will first see the spell cue "\
                 "and then the objects you need to transform using it.",
             "It will look like this:"]

positionFirst = ["Here is what you do:",
                    "(1) Memorize the presented objects.",
                    "When you are done with memorizing: (2) Press the spacebar.",
                    "You will then see a spell cue. (3) Apply it to the memorized display.",
                    "When you are done with transforming: (4) Press the spacebar.",
                    "You will see all the squares on which the objects stood, "\
                        "one of them will be marked.",
                    "(5) From the (equally likely) options below, choose the object that would be "\
                            "on the marked square after the transformation.",
                    "Use the following keys for this choice:",
                    0,
                    "Ready?"]

countFirst = ["Here is what you do:",
                  "(1) Memorize the presented objects.",
                  "When you are done with memorizing: (2) Press the spacebar.",
                  "You will then see a spell cue. (3) Apply it to the memorized display.",
                  "When you are done with transforming: (4) Press the spacebar.",
                  "You will now see an object category.",
                  "(5) From the (equally likely) options below, choose how often "\
                      "this object appears in the scene after the transformation.",
                  "Use the following keys for this choice:",
                  0,
                  "Ready?"]
    
# Faster = ["Next, you will do normal paced trials.",
#                 "Ready?"]


countSecond = ["Some magic students tend to cheat on the test above.",
               "In order to make sure that you transform the objects in your mind "\
                   "first and only then answer a test question...",
              "...there are two test displays (both equally likely to appear):",
              "The previous one was based on object positions. The next will be based "\
                  "on the object count.",
              "After memorizing and transforming the objects (steps 1-4), you will now see an object category",
              "(5) From the (equally likely) options below, choose how often "\
                  "this object appears in the scene after the transformation.",
              "Ready?"] 

positionSecond = ["Some magic students tend to cheat on the test above.",
                  "In order to make sure that you transform the objects in your mind "\
                      "first and only then answer a test question...",
                  "...there are two test displays (both equally likely to appear):",
                  "The previous one was based on object positions. The next will be based "\
                      "on the object count.",
                  "After memorizing and transforming the objects (steps 1-4)...", 
                  "you will see all the squares on which the objects stood. "\
                      "One of them will be marked.",
                  "(5) From the (equally likely) options below, choose the object that would be "\
                      "on the marked square after the transformation.",
                  "Ready?"] 

    
# Primitive Trials
Primitives = [0,
              "You are now well prepared for Alteration magic.",
              "In your examination during the next session, you will encounter tasks"\
                  " which are very similar to the previous ones.",
              "One important difference: You will not know"\
                  " which of the two tests comes at the end of any trial.",
              # "Also, you will not get immediate feedback during your examination.",
              "To ensure that you achieve your study goals, you practice this scenario now.",
              "Ready?"]

# Binary Trials
Binaries = ["Well done!",
            "You are almost finished.",
            "Just as a teaser for the next session: Cues for different spells"\
                " can be combined to produce new spells.",
            "Essentially, the final result is as if you apply the first spell...",
            "... take the intermediate result and then apply the second spell on it.",
            "You will do some exmaples of these 'binary' spells.",
            "This time there is no minimum score.",
            "Ready?"]

# Bye
Bye = ["Congrats!",
       "You are done with your Alteration studies for today.",
       "See you in your next session!"]
    
# Store as Dictionary
instructions ={  
  "lang": "Eng",  
  "exp": "CompInf",
  "Navigation": AddProceedKey2All(Navigation, '/k'),
  "Intro": AddProceedKey2All(Intro, '/k'),
  "Intermezzo1": AddProceedKey2All(Intermezzo1, '/k'),
  "Intermezzo2": AddProceedKey2All(Intermezzo2, '/k'),
  "Feedback0": AddProceedKey2All(Feedback0, '/e', wait_s = 2),
  "Feedback1": AddProceedKey2All(Feedback1, '/e', wait_s = 2),
  "learnCues": AddProceedKey2All(learnCues, '/k'),
  "TestTypes": AddProceedKey2All(TestTypes, '/k'),
  "positionFirst": AddProceedKey2All(positionFirst, '/k'),
  "positionSecond": AddProceedKey2All(positionSecond, '/k'),
  "countFirst": AddProceedKey2All(countFirst, '/k'),
  "countSecond": AddProceedKey2All(countSecond, '/k'),
  "Primitives": AddProceedKey2All(Primitives, '/k'),
  "Binaries": AddProceedKey2All(Binaries, '/k'),
  "Bye": AddProceedKey2All(Bye, '/k'),
}  

with open('instructions_en.pkl', 'wb') as handle:
    pickle.dump(instructions, handle, protocol=pickle.HIGHEST_PROTOCOL)
