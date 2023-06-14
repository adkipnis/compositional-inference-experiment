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


Binaries = [0,
            "Well done!",
            "Today's final lesson: Cues for different spells"\
                "\ncan be combined to produce new spells.",
            "Essentially, the final result of a double spell\nis as if you apply the first spell,...",
            "take the intermediate result\nand then apply the second spell on it.",
            
            "Here's an example:",
            "(1) Memorize the presented objects.",
            0.0,
            "When you are done:\n(2) Press the (red) 'next' key.",
            "You will then see two(!) spell cues.",
            1.0,
            "(3) In your mind, apply both spells\nto the memorized display.",
            "When you are done:\n(4) Press the (red) 'next' key.",
            2.0,
            "Then you can receive one of two possible test displays,\nthey are analogous to the previous trials.",
            "You will now be tested on these 'composed' spells.",
            "This time you only need to get at least 75% of them right.",
            "Again, use the following keys for the decision at the end of each trial:",
            1,
            "If you don't know the answer, press the (red) 'next' key.",
            "Ready?"]

BinariesMEG = [0,
            "Well done, you have finished the first part!",
            "The second part of the exam is like the first one,\nbut with two spell cues:",
            "You apply the first spell,\ntake the intermediate result"\
                "\nand then apply the second spell on it.",
            "Again, use the following keys:",
            1,
            "If you don't know the answer, press the (red) 'next' key.",
            "Be as accurate as possible.",
            "Ready?"]
    
BinariesMEGR = [0,
            "Well done, you have finished the first part!",
            "The second part of the exam is like the first one,\nbut with two spell cues",
            "Essentially, these 'double spells' require you\nto apply each primitive spell sequentially.",
            "The result is as if you apply the first spell,\ntake the intermediate result\nand then apply the second spell on that.",
            "Here's an example:",
            "(1) Memorize the presented objects.",
            0.0,
            "When you are done:\n(2) Press the (red) 'next' key.",
            "You will then see two(!) spell cues.",
            1.0,
            "(3) In your mind, apply both spells to the memorized display.",
            "When you are done:\n(4) Press the (red) 'next' key.",
            "Then you can receive one of two possible test displays,\nthey are analogous to the previous trials.",
            "Importantly, there is an invisible counter for each spell cue:",
            1,
            "If you answer fast and correctly,\nthe counter will increase by 1.\nYour response will be marked green.",
            "If your answer is correct but slow,\nthe counter will stay the same.\nYour response will be marked yellow.",
            "If you answer incorrectly,\nthe counter will decrease by 1.\nYour response will be marked red.",
            "Your goal is to reach a counter of 15\nfor each double spell.",
            "The counter cannot go beyond 15,\nso the progress bar won't increase for spells\nwhich you have mastered.",
            "Again, use the following keys for the decision at the end of each trial:",
            2,
            "If you don't know the answer, press the (red) 'next' key.",
            "This will not affect the counter,\nso it is better to admit ignorance than to guess!",
            "Be as accurate and as fast as possible.",
            "Remember to move as little as possible for the helmet.",
            "Ready to finish the exam?"]
    
Bye = ["Congrats!",
       "You are done with your Alteration studies for today.",
       "See you in your next session!"]

ByeBye = ["Congrats!",
       "You have finished your exam.",
       "The magical council will send you your grade and reward soon.",
       "Farewell on your remaining magical journey. :)"]


countFirst = ["Here is what you do:",
                "(1) Memorize the presented objects:",
                0.0,
                "When you are done with memorizing:\n(2) Press the (red) 'next' key.",
                "You will then see a spell cue.\n(3) In your mind, apply it to the memorized display.",
                1.0,
                "When you are done:\n(4) Press the (red) 'next' key.",
                "You will now see an object category\nand some integers on the bottom",
                2.0,
                "(5) From the options below, choose how often "\
                    "this object appears in the scene after the transformation.",
                "For training purposes you will get immediate feedback.",
                "Let's say, you incorrectly chose the leftmost option:",
                3.0,
                "Importantly, there is an invisible counter for each spell cue:",
                0,
                "The progress bar on the top of the screen\nis the summary of all counters.",
                "If you answer incorrectly,\nthe counter will decrease by 1.\nYour response will be marked red.",
                "If you answer fast and correctly,\nthe counter will increase by 1.\nYour response will be marked green.",
                "If your answer is correct but slow,\nthe counter will stay the same.\nYour response will be marked yellow.",
                "Your goal is to reach a counter of 10\nfor each spell cue.",
                "The counter cannot go beyond 10,\nso the progress bar won't increase for spells\nwhich you have mastered.",
                "Use the following keys for this choice:",
                1,
                "If you don't know the answer, press the (red) 'next' key.",
                "Place your fingers\non only the marked keys now.",
                "Ready?"]

