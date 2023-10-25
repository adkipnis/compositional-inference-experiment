#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 18:07:53 2021

@author: alex
"""
import os
import glob
import string
import csv
import pickle
from pathlib import Path
from itertools import product, combinations, groupby
import numpy as np

# ==============================================================================
# User settings
first_participant = 1
n_participants = 10
save_this = True
ending = 'pkl'
sep = '-'
n_stim = 4  # >= 4, otherwise no parallelizable compositions
display_size = 4
n_primitives = 3
# minimal number of instances per composition type
min_type = np.floor(n_primitives/3)
n_exposure_prim = 30  # present each map n times for the main task
n_exposure_binary = 20  
n_exposure_practice = 10
maxn_repeats = 8  # maximum number of times a block of n_exposure * factor can be repeated
n_exposure_prim_dec = 30
n_exposure_loc = 10.  # present each entity n times per condition for the localizer task
percentage_catch = 0.1  # p * 100% of the trials will contain catch trials
n_exposure_loc_quick = round(n_exposure_loc * (1.-percentage_catch))
n_exposure_loc_catch = round(n_exposure_loc * percentage_catch)
stimuli = np.array(list(string.ascii_uppercase)[:n_stim])
resp_list = list(range(4))

# ==============================================================================
# Directories
main_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(main_dir)
stim_dir = os.path.join(main_dir, "stimuli")
trial_list_dir = os.path.join(main_dir, "trial-lists")
if not os.path.exists(trial_list_dir):
    os.makedirs(trial_list_dir)

# =============================================================================
# Functions


def listofdicts2csv(listofdicts, fname):
    keys = listofdicts[0].keys()
    with open(fname, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(listofdicts)


def save_object(obj, fname, ending='pkl'):
    if ending == 'csv':
        listofdicts2csv(obj, fname + '.csv')
    elif ending == 'pkl':
        with open(fname + '.pkl', "wb") as f:
            pickle.dump(obj, f)


def cartesian_product(items, discard_reps=True,
                      strcat=True, sep='-'):
    '''generate the space of all possible combinations of a list of items
       optionally remove cases where item1 == item2'''
    if strcat:
        item_space = np.array([sep.join(i) for i in product(items, items)])
    else:
        item_space = np.array([list(i) for i in product(items, items)])
    if discard_reps:
        dupe_idx = list(range(0, len(item_space), len(items)+1))
        item_space = np.delete(item_space, dupe_idx, axis=0)
    return item_space


def analyze_map_type(general_map, sep='-'):
    '''analyzes list of compositions for the cases:
        X-Y-X-Z (empty-maps = only execute first map)
        X-Y-Y-X (auto-maps OR only second map if Y is in input display)
        X-Y-Y-Z (transitive maps) = X-Z-Y-Z (OR-map)
        X-Y-Z-X (rotation-maps)
        X-Y-Z-Y (OR-maps)
        X-Y-Z-O (generic maps = parallelisable maps)'''

    t = np.concatenate(np.char.split(general_map, sep=sep))
    if len(t) == 2:
        map_type = 'primitive'
    else:
        if t[0] == t[2]:
            map_type = 'first-only'
        elif t[0] == t[3] and t[1] == t[2]:
            map_type = 'second-only'
        elif t[0] != t[3] and t[1] == t[2]:
            map_type = 'transitive'
        elif t[0] == t[3] and t[1] != t[2]:
            map_type = 'rotation'
        elif t[1] == t[3]:
            map_type = 'OR'
        elif t[0] != t[1] != t[2] != t[3]:
            map_type = 'generic'
        else:
            map_type = 'unclear'
    return map_type


def get_arg_set(general_map, sep='-'):
    ''' takes map and generates a (mathematical) set of unique arguments that
        it contains'''
    t = np.concatenate(np.char.split(general_map, sep=sep))
    return set(t)


def split_into_categories(List, sep='-'):
    ''' takes List with general_maps (string elements interleaved by sep) and
        splits the list according to the types shown in analyze_map_type and
        stores them in a dictionary

    assumes that the following cases do not occur:
        X-X-?-? or ?-?-X-X (elementary auto-maps)
        X-Y-X-Y (duplicate maps)'''
    maps_first_only, maps_second_only, maps_trans, maps_rot, maps_or,\
        maps_generic = [], [], [], [], [], []

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
    binary_comps_dict = {"first-only": List[maps_first_only],
                         "second-only": List[maps_second_only],
                         "transitive": List[maps_trans],
                         "rotation": List[maps_rot],
                         "OR": List[maps_or],
                         "generic": List[maps_generic]
                         }
    return binary_comps_dict


def io_dist(List, sep='-'):
    ''' takes list with string elements interleaved by sep and
    analyzes the spread of the item distribution'''
    items = np.concatenate(np.char.split(List, sep=sep))
    instances, instance_count = np.unique(items, return_counts=True)
    return np.std(instance_count)


def gen_binary_compositions(T_unique, n_primitives=5, min_type=2,
                            sd_max=0.5, sep='-'):
    ''' Select n_primitives transmuters from T_unique, such that at least
        min_type binary compositions of each composition type listed below
        are composed from them AND the distribution of of primitive maps is
        balanced in terms of categories

        Returns T_selection and a dictionary with all derived compositions 
        '''
    sd = 99
    binary_comps_dict = {"second-only": [],
                         "transitive": [],
                         "generic": []
                         }

    while len(binary_comps_dict["second-only"]) < min_type or \
            len(binary_comps_dict["generic"]) < min_type or \
            sd > sd_max:
        T_selection = np.random.choice(T_unique,
                                       size=n_primitives,
                                       replace=False)
        sd = io_dist(T_selection, sep=sep)

        T_comp_unique = cartesian_product(T_selection,
                                          discard_reps=True,
                                          strcat=False,
                                          sep=sep)
        # Extract special types
        binary_comps_dict = split_into_categories(T_comp_unique)
    return T_selection, binary_comps_dict


def select_binary_compositions(binary_comps_dict):
    '''Takes dictionary of binary compositions and two second-only maps, such
       that the first primitive of only one second-only map does not appear in
       other compositions, returns a list of selected compositions'''
    maps_second_only = binary_comps_dict["second-only"]
    maps_generic = binary_comps_dict["generic"]

    idx_so = list(combinations([i for i in range(len(maps_second_only))], 2))
    idx_g = list(combinations([i for i in range(len(maps_generic))], 2))

    working_indices = []

    for idx_1 in idx_so:
        selection_second_only = maps_second_only[idx_1, :]
        prim_so_1, prim_so_2 = selection_second_only[0,
                                                     0], selection_second_only[1, 0]

        for idx_2 in idx_g:
            selection_rest = maps_generic[idx_2, :]
            count_1 = np.count_nonzero(selection_rest == prim_so_1)
            count_2 = np.count_nonzero(selection_rest == prim_so_2)

            if count_1 > 0 and count_2 == 0 or count_2 > 0 and count_1 == 0:
                working_indices.append([[idx_1, idx_2],
                                        [count_1, count_2]])

    working_indices = np.array(working_indices, dtype=object)
    best_idx = working_indices[np.argmax(working_indices[:, 1])]
    maps_selection = np.concatenate((maps_second_only[best_idx[0][0], :],
                                     maps_generic[best_idx[0][1], :]))
    return maps_selection


def apply_map(display, general_map, past_transforms=0, sep='-'):
    ''' recursively apply maps to an initial display and return final image '''
    display_in = display.copy()
    intermediate_display = display_in.copy()
    if isinstance(general_map, str):
        general_map = [general_map]
    if len(general_map) > 0:
        map_tmp = general_map[0]
        remaining_maps = general_map[1:]
        t_in = map_tmp.split(sep)[0]
        t_out = map_tmp.split(sep)[1]
        past_transforms += sum(display_in == t_in)
        display_in[display_in == t_in] = t_out
        intermediate_display = display_in.copy()
        display_in, _, past_transforms = apply_map(display_in, remaining_maps,
                                                past_transforms=past_transforms,
                                                sep=sep)
    return display_in, intermediate_display, past_transforms 


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
            target = np.random.choice(instances[resp == instance_count], p=p)
        else:
            target = instances[resp == instance_count][0]
    elif resp == 0:
        remainder = list(set(stimuli)-set(instances))
        p_idx = [item in remainder for item in stimuli]
        p_tmp = p[p_idx]
        if sum(p_tmp) > 0:
            p = p_tmp/sum(p_tmp)
            target = np.random.choice(remainder, p=p)
        else:
            target = remainder[0]
    return target


def draw_position_target(stimuli, resp, display_out,
                         display_size=6, n_options=4, p=None):
    '''randomly draw a target position,
    put corresponding item from display_out into ordered response_options
    randomly fill the remaining options up with distinct categories'''
    target_position = None
    target_position = np.random.choice(
        range(display_size), p=p)  # randomly draw position
    target_item = display_out[target_position]
    # init ordered response options
    response_options = np.tile(None, n_options)
    response_options[resp] = target_item
    remaining_categories = np.delete(stimuli, stimuli == target_item, axis=0)
    other_options = np.random.choice(remaining_categories, size=n_options-1,
                                     replace=False)
    response_options[response_options == None] = other_options
    return target_position, response_options


def gen_trial_dict_object_dec(stimuli, stim_idx, pos_idx, jitter_interval=[-30, 30], catch=False):
    """ subroutine to generate a trial dictionary for object decoding task"""
    # input display
    stim = stimuli[stim_idx]
    input_disp = [None] * display_size
    input_disp[pos_idx] = stim
    jitter = np.random.choice(jitter_interval)/1000
    
    # catch trial specifics
    target = None
    correct_resp = None
    if catch:
        correct_resp = np.random.choice([True, False])
        if correct_resp:
            target = stim
        else:
            choice_set = np.delete(stimuli, stim_idx)
            target = np.random.choice(choice_set)
    
    # trial dictionary
    trial_dict = {"trial_type": "object_decoder",
                  "input_disp": input_disp,
                  "is_catch_trial": catch,
                  "target": target,
                  "correct_resp": correct_resp,
                  "jitter": jitter} 
    return trial_dict


def gen_trial_dict(stimuli, general_map, resp,
                   resp_list=None, test_type="count", trial_type="generic",
                   p=None, display_size=5, max_duplicates=3, jitter=0.0,
                   sep='-'):
    ''' takes a set of stimuli, a general map and a fixed correct response,
        then generates a dict containing adequate input, output displays,
        a target item and the (max) number of mental transformations'''
    if isinstance(general_map, str):
        general_map = [general_map]
    map_type = analyze_map_type(general_map, sep=sep)
    target = None
    max_ic = 99  # initialization

    # generate displays until criteria for counting are met
    while target is None or max_ic > max_duplicates:
        necessary_items = np.concatenate(
            np.char.split(general_map, sep=sep))[0]
        if map_type == "second-only":
            necessary_items = np.append(
                necessary_items,
                np.concatenate(np.char.split(general_map, sep=sep))[2]
            )

        other_items = np.random.choice(
            stimuli,
            size=display_size-len(necessary_items),
            replace=True,
            )
        display_in = np.append(necessary_items, other_items)
        display_in = np.random.permutation(display_in)
        display_out, intermediate_display, past_transforms = apply_map(
            display_in, general_map, sep=sep)
        instances, instance_count = np.unique(display_out,
                                              return_counts=True)
        max_ic = instance_count.max()
        if test_type == "count":
            response_options = np.array(resp_list)
            target = draw_count_target(
                stimuli, resp, instances, instance_count, p=p)
        elif test_type == "position":
            target, response_options = draw_position_target(
                stimuli, resp, display_out,
                display_size=display_size,
                n_options=len(resp_list),
                p=p,
                )
        else:
            raise Exception("Test type not implemented")

    # compile down
    compiled_map = compile_down(general_map,
                                map_type=map_type,
                                display=display_in,
                                sep=sep)
    if np.array_equal(compiled_map, general_map):
        past_transforms_sparse = past_transforms
    else:
        _, _, past_transforms_sparse = apply_map(
            display_in, compiled_map, sep=sep)
    output_dict = {"trial_type": trial_type,
                   "map_type": map_type,
                   "test_type": test_type,
                   "map": np.array(general_map),
                   "input_disp": display_in,
                   "intermediate_disp": intermediate_display,
                   "output_disp": display_out,
                   "target": target,
                   "resp_options": response_options,
                   "correct_resp": resp,
                   "trans_ub": past_transforms,
                   "trans_lb": past_transforms_sparse,
                   "jitter": jitter}
    return output_dict


def gen_trials(stimuli,
               map_list,
               resp_list=list(range(4)),
               test_type="count",
               trial_type="generic",
               display_size=4,
               jitter_interval=[-30, 30],
               randomize=False,
               sep='-'):
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
    sample_interval = list(range(jitter_interval[0], jitter_interval[1]+1))
    jitter = np.random.choice(
        sample_interval,
        replace=True,
        size=(num_trials, 3),
        ) / 1000

    for i in range(num_trials):
        trial_dict = gen_trial_dict(stimuli, map_list[i], resp_sequence[i],
                                    test_type=test_type,
                                    trial_type=trial_type,
                                    resp_list=resp_list,
                                    p=target_urn/sum(target_urn),
                                    display_size=display_size,
                                    jitter=jitter[i,],
                                    sep=sep)
        if target_urn[target_list == trial_dict["target"]] >= 1:
            # remove instance-specific counter from target urn
            target_urn[target_list == trial_dict["target"]] -= 1
        trials.append(trial_dict)
    if randomize:
        trials = np.random.permutation(trials).tolist()
    return trials


def map_to_integers(general_map, sep='-'):
    ''' takes map and generates a list of corresponding integers'''
    categories = general_map.split(sep=sep)
    categories_int = []
    for i in range(len(categories)):
        categories_int.append(ord(categories[i]) - 65)
    return categories_int


def correct_cue_trial_resp(general_map, resp_options, sep='-'):
    ''' takes map and an ordered list of response options
    and generates a list of integers corresponding to the position of the map
    argument positions in the resp_options'''
    categories = general_map.split(sep=sep)
    correct_resp = []
    for cat in categories:
        correct_resp.append(np.where(resp_options == cat)[0][0])
    return correct_resp


def gen_cue_trials(map_list, stimuli,
                   display_size=6, sep='-'):
    ''' takes a list of maps and generates a datafreame (map, target, correct response)'''
    trials = []
    num_trials = len(map_list)
    for i in range(num_trials):
        general_map = [map_list[i]]
        resp_options = np.random.permutation(stimuli)
        correct_resp = correct_cue_trial_resp(
            general_map[0], resp_options, sep=sep)
        trial_dict = {"trial_type": "cue_memory",
                      "map": general_map,
                      "resp_options": resp_options,
                      "correct_resp": correct_resp}
        trials.append(trial_dict)
    return trials


def compile_down(general_map, map_type=None, display=None, sep='-'):
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
            compiled_map = f"{general_map[0][0]}{sep}{general_map[1][2]}"
    return compiled_map


def insert_with_different_neighbors(thisList, element):
    # easiest cases: first or last element
    if thisList[0] != element:
        thisList.insert(0, element)
        return True
    n = len(thisList)
    if thisList[-1] != element:
        thisList.append(element)
        return True
    # hard case: somewhere in the middle
    for i in range(1, n+1):
        if thisList[i] != element and thisList[i-1] != element:
            thisList.insert(i, element)
            return True
    return False


def get_map_list(selection, n_repeats=1, allow_repeats=False, inary_maps=False):
    ''' generate a list of n_repeats * selections such that no two selections are immediately adjacent '''
    if inary_maps:
        selection = inery2prim(selection)
    goal_length = len(selection) * n_repeats
    tile = np.random.permutation(
        np.repeat(selection, n_repeats, axis=0)).tolist()
    if allow_repeats:
        out = tile
    else:
        out = [e for i, e in enumerate(
            tile) if i == 0 or (i > 0 and tile[i-1] != e)]
        repeated_selections = [e for i, e in enumerate(
            tile) if i > 0 and tile[i-1] == e]
        while len(out) < goal_length:
            s = repeated_selections.pop()
            succesful = insert_with_different_neighbors(out, s)
            if not succesful:
                repeated_selections.append(s)
    if inary_maps:
        return prim2inary(out)
    return out


def inery2prim(inery_list, sep_2='+'):
    prims = []
    for inary in inery_list:
        prims.append(sep_2.join(inary))
    return np.array(prims)


def prim2inary(prim_list, len_inary=2, sep_2='+'):
    inaries = []
    for prims in prim_list:
        inaries.append([prims.split(sep_2, 1)[j] for j in range(len_inary)])
    return np.array(inaries)


# ============================================================================
# Selection of maps
print("Generating map selections...")
# Generate all transmuters and compose binary maps from a selection thereof
unique_prim = cartesian_product(stimuli, discard_reps=True,
                                strcat=True, sep=sep)
selection_prim, comps_dict_binary = gen_binary_compositions(
    unique_prim,
    n_primitives=n_primitives,
    min_type=min_type,
    sd_max=0.5,
    sep=sep)
    
# Select binary maps such that the first primitive of only one second-only map
# does not appear in other compositions
selection_binary = select_binary_compositions(comps_dict_binary)

# # Generate structural conjugates for the selected binary maps (second draft)
# unique_prim_rest = np.setdiff1d(unique_prim, selection_prim)
# selection_prim_conj, comps_dict_binary_conj = gen_binary_compositions(
#     unique_prim_rest,
#     n_primitives=n_primitives,
#     min_type=min_type,
#     sd_max=0.5,
#     sep=sep)
# selection_binary_conj = select_binary_compositions(comps_dict_binary_conj)
selection_prim = ['A-B', 'B-A', 'C-D']
selection_binary = [['B-A', 'A-B'],
                    ['A-B', 'C-D'],
                    ['C-D', 'B-A']]

print("Primitives:", selection_prim)
print("Binaries:", selection_binary)
    
# Localizer lists
print("Generating localizer lists...")
selection_prim_loc = np.tile(selection_prim, n_exposure_loc_quick)
selection_prim_loc_query = np.tile(selection_prim, n_exposure_loc_catch)
stimuli_loc = np.tile(stimuli, n_exposure_loc_quick)
stimuli_loc_query = np.tile(stimuli, n_exposure_loc_catch)


# ============================================================================
# Generate Blocks
with open(stim_dir + os.sep + "spell_names.csv", newline='') as f:
    reader = csv.reader(f)
    tcue_list = list(reader)[0]
vcue_list = glob.glob(stim_dir + os.sep + "c_*.png")
vcue_list = [Path(fname).stem for fname in vcue_list]  # remove trunk
stim_list = glob.glob(stim_dir + os.sep + "s_*.png")
stim_list = [Path(fname).stem for fname in stim_list]



for i in range(first_participant, first_participant+n_participants):
    print(f"Generating trial lists for participant {i}...")
    
    # ========================================================================
    # 0. Mappings between cues and stimuli
    tcue_list = np.random.permutation(tcue_list)
    vcue_list = np.random.permutation(vcue_list)
    stim_list = np.random.permutation(stim_list)
    fname = f"{trial_list_dir}{os.sep}{str(i).zfill(2)}_mappinglists"
    data = {'tcue': tcue_list, 'vcue': vcue_list, 'stim': stim_list}
    if save_this:
        save_object(data, fname, ending=ending)
    
    
    # ========================================================================
    # 1. Practice blocks
    # 1.1 Cue Memory
    df_list = []
    for _ in range(maxn_repeats):
        cue_list_prim = get_map_list(
            selection_prim,
            n_repeats=n_exposure_practice*2,
            allow_repeats=False,
            )
        trials = gen_cue_trials(cue_list_prim, stimuli)
        df_list.append(trials)
    trials_prim_cue = [item for sublist in df_list for item in sublist]
    fname = f"{trial_list_dir}{os.sep}{str(i).zfill(2)}_trials_prim_cue"
    if save_this:
        save_object(trials_prim_cue, fname, ending=ending)

    # 1.2 Test Practice
    for test_type in ["count", "position"]:
        df_list = []
        for _ in range(maxn_repeats):
            map_list_prim = get_map_list(
                selection_prim,
                n_repeats=n_exposure_practice,
                allow_repeats=False,
                )
            trials = gen_trials(
                stimuli,
                map_list_prim,
                resp_list=resp_list,
                trial_type="test_practice",
                test_type=test_type,
                display_size=display_size,
                sep=sep,
                )
            df_list.append(trials)
        trials_prim_practice_c = [item for sublist in df_list for item in sublist]
        fname = f"{trial_list_dir}{os.sep}{str(i).zfill(2)}_trials_prim_prac_{test_type[0]}"
        if save_this:
            save_object(trials_prim_practice_c, fname, ending=ending)
      
    
    # ========================================================================
    # 2. Generic blocks
    # generate trials twice with n_exposure/2 and each test display type,
    # then randomly permute both generated lists
    spell_types = ["prim", "binary"]
    test_types = ["count", "position"]
    for spell_type in spell_types:
        n_exposure = n_exposure_prim if spell_type == "prim" else n_exposure_binary
        selection = selection_prim if spell_type == "prim" else selection_binary
        df_list = []
        for _ in range(maxn_repeats//2):
            block_list = []
            for test_type in test_types:
                map_list = get_map_list(
                    selection,
                    n_repeats=n_exposure,
                    inary_maps=(spell_type == "binary"),
                    allow_repeats=True,
                    )
                trials = gen_trials(
                    stimuli,
                    map_list,
                    resp_list=resp_list,
                    test_type=test_type,
                    display_size=display_size,
                    sep=sep,
                    )
                block_list.append(trials)
            trials_flat = [item for sublist in block_list for item in sublist]
            df_list.append(np.random.permutation(trials_flat).tolist())
        trials_prim = [item for sublist in df_list for item in sublist]
        fname = f"{trial_list_dir}{os.sep}{str(i).zfill(2)}_trials_{spell_type}"
        if save_this:
            save_object(trials_prim, fname, ending=ending)
    
        
    # ========================================================================
    # 3. Object decoder blocks
    df_list = []
    
    for catch in [False, True]:
        n_exp = n_exposure_loc_catch if catch else n_exposure_loc_quick
    
        for _ in range(n_exp):
            for stim_idx in range(len(stimuli)):
                for pos_idx in range(display_size):
                    trial = gen_trial_dict_object_dec(stimuli, stim_idx, pos_idx, catch=catch)
                    df_list.append(trial)
    
    trials_localizer = np.random.permutation(df_list).tolist()
    fname = f"{trial_list_dir}{os.sep}{str(i).zfill(2)}_trials_obj_dec"
    if save_this:
        save_object(trials_localizer, fname, ending=ending)


    # ========================================================================
    # 4. Spell decoder blocks
    df_list = []
    
    jitter_interval = range(-30, 30)
    n_prim_decoder_trials = int(np.ceil(n_exposure_prim_dec/(display_size * 4)))
    
    for prim in selection_prim:
        for pos in range(display_size):
            for correct_resp in [0, 1, 2, 3]:
                for applicable in [True, False]:
                    if applicable:
                        input, output = prim[0], prim[2]
                    else:
                        stim_tmp = stimuli.copy().tolist()
                        stim_tmp.remove(prim[0])
                        input = np.random.choice(stim_tmp)
                        output = input
                    input_disp = [None] * display_size
                    input_disp[pos] = input
                    output_disp = input_disp.copy()
                    output_disp[pos] = output
                    resp_options = np.random.permutation(stimuli)
                    
                    # if the desired response is not at the correct location
                    # swap the two response options
                    if resp_options[correct_resp] != output:
                        idx = np.where(resp_options == output)[0][0]
                        resp_options[idx] = resp_options[correct_resp]
                        resp_options[correct_resp] = output

                    trial = {'trial_type': 'prim_decoder',
                            'input_disp': np.array(input_disp),
                            'output_disp': np.array(output_disp),
                            'map': [prim],
                            'applicable': applicable,
                            'test_type': 'position',
                            'resp_options': resp_options,
                            'correct_resp': correct_resp,
                            'target': pos,
                            'map_type': 'primitive',
                            'jitter': np.random.choice(
                                jitter_interval, 3, replace=True)/1000
                            }
                    df_list.append(trial)
    trials_prim_decoder = np.random.permutation(df_list).tolist()
    fname = f"{trial_list_dir}{os.sep}{str(i).zfill(2)}_trials_prim_dec"
    if save_this:
        save_object(trials_prim_decoder, fname, ending=ending)
