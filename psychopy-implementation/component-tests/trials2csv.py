import copy, pickle, csv
import numpy as np

def dump(trials, fname, source_of_difference=""):
    if source_of_difference:
        print(f"WARNING: Not all trials have the same {source_of_difference}, pickling instead!")
    with open(fname + ".pkl", "wb") as f:
        pickle.dump(trials, f)
        print(f"Saved {len(trials)} trials to '{fname}.pkl'")


def listofdicts2csv(trials: list, fname: str):
    """ write a list of trialdicts to a csv """
    trials = copy.deepcopy(trials)

    # === data integrity checks ===
    # 1. check if all trials have the same keys, dump otherwise
    unique_keys = trials[0].keys()
    key_check_list = [set(trial.keys()) == set(unique_keys)
                      for trial in trials]
    if not all(key_check_list):
        dump(trials, fname, "keys")
        return
        
    # 2. check if all trials have the same item types per key, dump otherwise
    key_types = {key: type(trials[0][key])
                 for key in unique_keys}
    type_check_list = [type(trial[key]) == key_types[key]
                       for trial in trials for key in unique_keys]
    if not all(type_check_list):
        dump(trials, fname, "key types")
        return
    
    # === data transformations ===
    # spread out lists and sets to new enumerated keys
    original_keys = list(unique_keys)
    list_keys = [key for key in original_keys
                 if isinstance(trials[0][key],
                               (set, list, np.ndarray))]
    if list_keys:
        new_keys = []
        for trial in trials:
            for key in list_keys:
                trial_updates = {f"{key}_{i}": item
                                 for i, item in enumerate(trial[key])}
                trial.update(trial_updates)
                new_keys.extend(trial_updates.keys())
                del trial[key]
        
        # update unique_keys (some trials may have more than others) and sort them in original order
        new_keys = sorted(set(new_keys))
        unique_keys = np.setdiff1d(original_keys, list_keys)
        unique_keys = np.union1d(unique_keys, new_keys)
        unique_keys = sorted(unique_keys, key=lambda x: original_keys.index(x.split('_')[0]))
 
    # === write to csv ===
    with open(fname + ".csv", "w", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file, unique_keys)
        dict_writer.writeheader()
        dict_writer.writerows(trials)
        print(f"Saved {len(trials)} trials to '{fname}.csv'")



# --- test ---------------------------------------------------------
def main():
    trial_list = [
        {"trial": 1, "condition": "A", "stimulus": ["B", "C"], "response": ["B"]},
        {"trial": 2, "condition": "A", "stimulus": ["C"], "response": ["B"]},
        {"trial": 3, "condition": "B", "stimulus": ["A", "B", "C"], "response": ["B", "C"]},
    ]
    listofdicts2csv(trial_list, "testDataSet")
    # dump(trial_list, "testDataSet")
    
if __name__ == "__main__":
    main()