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
Navigation1 = [
              # ["For the following displays, you can navigate back and forth"\
              #      " using the arrow keys:", "/e", 4],
              0,
              "Don't worry, there is no shame in going back pages.",
              "In this first session, you will prepare the basics of the task"\
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

Navigation2 = [
              0,
              "Don't worry, there is no shame in going back pages.",
              "In this second session, you will train the actual task"\
                  " which you will perform in the MEG in the third session.",
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

    
Navigation3 = [
              0,
              "This is the third and final session of the experiment.",
              "If you need to abort the experiment,\nor you have any questions,\n"\
                  "please ask the examiner.",
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

IntroAdvanced = ["Since the last time, you have advanced in your Alteration studies.",
         "Philbertine would be impressed.",
         "You now know all elements of alteration:",
         "(1) The two types of spell cue...",
         "And (2) the two types of spell tests...",
         "Just as a refresher you will do a couple of trials for each of these.",
         "You start with the spell cues, use the following keys:",
         0,
         "Ready?"]

# TODO eyetracking?
IntroMEG = ["Today is the day of your exam\nin the art of Alteration.",
         "You have trained hard to get here.",
         "The (very large) magical helmet above you\nreads your spellcasting.",
         "Everyone's mind is special,\nso before the exam...",
         "...it has to be attuned to yours:",
         "For this, you will view familiar images.",
         "After some of them, you have\nto answer a yes/no question.",
         "Use the following keys:",
         0,
         "Ready?"]



# Learn Cues
learnCues = ["Each spell has a specific name and symbol. Philbertine provides a"\
                   " cheat-sheet for the " + str(nMaps) + " beginner spells.",
                   "You need to spend some time to study them really well.",
                   "Specifically, you need to learn the exact name and symbol "\
                       "which are associated with each respective spell.",
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
    
Intermezzo2 = ["You have mastered the first spell cue type. Congrats!",
               "Next, you will see if you have learned the second spell cue type"\
                    " correctly.",
                "The following practice board is completely analogous to the previous"\
                    " one.",
                "Again, you choose the objects using the marked keys on your keyboard:",
                0,
                "Just as a refresher you get a second look at Philbertines cheet sheet before that.",
                "Ready?"]
    
# Practice accuracy too bad, repeat:
Feedback0 = ["In this training run, your score was:",
             0,
             "You feel like you can do better, so you decide to have another "\
                 "look at the cheet sheet and then train a little more."]
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
                 "and then the objects you need to transform using it.",       # TODO update order 
             "It will look like this:",
             0.0]

positionFirst = ["Here is what you do:",
                "(1) Memorize the presented objects:",
                0.0,
                "When you are done with memorizing: (2) Press the spacebar.",
                "You will then see a spell cue. (3) In your head, apply it to the memorized display.",
                1.0,
                "When you are done: (4) Press the spacebar.",
                "You will see all the squares on which the objects stood, "\
                    "one of them will be marked.",
                2.0,
                "",
                "(5) From the options below, choose the object that would be "\
                        "on the marked square after the transformation.",
                "For training purposes you will get immediate feedback:",
                3.0,
                "Use the following keys for this choice:",
                0,
                "Ready?"]

countFirst = ["Here is what you do:",
                "(1) Memorize the presented objects:",
                0.0,
                "When you are done with memorizing: (2) Press the spacebar.",
                "You will then see a spell cue. (3) In your head, apply it to the memorized display.",
                1.0,
                "When you are done: (4) Press the spacebar.",
                "You will now see an object category and some integers on the bottom.",
                2.0,
                "",
                "(5) From the options below, choose how often "\
                    "this object appears in the scene after the transformation.",
                "For training purposes you will get immediate feedback:",
                3.0,
                "Use the following keys for this choice:",
                0,
                "Ready?"]


countSecond = ["Some magic students tend to cheat on the test above.",
               "In order to make sure that you transform the objects in your mind "\
                   "first and only then answer a test question...",
              "...there are two test displays (both equally likely to appear):",
              "The previous one was based on object positions. The next will be based "\
                  "on the object count.",
              "After memorizing and transforming the objects (steps 1-4)...",
              0.0,
              "you will see an object category and some integers on the bottom.",
              1.0,
              "",
              "(5) From the options below, choose how often "\
                  "this object appears in the scene after the transformation.",
              "For training purposes you will get immediate feedback:",
              2.0,
              "Again, use the following keys for this choice:",
              0,
              "Ready?"] 

positionSecond = ["Some magic students tend to cheat on the test above.",
                  "In order to make sure that you transform the objects in your mind "\
                      "first and only then answer a test question...",
                  "...there are two test displays (both equally likely to appear):",
                  "The previous one was based on object count. The next will be based "\
                      "on the object positions.",
                  "After memorizing and transforming the objects (steps 1-4)...", 
                  0.0,
                  "you will see all the squares on which the objects stood. "\
                      "One of them will be marked.",
                  1.0,
                  "",
                  "(5) From the options below, choose the object that would be "\
                      "on the marked square after the transformation.",
                  "For training purposes you will get immediate feedback:",
                  2.0,
                  "Again, use the following keys for this choice:",
                  0,
                  "Ready?"] 

TestTypesReminder = [0,
             "You hopefully still remember how you used spells in your first session.",
             "Just to be safe, here's a reminder:",
             "You first see a set of objects: (1) Memorize the presented objects.",
             0.0,
             "When you are done with memorizing: (2) Press the spacebar.",
             "You will then see a spell cue. (3) In your head, apply it to the memorized display.",
             1.0,
             "When you are done: (4) Press the spacebar.",
             "Then you can receive one of two possible test displays.",
             "Counting: You will see an object category and integers on the bottom.",
             2.0,
             "",
             "(5) From the options below, choose how often "\
             "this object appears in the scene after the transformation.",
             "Position query: You will see all the squares on which the objects stood, "\
                        "one of them will be marked.",
             3.0,
             "",
             "(5) From the options below, choose the object that would be "\
                    "on the marked square after the transformation.",
             "Use the following keys for your choice:",
             1,
             "It's important that you understand the instructions, so please go "\
                 "back and review them if you are unsure. Otherwise click next."
             ]    

    
# Primitive Trials
Primitives = [0,
              "In your examination during the next session, you will encounter tasks"\
                  " which are very similar to the ones you did in the first session.",
              "One important difference: You will not know"\
                  " which of the two tests comes at the end of any trial.",
              "To ensure that you achieve your study goals, you practice this scenario now.",
              "Again, use the following keys for the decision at the end of each trial:",
                    1,
              "Ready?"]
    
PrimitivesMEG = [0,
              "The magical helmet is now accustomed to your thought patterns.",
              "It says, you have a beautiful mind. :)",
              "You will surely put it to good use in the exam.",
              "In the first of two parts,\nyour task is the one you practices in the last sessions.",
              "You hopefully still remember it, but here's a reminder:",
              "You first see a set of objects:\n(1) Memorize the presented objects.",
              0.0,
              "When you are done with memorizing:\n(2) Press the right thumb button.",
              "You will then see a spell cue.\n(3) In your head, apply it to the memorized display.",
              1.0,
              "When you are done:\n(4) Press the right thumb button.",
              "Then you can receive one of two possible test displays.",
              "Type 1 - Counting: You will see an object category and integers on the bottom.",
              2.0,
              "",
              "(5) From the options below, choose how often "\
              "this object appears in the scene after the transformation.",
              "Type 2 - Position query: You will see all the squares on which the objects stood, "\
                         "one of them will be marked.",
              3.0,
              "",
              "(5) From the options below, choose the object that would be "\
                     "on the marked square after the transformation.",
              "Use the following keys:",
              1,
              "Be as accurate as possible\n-\nyour reward will depend on it!",
              "Ready to begin the exam?"]

# Binary Trials
Binaries = [0,
            "Well done!",
            "Just as a teaser for the next session: Cues for different spells"\
                " can be combined to produce new spells.",
            "Essentially, the final result is as if you apply the first spell...",
            "... take the intermediate result and then apply the second spell on it.",
            "You will do some exmaples of these 'binary' spells.",
            "This time there is no minimum score.",
            "Again, use the following keys for the decision at the end of each trial:",
                    1,
            "Ready?"]

BinariesMEG = [0,
            "Well done, you have finished the first part!",
            "The second part of the exam is like the first one,\nbut with two spell cues:",
            "You apply the first spell,\ntake the intermediate result"\
                "\nand then apply the second spell on it.",
            "Again, use the following keys:",
                    1,
            "Be as accurate as possible.",
            "Ready?"]
    
# Bye
Bye = ["Congrats!",
       "You are done with your Alteration studies for today.",
       "See you in your next session!"]

ByeBye = ["Congrats!",
       "You have finished your exam.",
       "The magical council will send you your grade and reward soon.",
       "Farewell on your remaining magical journey. :)"]
    
# Store as Dictionary
instructions ={  
  "lang": "Eng",  
  "exp": "CompInf",
  "Navigation1": AddProceedKey2All(Navigation1, '/k'),
  "Navigation2": AddProceedKey2All(Navigation2, '/k'),
  "Navigation3": AddProceedKey2All(Navigation3, '/m'),
  "Intro": AddProceedKey2All(Intro, '/k'),
  "IntroAdvanced": AddProceedKey2All(IntroAdvanced, '/k'),  
  "IntroMEG": AddProceedKey2All(IntroMEG, '/m'),  
  "Intermezzo1": AddProceedKey2All(Intermezzo1, '/k'),
  "Intermezzo2": AddProceedKey2All(Intermezzo2, '/k'),
  "Feedback0": AddProceedKey2All(Feedback0, '/k'),
  "Feedback1": AddProceedKey2All(Feedback1, '/e', wait_s = 2),
  "learnCues": AddProceedKey2All(learnCues, '/k'),
  "TestTypes": AddProceedKey2All(TestTypes, '/k'),
  "positionFirst": AddProceedKey2All(positionFirst, '/k'),
  "positionSecond": AddProceedKey2All(positionSecond, '/k'),
  "countFirst": AddProceedKey2All(countFirst, '/k'),
  "countSecond": AddProceedKey2All(countSecond, '/k'),
  "TestTypesReminder": AddProceedKey2All(TestTypesReminder, '/k'),
  "Primitives": AddProceedKey2All(Primitives, '/k'),
  "PrimitivesMEG": AddProceedKey2All(PrimitivesMEG, '/m'),
  "Binaries": AddProceedKey2All(Binaries, '/k'),
  "BinariesMEG": AddProceedKey2All(BinariesMEG, '/m'),
  "Bye": AddProceedKey2All(Bye, '/k'),
  "ByeBye": AddProceedKey2All(ByeBye, '/m'),
}  

with open('instructions_en.pkl', 'wb') as handle:
    pickle.dump(instructions, handle, protocol=pickle.HIGHEST_PROTOCOL)