countSecond = ["Some magic students tend to cheat on the test above.",
               "In order to make sure\nthat you transform the objects in your mind "\
                   "first\nand only then answer a test question...",
              "...there are two test displays\n(both equally likely to appear):",
              "The previous one was based on object positions.\nThe next will be based "\
                  "on the object count.",
              "After memorizing and transforming the objects\n(steps 1-4)...",
              0.0,
              "you will see an object category\nand some integers on the bottom.",
              1.0,
              "(5) From the options below, choose how often "\
                  "this object appears in the scene after the transformation.",
              "For training purposes you will get immediate feedback:",
              2.0,
              "Again, use the following keys for this choice:",
              0,
              "If you don't know the answer, press the (red) 'next' key.",
              "Place your fingers\non only the marked keys now.",
              "Ready?"] 

DropOut = ["Luck is not on your side today.",
           "You've answered less than 80%\nof the questions correctly, again.",
           "The magical helmet judges that\nyou are not ready.",
           "Unfortunately this concludes the experiment.",
           "Your participation will be\ncompensated nonetheless, of course.",
           "Have a nice day, goodbye!"]

Feedback0 = ["In this training run, your score was:",
             0,
             "You feel like you can do better, so you decide to have another "\
                 "look at the cheat sheet and then train a little more."]
Feedback0Test =  ["In this training run, your score was:",
                  0,
                  "You feel like you can do better."]   
Feedback1 = ["In this training run, your score was:", 
             0, 
             "This is good, you are confident to continue..."]

Intermezzo1 = ["Now that you have committed the spell cues\nto your memory, you"\
                   " want to make sure\nyou remember them correctly.",
               "In her wise anticipation, Philbertine provides you\nwith a"\
                   " magical practice board.",
               "You will first see the spell cue.\nThen you need to select the"\
                   " two corresponding objects:",
               "(1) The object which is susceptible to the spell",
               "...and (2) the object into which it is transformed.",
               "You choose the two objects using the marked keys\non your keyboard:",
               0,
               "The blue keys will correspond to your options\nfrom left to right.",
               "If you don't know the answer,\npress the (red) 'next' key.",
               "Importantly, there is an invisible counter for each spell cue:",
               1,
               "If you answer incorrectly,\nthe counter will decrease.\nYour response will be marked red.",
               "If you answer correctly within 2 seconds,\nthe counter will increase.\nYour response will be marked green.",
               "If your answer is correct but slow,\nthe counter will stay the same.\nYour response will be marked yellow.",
               "Each correct answer will increase the progress bar:",
               "Your goal is to reach a counter of 5\nfor each spell cue.",
               "The counter cannot go beyond 5,\nso the progress bar won't increase for spells\nwhich you have mastered.",
               "Place your fingers\non only the marked keys now.",
               "Ready?"]
    
Intermezzo2 = ["You have mastered the first type of spell cue.\nCongrats!",
               "Next, you will see if you have correctly learned\nthe second type of spell cue.",
                "The following practice board is\ncompletely analogous to the previous"\
                    " one.",
                "Again, you choose the objects using\nthe marked keys on your keyboard:",
                0,
                "If you don't know the answer, press the (red) 'next' key.",
                "Just as a refresher you get a second look\nat Philbertines cheat sheet before you continue."]

