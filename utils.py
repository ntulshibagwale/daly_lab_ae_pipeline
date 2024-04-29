"""
daly_lab_ae_pipeline
utils
version: 1.0

Author: Nick Tulshibagwale
Date: March 06, 2024

Utility functions used in other python scripts.

"""
from tkinter import filedialog
from tkinter import Tk
import json
import numpy as np
import matplotlib.pyplot as plt


def select_txt_file(root=None):
    """ User selects a .txt file to load into program, returns entire path. 
            Ex: "C:/Users/nt/Desktop/..../readme.txt" """
    # Create a Tkinter window for file selection
    if root is None:
        root = Tk()
    root.filename = filedialog.askopenfilename(
        title="Select a .txt file", filetypes=(("Text files", "*.txt"),
                                               ("All files", "*.*")))
    txt_file=root.filename
    root.destroy()
    
    return txt_file  


def select_json_file(root):
    """ User selects a .json file to load into program, returns entire path. 
            Ex: "C:/Users/nt/Desktop/..../ae_data.json" """
    # Create a Tkinter window for file selection
    #root = Tk()
    root.filename = filedialog.askopenfilename(
        title="Select a .json file", filetypes=(("Json files", "*.json"),
                                                ("All files", "*.*")))
    json_file=root.filename
    #root.destroy()
    
    return json_file  


def select_json_or_txt_file():
    """User selects a .json or .txt file to load in, returns entire path."""
    # Create a Tkinter window for file selection
    root = Tk()
    root.filename = filedialog.askopenfilename(
        title="Select a .json or .txt file",
        filetypes=(("JSON files", "*.json"), ("Text files", "*.txt"),
                   ("All files", "*.*"))
    )
    selected_file = root.filename
    root.destroy()
    
    return selected_file


def tellme(s):
    """ Print statements to user for instructions """
    plt.title(s, fontsize=30)
    plt.draw()
    
    return
    

def flatten(t): 
    """ flattens out a list of lists, i.e., 2D array to 1D array """
    return [item for sublist in t for item in sublist]


def save_dict_as_json_file(data_as_dict, file_name):
    """ save dictionary as .json file in working directory """
    with open(file_name+'.json', "w") as outfile:
        json.dump(data_as_dict, outfile)
    print("dataset .json saved  : {:>5s}".format(file_name+'.json'))

    return
    

def load_json_file(json_file):
    """ Loads in .json file from file path. """
    print(f"Loading in Dataset from {json_file}")
    with open(json_file) as file:
        data = json.load(file)
    for key in data.keys():
        data[key]  = np.array(data[key])
    print(f"Successfully loaded in {json_file}.\n")
    
    return data