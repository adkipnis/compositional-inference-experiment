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
nMaps = round(len(tcue_list)/2)

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


# ============================================================================
AutonomousMEGR = [0,
              "Rejoice!\n\nYou have reached the final part of the exam.\nIt will be much shorter than the last one.",
              "The school wants its students\nto be autonomous magicians.",
              "For the following trials\nyou will have to choose the spell yourself!",
              "(Step 1)\nMemorize the presented objects.\n\nThen, press the 'next' key (right thumb).",
              0.0,
              "(Step 2)\nYou will see a question mark.\nChoose a single spell.\n\nThen, press the 'next' key.",
              1,
              "(Step 3)\nApply the chosen spell\nto the memorized display.\n\nThen, press the 'next' key.",
              2,
              "(Step 4)\nDo the given test on the output display.",
              1.0,
              "(Step 5)\nIndicate which spell you chose.",
              2.0,
              "Use the following keys\nfor each decision:",
              3,
              "The exam continues until you have enough consistent responses.",
              "Be as accurate and as fast as possible.",
              "Remember to move as little as possible\nfor the helmet.",
              "Ready for the exam?"]

BinariesMEGR = [0,
            "Well done, you have finished the first part!",
            "The second part of the exam is like the first one,\nbut with two spell cues",
            "Essentially, these 'double spells' require you\nto apply each primitive spell sequentially.",
            "The result is as if you apply the first spell,\ntake the intermediate result\nand then apply the second spell on that.",
            "Here's an example:",
            "(1) Memorize the presented objects.",
            0.0,
            "When you are done:\n(2) Press the 'next' key (right thumb).",
            "You will then see two(!) spell cues.",
            1.0,
            "(3) In your mind, apply both spells to the memorized display.",
            "When you are done:\n(4) Press the 'next' key (right thumb).",
            "Then you can receive one of two possible test displays,\nthey are analogous to the previous trials.",
            "You will now be tested on these 'composed' spells\nuntil you have enough correct responses.",
            "Again, use the following keys for the decision at the end of each trial:",
            2,
            "If you don't know the answer,\npress the 'next' key (right thumb).",
            "Be as accurate and as fast as possible.",
            "Remember to move as little as possible for the helmet.",
            "Ready to finish the exam?"]
    
Bye = ["Congrats!",
       "You are done with the first session.",
       "Have a quick break!"]

ByeBye = ["Congrats!",
       "You have finished your exam.",
       "The council will send you your grade and reward soon.",
       "Farewell on your further journey! :)"]

TestTypes = [0,
             "It is time for the next chapter in Philbertine's book: \n\nYou will apply alteration spells\nto groups of objects.",
             "Again, the textbook provides\ntwo magical practice boards.\nThe trials go as follows:",
             "(Step 1)\nMemorize the presented objects.\n\nThen, press the 'next' key (right thumb).",
             0.0,
             "(Step 2)\nYou will see a spell cue.",
             1.0,
             "(Step 3)\nYou will see empty squares. Apply the spell to the memorized display.\n\nThen, press the 'next' key (right thumb).",
             1]

countFirst = TestTypes + [
    "(Step 4)\nYou will see an object. Count how often it appears in the output display.\n\nChoose the corresponding integer below.",
    2.0,
    "Use the following keys for this choice:",
    2,
    "If you don't know the answer,\npress the 'next' key (right thumb).",
    "This test continues\nuntil you have enough correct responses.",
    "Ready?"]

countSecond = ["Nicely done! Some magic students tend to cheat on this though.",
               "We need to make sure that you transform the objects in your mind first and only then answer a test question.\n\nThat's why there are two test displays!",
               "The previous one was based on object positions. The next will be based on the object counting.",
               "(Steps 1-3) The procedure is the same as before.",
               0.0,
               "(Step 4)\nYou will see an object. Count how often it appears in the output display.\n\nChoose the corresponding integer below.",
               1.0,
               "Again, use the following keys for this choice:",
               0,
               "If you don't know the answer,\npress the 'next' key (right thumb).",
               "Ready?"] 