Intro = [0, 
         "You are a magic novice preparing for\nyour course in Alteration magic.",
         "As you may know, Alteration spells\nchange the world around you.",
         "Luckily, you own a copy of the famous book series"\
             " 'Principles of Alteration Magic'...",
         1,
         "... famously written by Philbertine:",
         2,
         "The introductory chapter\nlists the following beginner objects:",
         3,
         "With the correct spell, each beginner object\ncan be transformed into "\
             "another beginner object!",
         "Here you see an example of such an Alteration spell:",
         4,
         "Note, that these spells have an area effect: If you cast it,"\
             " all susceptible objects will be transformed.",
         5,
         "Each spell has a specific name and symbol. Philbertine provides a"\
             " cheat-sheet for the " + str(nMaps) + " beginner spells.",
         "You need to spend a minute to study them really well.",
             "Specifically, you need to learn the exact name and symbol "\
         "which are associated with each respective spell.",
         "You may go back across the cheat sheet pages.",
         "Ready?"]

IntroAdvanced = ["Since the last time, you have advanced in your Alteration studies.",
         "Philbertine would be impressed.",
         "You now know all elements of Alteration:",
         "(1) The two types of spell cue...",
         "And (2) the two types of spell tests...",
         "Just as a refresher you will do\na couple of trials for each of these.",
         "You start with the spell cues.\nUse the following keys:",
         0,
         "Ready?"]

IntroMEG = [
    "Today is the day of your exam\nin the art of Alteration.",
    "You have trained hard to get here."] #TODO more text
        

    
Navigation1 = [0,
              "Don't worry, there is no shame in going back pages.",
              "In this first session, you will prepare the basics of the task.",
              "If you have any questions\nor need to abort the experiment,\nplease ask the examiner.",
              "Now, the experiment begins..."
              ]

Navigation2 = [0,
              "In this second session, you will train the actual task.",
              "If for some reason you need to abort the experiment, you can"\
                  " do so by pressing Esc:",
              1,
              "Please be careful not to press this key by accident!",
              "Finally, if you have any questions, please ask the examiner.",
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
    "Everyone's mind is special,\nso before your magical journey start...",
    "...the helmet has to be attuned to your mind.",
    "For this, you will see objects on the screen.",
    "Sometimes, you will see a big object\nin the center of the screen:",
    "You then need to indicate via keypress,\nwhether the object is the same as the previous one.",
    "Please use the following keys for this task:",
    0,
    "Place your fingers\non only the marked keys now.",
    "Ready?"]

objectDecoderPost = [
    "The magical helmet is now accustomed\nto your thought patterns.",
    "It says, you have a beautiful mind. :)",
    "Now, your journey begins..."]
    


positionFirst = ["Here is what you do:",
                "(1) Memorize the presented objects:",
                0.0,
                "When you are done with memorizing:\n(2) Press the (red) 'next' key.",
                "You will then see a spell cue.\n(3) In your mind, apply it to the memorized display.",
                1.0,
                "When you are done:\n(4) Press the (red) 'next' key.",
                "You will see all the squares on which the objects stood, "\
                    "one of them will be marked.",
                2.0,
                "(5) From the options below, choose the object that would be "\
                        "on the marked square after the transformation.",
                "For training purposes you will get immediate feedback.",
                "Let's say, you incorrectly chose the following option -\nthen feedback would look like this:",
                3.0,
                "Importantly, there is an invisible counter for each spell cue:",
                0,
                "The progress bar on the top of the screen\nis the summary of all counters.",
                "If you answer incorrectly,\nthe counter will decrease by 1.\nYour response will be marked red.",
                "If you answer fast and correctly,\nthe counter will increase by 1.\nYour response will be marked green.",
                "If your answer is correct but slow,\nthe counter will stay the same.\nYour response will be marked yellow.",
                "Your goal is to reach a counter of 10\nfor each spell cue.",
                "The counter cannot go beyond 10,\nso the progress bar won't increase for spells\nwhich you have mastered.",
                "Use the following keys for this choice:",
                1,
                "If you don't know the answer, press the (red) 'next' key.",
                "Place your fingers\non only the marked keys now.",
                "Ready?"]
    
positionSecond = ["Some magic students tend to cheat on the test above.",
                  "In order to make sure\nthat you transform the objects in your mind "\
                      "first\nand only then answer a test question...",
                  "...there are two test displays\n(both equally likely to appear).",
                  "The previous one was based on object count.\nThe next will be based "\
                      "on the object positions.",
                  "After memorizing and transforming the objects\n(steps 1-4)...",
                  0.0,
                  "you will see all the squares on which the objects stood. "\
                      "\nOne of them will be marked.",
                  1.0,
                  "(5) From the options below, choose the object that would be "\
                      "on the marked square after the transformation.",
                  "For training purposes you will get immediate feedback:",
                  2.0,
                  "Again, use the following keys for this choice:",
                  0,
                  "If you don't know the answer, press the (red) 'next' key.",
                  "Place your fingers\non only the marked keys now.",
                  "Ready?"] 

