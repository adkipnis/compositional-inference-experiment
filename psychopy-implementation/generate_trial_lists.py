#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 18:07:53 2021

@author: alex
"""
import os, glob, pickle, string
from itertools import product 
from itertools import combinations
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
plt.close("all")
main_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(main_dir)
stim_dir = os.path.join(main_dir, "stimuli")
trial_list_dir = os.path.join(main_dir, "trial-lists")

#=============================================================================
# Helper Functions

def cartesian_product(items, discard_reps = True,
                      strcat = True, sep='-'):
    '''generate the space of all possible combinations of a list of items
       optionally remove cases where item1 == item2'''
    if strcat:
        item_space = np.array([sep.join(i) for i in product(items, items)])
    else:
        item_space = np.array([list(i) for i in product(items, items)])
    if discard_reps:
        dupe_idx = list(range(0,len(item_space),len(items)+1))
        item_space = np.delete(item_space, dupe_idx, axis = 0)
    return item_space


def analyze_map_type(general_map, sep='-'):
    '''analyzes list of compositions for the cases:
        X-Y-X-Z (empty-maps = only execute first map)
        X-Y-Y-X (auto-maps OR only second map if Y is in input display)
        X-Y-Y-Z (transitive maps) = X-Z-Y-Z (OR-map)
        X-Y-Z-X (rotation-maps)
        X-Y-Z-Y (OR-maps)
        X-Y-Z-O (generic maps = parallelisable maps)'''
    
    t = np.concatenate(np.char.split(general_map, sep = sep))
    if len(t) == 2:
        map_type = 'primitive'
    else:
        if t[0]==t[2]:
            map_type = 'first-only' 
        elif t[0]==t[3] and t[1]==t[2]:
            map_type = 'second-only' 
        elif t[0]!=t[3] and t[1]==t[2]:
            map_type = 'transitive' 
        elif t[0]==t[3] and t[1]!=t[2]:
            map_type = 'rotation' 
        elif t[1]==t[3]:
            map_type = 'OR' 
        elif t[0]!=t[1]!=t[2]!=t[3]:
            map_type = 'generic' 
        else:
            map_type = 'unclear' 
    return map_type


def get_arg_set(general_map, sep = '-'):
    ''' takes map and generates a (mathematical) set of unique arguments that
        it contains'''
    t = np.concatenate(np.char.split(general_map, sep = sep))
    return set(t)


def split_into_categories(List, sep='-'):
    ''' takes List with general_maps (string elements interleaved by sep) and
        splits the list according to the types shown in analyze_map_type and
        stores them in a dictionary
        
    assumes that the following cases do not occur:
        X-X-?-? or ?-?-X-X (elementary auto-maps)
        X-Y-X-Y (duplicate maps)'''
    maps_first_only, maps_second_only, maps_trans, maps_rot, maps_or,\
        maps_generic =[],[],[],[],[],[]

    for i in range(len(List)):
        map_type = analyze_map_type(List[i], sep='-')
        if map_type == 'first-only':
            maps_first_only.append(i) 
        elif map_type == 'second-only':
            maps_second_only.append(i)
        elif map_type == 'transitive':
            maps_trans.append(i)
        elif map_type == 'rotation':
            maps_rot.append(i)
        elif map_type == 'OR':
            maps_or.append(i)
        elif map_type == 'generic':
            maps_generic.append(i)
    
    # Store maps in dictionary
    binary_comps_dict = {"first-only" : List[maps_first_only],
                         "second-only" : List[maps_second_only],
                         "transitive" : List[maps_trans],
                         "rotation" : List[maps_rot],
                         "OR" : List[maps_or],
                         "generic" : List[maps_generic]
                         }
    return binary_comps_dict


def io_dist(List, sep='-'):
    ''' takes list with string elements interleaved by sep and
    analyzes the spread of the item distribution'''
    items = np.concatenate(np.char.split(List, sep = sep))
    instances, instance_count = np.unique(items, return_counts=True)
    return np.std(instance_count)


def gen_binary_compositions(T_unique, n_primitives = 5, min_type = 2,
                            sd_max = 0.5, sep = '-'):
    ''' Select n_primitives transmuters from T_unique, such that at least
        min_type binary compositions of each composition type listed below
        are composed from them AND the distribution of of primitive maps is
        balanced in terms of categories

        Returns T_selection and a dictionary with all derived compositions 
        '''
    sd = 99
    binary_comps_dict = {"second-only" : [],
                         "transitive" : [],
                         "generic" : []
                         }
    
    while len(binary_comps_dict["second-only"]) < min_type or \
          len(binary_comps_dict["transitive"]) < min_type or \
          len(binary_comps_dict["generic"]) < min_type or \
          sd > sd_max:
        T_selection = np.random.choice(T_unique,
                                       size = n_primitives,
                                       replace = False)
        sd = io_dist(T_selection, sep = sep)
        
        T_comp_unique = cartesian_product(T_selection,
                                          discard_reps = True,
                                          strcat = False,
                                          sep = sep)
        # Extract special types
        binary_comps_dict = split_into_categories(T_comp_unique)
    return T_selection, binary_comps_dict
   

def select_binary_compositions(binary_comps_dict):
    '''Takes dictionary of binary compositions and two second-only maps, such
       that the first primitive of only one second-only map does not appear in
       other compositions, returns a list of selected compositions'''
    maps_second_only = binary_comps_dict["second-only"]
    maps_trans = binary_comps_dict["transitive"]
    maps_generic = binary_comps_dict["generic"]
    
    idx_so = list(combinations([i for i in range(len(maps_second_only))], 2))
    idx_t = list(combinations([i for i in range(len(maps_trans))], 2))
    idx_g = list(combinations([i for i in range(len(maps_generic))], 2))
    
    working_indices = []
    
    for idx_1 in idx_so:
        selection_second_only = maps_second_only[idx_1, :]
        prim_so_1, prim_so_2 = selection_second_only[0,0], selection_second_only[1,0]
        
        if prim_so_1 != selection_second_only[1,1] and \
            prim_so_2 != selection_second_only[0,1]:
        
            for idx_2 in idx_t:
                for idx_3 in idx_g:
                    selection_rest = np.concatenate((maps_trans[idx_2, :],
                                                     maps_generic[idx_3, :]))
                    count_1 = np.count_nonzero(selection_rest == prim_so_1)
                    count_2 = np.count_nonzero(selection_rest == prim_so_2)
                    
                    if count_1 > 0 and count_2 == 0 or count_2 > 0 and count_1 == 0:
                            working_indices.append([[idx_1, idx_2, idx_3],
                                                    [count_1, count_2]])
    working_indices = np.array(working_indices) 
    best_idx = working_indices[np.argmax(working_indices[:,1])]
    maps_selection = np.concatenate((maps_second_only[best_idx[0][0], :],
                                     maps_trans[best_idx[0][1], :],
                                     maps_generic[best_idx[0][2], :]))
    return maps_selection


def gen_special_trinary_compositions(selection_prim, selection_binary,
                                     sep = '-'):
    # TODO: Docstring, Selection of distinct comp in # 4.
    
    # 1. partition selection_binary 
    maps_second_only = []
    maps_rest = []
    for general_map in selection_binary:
        if analyze_map_type(general_map, sep=sep) == "second-only":
            maps_second_only.append(general_map)
        else:
            maps_rest.append(general_map)
    
    # 2. Analyze which primitive resp. composition is solitary 
    prim_so_1, prim_so_2 = np.array(maps_second_only)[0,0], \
        np.array(maps_second_only)[1,0]
    if np.count_nonzero(maps_rest == prim_so_1) == 0:
        prim_sol = [prim_so_1]
        prim_common = [prim_so_2]
        so_sol = list(np.array(maps_second_only)[0])
        so_common = list(np.array(maps_second_only)[1])
    else:
        prim_sol = [prim_so_2]
        prim_common = [prim_so_1]
        so_sol = list(np.array(maps_second_only)[1])
        so_common = list(np.array(maps_second_only)[0])
    
    # 3. so + distinct prim 
    rest_prim = np.setdiff1d(selection_prim,
                             np.ndarray.flatten(np.array(maps_second_only)))
    selected_prim = [rest_prim[0]]
    
    trinary_1 = np.concatenate((np.array(so_common), selected_prim))
    trinary_2 = np.concatenate((np.array(so_sol), selected_prim))
    
    # 4. prim_sol + distinct comp 
    trinary_3 = np.concatenate((prim_common, rest_prim))
    trinary_4 = np.concatenate((prim_sol, rest_prim))
    return np.stack((trinary_1, trinary_2, trinary_3, trinary_4))


def apply_map(display, general_map, past_transforms = 0, sep = '-'):
    ''' recursively apply maps to an initial display and return final image '''
    display_in = display.copy()
    if isinstance(general_map, str):
        general_map = [general_map]
    if len(general_map) > 0:
        map_tmp = general_map[0]
        remaining_maps = general_map[1:]
        t_in = map_tmp.split(sep)[0]
        t_out = map_tmp.split(sep)[1]
        past_transforms += sum(display_in==t_in)
        display_in[display_in==t_in] = t_out
        display_in, past_transforms = apply_map(display_in, remaining_maps,
                                             past_transforms = past_transforms,
                                             sep = sep)
    return display_in, past_transforms


def draw_count_target(stimuli, resp, instances, instance_count, p=None):
    '''draw a target item with an adaptive probability distr. depending on
        previous target draws, the correct response and output display'''
    target = None
    if p is None:
        p = np.tile(1/len(stimuli), len(stimuli))
    if resp in instance_count:
        p_idx = [item in instances[resp == instance_count] for item in stimuli]
        p_tmp = p[p_idx]
        if sum(p_tmp) > 0:
            p = p_tmp/sum(p_tmp)
            target = np.random.choice(instances[resp == instance_count], p = p)
        else:
            target = instances[resp == instance_count][0]
    elif resp == 0:
        remainder = list(set(stimuli)-set(instances))
        p_idx = [item in remainder for item in stimuli]
        p_tmp = p[p_idx]
        if sum(p_tmp) > 0:
            p = p_tmp/sum(p_tmp)
            target = np.random.choice(remainder, p = p)
        else:
            target = remainder[0]
    return target


def draw_position_target(stimuli, resp, display_out,
                         display_size = 6, n_options = 4, p = None):
    '''randomly draw a target position,
    put corresponding item from display_out into ordered response_options
    randomly fill the remaining options up with distinct categories'''
    target_position = None
    target_position = np.random.choice(range(display_size), p = p) # randomly draw position  # TODO: p
    target_item = display_out[target_position]
    response_options = np.tile(None, n_options) # init ordered response options
    response_options[resp] = target_item
    remaining_categories = np.delete(stimuli, stimuli == target_item, axis = 0)
    other_options = np.random.choice(remaining_categories, size = n_options-1,
                                     replace = False)
    response_options[response_options == None] = other_options
    return target_position, response_options


def gen_trial_dict(stimuli, general_map, resp,
                   resp_list = None, test_type = "count", trial_type = "generic",
                   p = None, display_size = 5, max_duplicates = 3, sep = '-'):
    ''' takes a set of stimuli, a general map and a fixed correct response,
        then generates a dict containing adequate input, output displays,
        a target item and the (max) number of mental transformations''' 
    if isinstance(general_map, str):
        general_map = [general_map]
    map_type = analyze_map_type(general_map, sep = sep)        
    target = None
    max_ic = 99 #initialization

    # generate displays until criteria for counting are met
    while target is None or max_ic > max_duplicates:
        necessary_items = np.concatenate(
                            np.char.split(general_map, sep = sep))[0]
        if map_type == "second-only":
            necessary_items = np.append(
                necessary_items,
                np.concatenate(np.char.split(general_map, sep = sep))[2]
                )

        other_items = np.random.choice(stimuli,
                                       size = display_size-len(necessary_items),
                                       replace = True)
        display_in = np.append(necessary_items, other_items)                          
        display_out, past_transforms = apply_map(display_in, general_map,
                                                 sep = sep)
        instances, instance_count = np.unique(display_out,
                                              return_counts=True)
        max_ic = instance_count.max()
        if test_type == "count":
            response_options = resp_list.copy()
            target = draw_count_target(
                stimuli, resp, instances, instance_count, p = p) 
        elif test_type == "position":
            target, response_options = draw_position_target(
                    stimuli, resp, display_out, display_size = display_size,
                    n_options = len(resp_list), p = p) 
        else:
            raise Exception("Test type not implemented") 

                              
    # compile down
    compiled_map = compile_down(general_map, map_type = map_type,
                                display = display_in, sep = sep)
    if np.array_equal(compiled_map, general_map):
         past_transforms_sparse = past_transforms
    else:
        _, past_transforms_sparse = apply_map(display_in, compiled_map,
                                               sep = sep)     
    output_dict = {"trial_type" : trial_type,
                   "input_disp" : display_in,
                   "map" : general_map,
                   "output_disp": display_out,
                   "test_type": test_type,
                   "target": target,
                   "resp_options": response_options,
                   "correct_resp": resp,
                   "trans_ub" : past_transforms,
                   "trans_lb" : past_transforms_sparse,
                   "map_type" : map_type,
                   "arg_set": get_arg_set(general_map, sep = sep)}
    return output_dict


def gen_trials(stimuli, map_list,
               resp_list = list(range(4)),
               test_type = "count",
               trial_type = "generic",
               display_size = 6, sep='-'):
    ''' takes a list of maps and generates a datafreame (input display, map,
        output display, target, correct response)'''     
    if test_type == "count":
        target_list = stimuli.copy()
    elif test_type == "position":
        target_list = np.array(range(display_size))
    else:
        raise Exception("Test type not implemented") 
    trials = []
    num_trials = len(map_list)
    num_tiles_r = np.ceil(num_trials/len(resp_list)).astype('int')
    resp_sequence = np.random.permutation(np.tile(resp_list, num_tiles_r))
    target_urn = np.tile(num_trials/len(target_list), len(target_list))
    
    for i in range(num_trials):
        trial_dict = gen_trial_dict(stimuli, map_list[i], resp_sequence[i],
                                    test_type = test_type,
                                    trial_type = trial_type,
                                    resp_list = resp_list,
                                    p = target_urn/sum(target_urn),
                                    display_size = display_size, sep = sep)
        if target_urn[target_list == trial_dict["target"]] >= 1:
            target_urn[target_list == trial_dict["target"]] -= 1               #remove instance-specific counter from target urn
        # if sum(target_urn)+i+1 > 90:
        #     raise Exception("Target urn contains more targets than expected") 
        trials.append(pd.DataFrame(trial_dict.items()).set_index(0).T)
    df = pd.concat(trials, ignore_index=True)
    return df[["trial_type", "input_disp", "map", "output_disp", "test_type", "target",
               "resp_options", "correct_resp", "trans_ub", "trans_lb",
               "map_type", "arg_set"]]    

def map_to_integers(general_map, sep = '-'):
    ''' takes map and generates a list of corresponding integers'''
    categories = general_map.split(sep = sep)
    categories_int = []
    for i in range(len(categories)):
        categories_int.append(ord(categories[i]) - 65)
    return categories_int

def correct_cue_trial_resp(general_map, resp_options, sep = '-'):
    ''' takes map and an ordered list of response options
    and generates a list of integers corresponding to the position of the map
    argument positions in the resp_options'''
    categories = general_map.split(sep = sep)
    correct_resp = []
    for cat in categories:
        correct_resp.append(np.where(resp_options == cat)[0][0])
    return correct_resp
    
def gen_cue_trials(map_list, stimuli,
                   display_size = 6, sep='-'):
    ''' takes a list of maps and generates a datafreame (map, target, correct response)'''     
    trials = []
    num_trials = len(map_list)
    for i in range(num_trials):
        general_map = [map_list[i]]
        resp_options = np.random.permutation(stimuli)
        correct_resp = correct_cue_trial_resp(general_map[0], resp_options,
                                              sep = sep)
        trial_dict = {"trial_type": "cue_memory",
                      "map" : general_map,
                      "resp_options": resp_options,
                      "correct_resp": correct_resp}
        trials.append(pd.DataFrame(trial_dict.items()).set_index(0).T)
    df = pd.concat(trials, ignore_index=True)
    return df  


def compile_down(general_map, map_type = None, display = None, sep = '-'):
    ''' takes map and generates sparser but equivalent version of it'''
    compiled_map = general_map
    if map_type is None:
        map_type = analyze_map_type(general_map, sep=sep)
    if map_type == "first-only":
        compiled_map = general_map[0]    
    elif map_type == "second-only":
        compiled_map = general_map[1]
    elif display is not None and map_type == "transitive":
        if general_map[0][2] not in display:
            compiled_map = general_map[0][0] + sep + general_map[1][2]
    return compiled_map 

# ============================================================================
# Stimuli & Maps

# Design parameters
sep = '-'
n_stim = 6 #>= 4, otherwise no parallelizable compositions
display_size = 6
min_type = 3 #minimal number of instances per composition type
n_primitives = 6 
n_exposure = 30 #per primitive per block
stimuli = np.array(list(string.ascii_uppercase)[:n_stim])
resp_list = list(range(4))

# Generate all transmuters and compose binary maps from a selection thereof
unique_prim = cartesian_product(stimuli, discard_reps = True,
                                strcat = True, sep = sep)
selection_prim, comps_dict_binary = gen_binary_compositions(
                                    unique_prim,
                                    n_primitives = n_primitives,
                                    min_type = min_type,
                                    sd_max = 0.5,
                                    sep = sep)   

# Select binary maps such that the first primitive of only one second-only map
# does not appear in other compositions
selection_binary = select_binary_compositions(comps_dict_binary) 

## Alternatively: just select the first two of each
# selection_binary = np.concatenate([comps_dict_binary["second-only"][0:2],
#                                    comps_dict_binary["transitive"][0:2],
#                                    comps_dict_binary["generic"][0:2]])


# Generate structural conjugates for the selected binary maps (second draft)
unique_prim_rest = np.setdiff1d(unique_prim, selection_prim)
selection_prim_conj, comps_dict_binary_conj = gen_binary_compositions(
                                                unique_prim_rest,
                                                n_primitives = n_primitives,
                                                min_type = min_type,
                                                sd_max = 0.5,
                                                sep = sep)   
selection_binary_conj = select_binary_compositions(comps_dict_binary_conj) 
##Alternatively: Generate conjugate versions for the selected binary maps (
# df_binary_maps = gen_df_binary_maps(unique_prim, sep = sep)
# selection_conj_struct, selection_conj_arg = gen_conjugate_compositions(
#                                                     selection_binary,
#                                                     df_binary_maps,
#                                                     sep = sep)

# Generate trinary maps from the selected binary maps
selection_trinary = gen_special_trinary_compositions(selection_prim,
                                                     selection_binary,
                                                     sep = sep)


# ============================================================================
# Generate Blocks

n_participants = 2
tcue_list = pd.read_csv(stim_dir + os.sep + "spell_names.csv").columns.tolist()
vcue_list = glob.glob(stim_dir + os.sep + "c_*.png")
stim_list = glob.glob(stim_dir + os.sep + "s_*.png")

for i in range(1, n_participants+1):
    # Mappings between cues and stimuli
    tcue_list = np.random.permutation(tcue_list)
    vcue_list = np.random.permutation(vcue_list)
    stim_list = np.random.permutation(stim_list)
    fname = trial_list_dir + os.sep + str(i).zfill(2) + "_" + "mappinglists.pkl"
    data = {'tcue': tcue_list, 'vcue': vcue_list, 'stim': stim_list}
    with open(fname, "wb") as f:
        pickle.dump(data, f)
        
    # 0. Practice blocks
    # Cue Memory
    df_list = []
    for j in range(8):
        cue_list_prim = np.random.permutation(np.repeat(selection_prim, 5, axis = 0))
        df_list.append(gen_cue_trials(cue_list_prim, stimuli,
                                         display_size = 6, sep='-'))
    trials_prim_cue = pd.concat(df_list).sample(frac=1).reset_index(drop=True)    
    trials_prim_cue.to_pickle(trial_list_dir + os.sep + str(i).zfill(2) + "_" + "trials_prim_cue.pkl")
    
    # Test Practice: Count
    df_list = []
    for j in range(8):
        map_list_prim = np.random.permutation(np.repeat(selection_prim, 5, axis = 0))
        df_list.append(gen_trials(stimuli,
                                 map_list_prim,                         
                                 resp_list = resp_list,
                                 trial_type = "test_practice",
                                 test_type = "count",
                                 display_size = display_size,
                                 sep = sep))
    trials_prim_practice_c = pd.concat(df_list).sample(frac=1).reset_index(drop=True) 
    trials_prim_practice_c.to_pickle(trial_list_dir + os.sep + str(i).zfill(2) + "_" + "trials_prim_prac_c.pkl")
    
    # Test Practice: Position
    df_list = []
    for j in range(8):
        map_list_prim = np.random.permutation(np.repeat(selection_prim, 5, axis = 0))
        df_list.append(gen_trials(stimuli,
                                 map_list_prim,                         
                                 resp_list = resp_list,
                                 trial_type = "test_practice",
                                 test_type = "position",
                                 display_size = display_size,
                                 sep = sep))
    trials_prim_practice_p = pd.concat(df_list).sample(frac=1).reset_index(drop=True) 
    trials_prim_practice_p.to_pickle(trial_list_dir + os.sep + str(i).zfill(2) + "_" + "trials_prim_prac_p.pkl")
    
    # 1. Primitive blocks
    # generate trials twice with n_exposure/2 and each test display type,
    # then randomly permute both generated lists
    test_types = ["count", "position"]
    df_list = []
    for j in range(2):
        map_list_prim = np.random.permutation(np.repeat(selection_prim, np.ceil(n_exposure/2),
                                                axis = 0))
        df_list.append(gen_trials(stimuli,
                                 map_list_prim,                         
                                 resp_list = resp_list,
                                 test_type = test_types[j],
                                 display_size = display_size,
                                 sep = sep))
    trials_prim = pd.concat(df_list).sample(frac=1).reset_index(drop=True) 
    trials_prim.to_pickle(trial_list_dir + os.sep + str(i).zfill(2) + "_" + "trials_prim.pkl")
    # plt.figure()
    # trials_prim["correct_resp"].plot.hist(alpha=0.5)
    # trials_prim["trans_ub"].plot.hist(alpha=0.5)
    # trials_prim["target"].value_counts().plot(kind='bar')


    # 2. Compositional blocks
    df_list = []
    for j in range(2):
        map_list_binary = np.random.permutation(np.repeat(
            selection_binary, np.ceil(n_exposure/4), axis = 0))
        df_list.append(gen_trials(stimuli,
                                 map_list_binary,                         
                                 resp_list = resp_list,
                                 test_type = test_types[j],
                                 display_size = display_size,
                                 sep = sep))
    trials_binary = pd.concat(df_list).sample(frac=1).reset_index(drop=True) 
    trials_binary.to_pickle(trial_list_dir + os.sep + str(i).zfill(2) + "_" + "trials_bin.pkl")
    
    # trials_binary["correct_resp"].plot.hist(alpha=0.5)
    # trials_binary["trans_ub"].plot.hist(alpha=0.5)
    # trials_binary["target"].value_counts().plot(kind='bar')


# 3. Conjugate blocks
df_list = []
for j in range(2):
    map_list_binary_conj = np.random.permutation(np.repeat(
        selection_binary_conj, np.ceil(n_exposure/4), axis = 0))
    df_list.append(gen_trials(stimuli,
                             map_list_binary_conj,                         
                             resp_list = resp_list,
                             test_type = test_types[j],
                             display_size = display_size,
                             sep = sep))
trials_binary_conj = pd.concat(df_list).sample(frac=1).reset_index(drop=True) 


# 4. Trinary blocks
df_list = []
for j in range(2):
    map_list_trinary = np.random.permutation(
        np.repeat(selection_trinary, np.ceil(n_exposure/2), axis = 0))
    df_list.append(gen_trials(stimuli,
                             map_list_trinary,                         
                             resp_list = resp_list,
                             test_type = test_types[j],
                             display_size = display_size,
                             sep = sep))
trials_trinary = pd.concat(df_list).sample(frac=1).reset_index(drop=True) 

