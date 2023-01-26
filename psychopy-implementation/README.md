# Compositional Inference Experiment

#### Prerequisite: Psychopy
It is possible to install psychopy via conda but that route is less reliable in practice.
Instead we install it via pip in a virtual environment with Python 3.6 to 3.10
1. Set a target directory for a python venv and cd into it.
2. `python -m env psychopy`
3. activate it using `{source path-to-your-dir}/bin/activate` 
4. Download the appropriate build of wxpython and `pip install {path-to-wxpython-installation-file}`
5. `pip install psychopy`
6. Test installation: `psychopy`


#### Running the experiment:
1. Activate the environment and launch `main.py`.