PrimDecMEG1 = [0,
              "Now that you have familiarized yourself\nwith the new objects,...",
              "...you probably know what comes next.",
              "Next come three new spells,\nwhich are very similar to the ones\nyou have practiced earlier.",
              "Memorize them."]
PrimDecMEG2 = ["You get a chance to practice applying the spells.",
               "This time, only one object will be presented\nto you on each trial.",
               "Apply the cued spell on it and choose the object\ninto which you have transformed it.",
               "Use the following keys:",
               0,
               "This will also help to fine-tune the magical helmet.",
               "Therefore, try to move as little as possible.\nThe helmet will be "\
                   "attuned quicker\nthis way.",
               "Ready?"]    
    
Primitives = [0,
              "In your examination during the next session, you will perform tasks"\
                  " which are very similar to the ones you trained in the first session.",
              "One important difference: You will not know"\
                  "\nwhich of the two tests comes at the end of any trial.",
              "To ensure that you achieve your study goals,\nyou practice this scenario now.",
              "You need to get at least 90% of all practice trials right.",
              "Again, use the following keys for the decision\nat the end of each trial:",
              1,
              "If you don't know the answer, press the (red) 'next' key.",
              "Ready?"]
    
PrimitivesMEG = [0,
              "The magical helmet is now accustomed\nto your thought patterns.",
              "It says, you have a beautiful mind. :)",
              "You will surely put it to good use in the exam.",
              "In the first of two exam parts,\nyour task is the one you practiced in the last session.",
              "You hopefully still remember it, but here's a reminder:",
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
              "If you don't know the answer, press the (red) 'next' key.",
              "Be as accurate as possible\n-\nyour reward will depend on it!",
              "Remember to move as little as possible for the helmet.",
              "Ready to begin the exam?"]

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
                "Importantly, there is an invisible counter for each spell cue:",
                1,
                "The progress bar on the top of the screen\nis the summary of all counters.",
                "If you answer fast and correctly,\nthe counter will increase by 1.\nYour response will be marked green.",
                "If your answer is correct but slow,\nthe counter will stay the same.\nYour response will be marked yellow.",
                "If you answer incorrectly,\nthe counter will decrease by 1.\nYour response will be marked red.",
                "Your goal is to reach a counter of 20\nfor each spell.",
                "The counter cannot go beyond 20,\nso the progress bar won't increase for spells\nwhich you have mastered.",
                "Use the following keys:",
                2,
                "If you don't know the answer, please press the (red) 'next'.",
                "This will not affect the counter,\nso it is better to admit ignorance than to guess!",
                "Be as accurate and as fast as possible.",
                "Remember to move as little as possible for the helmet.",
                "Ready to begin the exam?"]

spellDecoder = [
    "The magical helmet above you\nalso reads your spellcasting.",
    "Before the exam,\nit has to be attuned to yours.",
    "For this, you need to do a set\nof easy Alteration trials:",
    "Only one object will be shown in each trial.\nYou will have to transform it as usual.",
    "Importantly, there is an invisible counter for each spell cue:",
    0,
    "The progress bar on the top of the screen\nis the summary of all counters.",
    "If you answer fast and correctly,\nyour response will be marked green.",
    "The counter will then increase by 1\nonly if a spell was applied.\n Otherwise it will stay the same.",
    "It will also stay the same\nif your answer is correct but slow.\nYour response will be marked yellow, though.",
    "If you answer incorrectly,\nthe counter will stay the same\nbut the trial may reappear later.\nYour response will be marked red.",
    "Your goal is to reach a counter of 16\nfor each spell.",
    "The counter cannot go beyond 16,\nso the progress bar won't increase for spells\nwhich you have mastered.",
    "Please use the following keys for this task:",
    1,
    "Try to move as little as possible:\nThe helmet will be attuned quicker this way.",
    "Ready?"]

