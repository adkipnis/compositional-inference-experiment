import pickle
import os
leaf = os.path.join("component-tests", "set-mapping-lists-for-piloting.py")
trunk = os.path.abspath(__file__).replace(leaf, "")
fname = os.path.join(trunk, "trial-lists", "01_mappinglists.pkl")
print("Path to mapping lists:", fname)
m = pickle.load(open(fname, "rb"))
m["stim"] = ['s_heart', 's_shoe', 's_frog', 's_puzzle',
             's_globe', 's_banana', 's_signpost', 's_rocket']
m["tcue"] = ['Virnas', 'Stites', 'Probus',
             'Ramys', 'Locris', 'Tyges']
m["vcue"] = ['c_F', 'c_A', 'c_E',
             'c_D', 'c_B', 'c_C']

with open(fname, "wb") as f:
    pickle.dump(m, f)
    print("Changed mapping lists suffecfully.")