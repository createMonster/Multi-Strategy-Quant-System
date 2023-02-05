#this is utility file for perforing simple tasks

#python3 -m pip install pickle

import pickle

def save_file(path, obj):
    try:
        with open(path, "wb") as fp: #write bytes
            pickle.dump(obj, fp)
    except Exception as err:
        #do some error handling
        print(err)

def load_file(path):
    try:
        with open(path, "rb") as fp: #load bytes
            return pickle.load(fp)
    except Exception as err:
        #do some error handling
        print(err)