TestTypes = [0,
             "It is time for some field practice.",
             "You now know the spell names and symbols\nwhich prompt you to "\
                 "cast a spell.",
             "You will now practice applying these spells\nto groups of objects.",
             "Earlier, you saw what effect alteration spells had.",
             "For the following trials, you will first see the spell cue "\
                 "and then the objects you need to transform using it.",       # TODO update order 
             "It will look like this:",
             0.0]
    
TestTypesReminder = [0,
             "You hopefully still remember\nhow you used spells in your first session.",
             "Just to be safe, here's a reminder:",
             "You first see a set of objects:\n(1) Memorize the presented objects.",
             0.0,
             "When you are done with memorizing:\n(2) Press the (red) 'next' key.",
             "You will then see a spell cue.",
             1.0,
             "(3) In your head, apply it to the memorized display.",
             "When you are done:\n(4) Press the (red) 'next' key.",
             2.0,
             "Then you can receive one of two possible test displays:\nCounting or Position.",
             "Type 1 - Counting: You will see an object category and integers on the bottom.",
             3.0,
             "(5) From the options below, choose how often "\
             "this object appears in the scene after the transformation.",
             "Type 2 - Position query: You will see all the squares on which the objects stood, "\
                        "one of them will be marked.",
             4.0,
             "(5) From the options below, choose the object that would be "\
                    "on the marked square after the transformation.",
             "Use the following keys for your choice:",
             1,
             "If you don't know the answer, press the (red) 'next' key.",
             "It's important that you understand the instructions, so please go "\
                 "back and review them if you are unsure. Otherwise click next."
             ]    

    
# ============================================================================
# Store as Dictionary
instructions ={  
  "lang": "Eng",  
  "exp": "CompInf",
  
  "Binaries": AddProceedKey2All(Binaries, '/k'),
  "BinariesMEGR": AddProceedKey2All(BinariesMEGR, '/k'),
  
  "Bye": AddProceedKey2All(Bye, '/k'),
  "ByeBye": AddProceedKey2All(ByeBye, '/k'),
  "DropOut": AddProceedKey2All(DropOut, '/k'),
  
  "Feedback0": AddProceedKey2All(Feedback0, '/e', wait_s = 3),
  "Feedback0Test": AddProceedKey2All(Feedback0Test, '/e', wait_s = 3),
  "Feedback1": AddProceedKey2All(Feedback1, '/e', wait_s = 2),
  
  "Intermezzo1": AddProceedKey2All(Intermezzo1, '/k'),
  "Intermezzo2": AddProceedKey2All(Intermezzo2, '/k'),
  
  "Intro": AddProceedKey2All(Intro, '/k'),
  "IntroAdvanced": AddProceedKey2All(IntroAdvanced, '/k'),  
  "IntroMEG": AddProceedKey2All(IntroMEG, '/k'),  
  
  "Navigation1": AddProceedKey2All(Navigation1, '/k'),
  "Navigation2": AddProceedKey2All(Navigation2, '/k'),
  "Navigation3": AddProceedKey2All(Navigation3, '/k'),
  
  "objectDecoder": AddProceedKey2All(objectDecoder, '/k'),
  "objectDecoderPost": AddProceedKey2All(objectDecoderPost, '/k'),
  "spellDecoder": AddProceedKey2All(spellDecoder, '/k'),
  "PrimDecMEG1": AddProceedKey2All(PrimDecMEG1, '/k'),
  "PrimDecMEG2": AddProceedKey2All(PrimDecMEG2, '/k'),
  "Primitives": AddProceedKey2All(Primitives, '/k'),
  "PrimitivesMEGR": AddProceedKey2All(PrimitivesMEGR, '/k'),
  
  "TestTypes": AddProceedKey2All(TestTypes, '/k'),
  "positionFirst": AddProceedKey2All(positionFirst, '/k'),
  "positionSecond": AddProceedKey2All(positionSecond, '/k'),
  "countFirst": AddProceedKey2All(countFirst, '/k'),
  "countSecond": AddProceedKey2All(countSecond, '/k'),
  "TestTypesReminder": AddProceedKey2All(TestTypesReminder, '/k'),
}  

with open('instructions_en.pkl', 'wb') as handle:
    pickle.dump(instructions, handle, protocol=pickle.HIGHEST_PROTOCOL)