InterleavedMEGR = [0,
                   "You have studied diligently.\nYou are well prepared for the magic exam.",
                   "The first part consists of\nnormal Alteration trials.",
                   "However, the test is\nrandomly chosen each time.",
                   "On top, some trials will have two spell cues!",
                   "These 'double spells' require you\nto apply each primitive spell sequentially.",
                   "The result is as if you apply the first spell, take the intermediate result, and then apply the second spell on that.",
                   "Here's an example:",
                   "(Step 1)\nMemorize the presented objects.\n\nThen, press the 'next' key (right thumb).",
                   0.0,
                   "(Step 2)\nYou will see two(!) spell cues.",
                   1.0,
                   "(Step 3)\nApply both spells to the memorized display.\n\nThen, press the 'next' key (right thumb).",
                   1,
                   "(Step 4)\nDo the test on the output display.",
                   2.0,
                   "Use the following keys for the decision:",
                   2,
                   "The exam continues until you have enough correct responses.\n\nWrong responses prolong it.",
                   "So if you don't know the answer,\nplease press the 'next' key (right thumb).",
                   "This will be the longest part of both sessions.",
                   "Be as accurate and as fast as possible.",
                   "Remember to move as little as possible\nfor the magical helmet.",
                   "Ready for the exam?"]


Intermezzo1 = ["Next, you need to make sure\nyou remember the spells correctly.",
               "Philbertine's textbook provides\ntwo magical practice boards.",
               "One for spell symbols and one for spell names. The trials go as follows:",
               "(Step 1)\nYou will see the spell cue.\nBelow are the objects.",
               0.0,
               "(Step 2)\nFirst, select the input object.\nSecond, select the output object.",
               "Use the marked keys for your choice:",
               0,
               "The blue keys will correspond to your options\nfrom left to right.",
               "If you don't know the answer,\npress the 'next' key (right thumb).",
               "You will now be tested on the cues\nuntil you have enough correct responses.",
               "Ready?"]
    
Intermezzo2 = ["Nice, you have mastered the first cue modality!",
               "Next, you train on the second modality.",
               "The following practice board is\ncompletely analogous.",
               "(Step 1)\nYou will see the spell cue.\nBelow are the objects.",
               0.0,
               "(Step 2)\nFirst, select the input object.\nSecond, select the output object.",
               "Again, use the marked keys for your choice:",
               0,
               "If you don't know the answer,\npress the 'next' key (right thumb).",
               "As a refresher you get a second look at Philbertines cheat sheet before you continue."]

Intro = [0, 
         "You are a magic novice preparing for\nyour exam in Alteration magic!",
         "As you may know, Alteration spells\nchange the world around you.",
         "Luckily, you own a copy of the famous book 'Elements of Alteration Magic'...",
         1,
         "... famously written by Philbertine:",
         2,
         "The introductory chapter\nlists the following beginner objects:",
         3,
         "With the correct spell, each beginner object\ncan be transformed into another!",
         "Here you see an example of such a spell:",
         4,
         "Note, that these spells affect\nall susceptible objects on the display.",
         5,
         "Each spell has a specific name and symbol. Philbertine provides a"\
             " cheat-sheet for the " + str(nMaps) + " beginner spells.",
         "You need to spend a minute to memorize them.",
         "You may go back across the cheat sheet pages.",
         "Ready?"]

    
Navigation1 = [0,
              "There is no shame in going back pages.",
              "If you have any questions\nor need to abort the experiment,\nplease ask the examiner.",
              "Now, the experiment begins..."
              ]


Navigation3 = [0,
              "This is the final session of the experiment.",
              "If you need to abort the experiment,\nor you have any questions,\n"\
                  "please ask the examiner.",
              "Now, the experiment begins..."
              ]

objectDecoder = [
    "The (very large) magical helmet above you\nreads your mind.",
    "Everyone's mind is special,\nso before your magical journey starts...",
    "...the helmet has to be attuned to your mind.",
    "You will see objects on the screen.",
    "Sometimes, you will see a big object\nin the center of the screen:",
    "You then need to indicate via keypress,\nwhether the object is the same as the previous one.",
    "Please use the following keys for this task:",
    0,
    "Ready?"]

objectDecoderPost = [
    "The magical helmet is now accustomed\nto your thought patterns.",
    "It says, you have a beautiful mind. :)",
    "Now, your journey begins..."]
    


positionFirst = TestTypes + [
    "(Step 4)\nOne of the squares will be marked.\n\nChoose the object on that square after the transformation.",
    2.0,
    "Use the following keys for this choice:",
    2,
    "If you don't know the answer,\npress the 'next' key (right thumb).",
    "This test continues\nuntil you have enough correct responses.",
    "Ready?"]

