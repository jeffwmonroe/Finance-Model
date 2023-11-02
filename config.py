import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
config = os.environ

print('loading environment variables')
print(f'cwd = {Path.cwd()}')

###############################################################################################################
#                         Notebook Directory
# This is a bit of a hack. I would like to keep my Jupyter Notebooks in a separate directory from the top
# level directory. This is purely to keep the project structure neat. This code checks to see if the notebook
# is running from the config['notebook_dir']. If so, this code sets the current working directory to be the
# path without the config['notebook_dir']
if Path.cwd().parts[-1] == config['notebook_dir']:
    print('inside of notebook directory')

    new_wd = Path(*Path.cwd().parts[:-1])
    os.chdir(new_wd)
    print(f'   setting new working directory: {Path.cwd()}')
