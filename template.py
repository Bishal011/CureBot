import os 
from pathlib import Path 
import logging 

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

list_of_files = [
    "src/__init__.py",
    "src/helper.py",
    "src/prompt.py",
    ".env",
    "setup.py",
    "app.py",
    "research/trials.ipynb",
   " test.py"
]

for filePath in list_of_files:
    filePath = Path(filePath)
    
    filedir, filename = os.path.split(filePath)

    # for  folder
    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory; {filedir} for the file: {filename}")

    # for checking file is present or not
    if (not os.path.exists(filePath)) or (os.path.getsize(filePath) == 0): #size of file
        with open(filePath, "w") as f:
            pass 
            logging.info(f"Creating empty file: {filePath}")
    
    else:
        logging.info(f"{filename} already exists")