positionSecond = ["Nicely done! Some magic students tend to cheat on this though.",
                  "We need to make sure that you transform the objects in your mind first and only then answer a test question.\n\nThat's why there are two test displays!",
                  "The previous one was based on object counting. The next will be based on the object positions.",
                  "(Steps 1-3) The procedure is the same as before.",
                  0.0,
                  "(Step 4)\nOne of the squares will be marked.\n\nChoose the object on that square after the transformation.",
                  1.0,
                  "Again, use the following keys for this choice:",
                  0,
                  "If you don't know the answer,\npress the 'next' key (right thumb).",
                  "This test continues\nuntil you have enough correct responses.",
                  "Ready?"] 

    
PrimitivesMEGR = [0,
                "You have studied diligently\nand are well prepared for your magic exam.",
                "In the first of two exam parts,\nyour task is the one you practiced in the last session.",
                "One important difference: You will not know"\
                    "\nwhich of the two tests comes at the end of any trial.",
                "You hopefully still remember the procedure, but here's a reminder:",
                "You first see a set of objects:\n(1) Memorize the presented objects.",
                0.0,
                "When you are done with memorizing:\n(2) Press the right thumb button.",
                "You will then see a spell cue.",
                1.0,
                "(3) In your head, apply it to the memorized display.",
                "When you are done:\n(4) Press the right thumb button.",
                "Then you can receive one of two possible test displays:\nCounting or Position.",
                "Type 1 - Counting: You will see an object category and integers on the bottom.",
                2.0,
                "(5) From the options below, choose how often "\
                "this object appears in the scene after the transformation.",
                "Type 2 - Position query: You will see all the squares on which the objects stood, "\
                            "one of them will be marked.",
                3.0,
                "(5) From the options below, choose the object that would be "\
                        "on the marked square after the transformation.",
                "Use the following keys:",
                1,
                "If you don't know the answer, please press the (red) 'next'.",
                "This test continues\nuntil you have enough correct responses.",
                "Be as accurate and as fast as possible.",
                "Remember to move as little as possible for the helmet.",
                "Ready to begin the exam?"]


spellDecoder = ["Nicely done!\nYou are almost ready for the exam.",
    "The magical helmet above you\nalso reads your spellcasting.\n\nBefore the exam,\nit has to be attuned to yours.",
    "For this, you need to do a set\nof easy Alteration trials:",
    "Only one object will be shown in each trial.\nYou will have to transform it as usual.",
    "Please use the following keys for this task:",
    0,
    "Be as accurate and as fast as possible.",
    "Try to move as little as possible:\nThe helmet will be attuned quicker this way.",
    "Ready?"]


    
    
# ============================================================================
# Store as Dictionary
instructions ={  
  "lang": "Eng",  
  "exp": "CompInf",
  
  "Intro": AddProceedKey2All(Intro, '/k'),
  "Navigation1": AddProceedKey2All(Navigation1, '/k'),
  "Navigation3": AddProceedKey2All(Navigation3, '/k'),
  "Intermezzo1": AddProceedKey2All(Intermezzo1, '/k'),
  "Intermezzo2": AddProceedKey2All(Intermezzo2, '/k'),
  "Bye": AddProceedKey2All(Bye, '/k'),
  "ByeBye": AddProceedKey2All(ByeBye, '/k'),
  
  "TestTypes": AddProceedKey2All(TestTypes, '/k'),
  "positionFirst": AddProceedKey2All(positionFirst, '/k'),
  "positionSecond": AddProceedKey2All(positionSecond, '/k'),
  "countFirst": AddProceedKey2All(countFirst, '/k'),
  "countSecond": AddProceedKey2All(countSecond, '/k'),
  
  "PrimitivesMEGR": AddProceedKey2All(PrimitivesMEGR, '/k'),
  "BinariesMEGR": AddProceedKey2All(BinariesMEGR, '/k'),
  "InterleavedMEGR": AddProceedKey2All(InterleavedMEGR, '/k'),
  "AutonomousMEGR": AddProceedKey2All(AutonomousMEGR, '/k'),
  
  "objectDecoder": AddProceedKey2All(objectDecoder, '/k'),
  "objectDecoderPost": AddProceedKey2All(objectDecoderPost, '/k'),
  "spellDecoder": AddProceedKey2All(spellDecoder, '/k'),
  
}  

with open('instructions_en.pkl', 'wb') as handle:
    pickle.dump(instructions, handle, protocol=pickle.HIGHEST_PROTOCOL)