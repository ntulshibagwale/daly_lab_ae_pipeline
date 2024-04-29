"""
daly_lab_ae_pipeline
filter_ae_energy
version: 1.0

Author: Nick Tulshibagwale
Date: February 26, 2024

Filter AE according to energy magnitude.

"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path  
import pandas as pd
import os
import sys
from tkinter import filedialog
from tkinter import *
import numpy as np
import os
import json 
import io
from contextlib import redirect_stdout
import datetime

# Boiler plate code to import waves module
waves_dir = r'G:\My Drive\phd\projects\waves'
print(f"Waves module stored at: {waves_dir}")
if sys.path[0] != os.path.dirname(waves_dir):
    sys.path.insert(0, os.path.dirname(waves_dir))
print(f"Directory added to path: {os.path.dirname(waves_dir)}")
print("Waves modules can be imported.")  

from waves.signal_processing import calc_signal_energy


def load_json_file(json_file):
    """ Loads in .json file from file path. """
    print(f"Loading in Dataset from {json_file}")
    with open(json_file) as file:
        data = json.load(file)
    for key in data.keys():
        data[key]  = np.array(data[key])
    print("Successfully loaded in .json file.\n")
    
    return data
    
   
def filter_ae_energy(ae_json_file, filter_sensor='avg', energy_threshold=-1.0):
    """ Remove low energy events """
    dataset = load_json_file(ae_json_file)
    waves=dataset['waves']
    waves = [list(waveform) for waveform in waves]
    event=dataset['event'].tolist()
    time=dataset['time'].tolist()
    parent_txt=dataset['parent_txt'].tolist()
    sensor=dataset['sensor'].tolist()
    waves_filtered=[]
    event_filtered=[]
    time_filtered=[]
    sensor_filtered=[]
    for zz, ev in enumerate(event): 
        # Find the other sensor indices
        indices = [jj for jj,x in enumerate(event) if x == ev]
        ch1_idx = indices[0]
        ch2_idx = indices[1]
        ch1w = waves[ch1_idx]
        ch2w = waves[ch2_idx]
        ch1e = calc_signal_energy(ch1w)
        ch2e = calc_signal_energy(ch2w)
        avg_e = (ch1e+ch2e)/2
        # If the energy of filter_sensor is sufficient, add data
        
        if filter_sensor == 'avg':
            if np.log10(avg_e) > energy_threshold: 
                waves_filtered.append(waves[zz])
                event_filtered.append(event[zz])
                time_filtered.append(time[zz])
                sensor_filtered.append(sensor[zz])

    
    filtered_dataset={'waves': waves_filtered,
                 'sensor': sensor_filtered,
                 'event': event_filtered,
                 'time': time_filtered,
                 'parent_txt': parent_txt}
    
    save_dict_as_json(ae_json_file, filtered_dataset, f'energy_filter_{energy_threshold}')
    
    return


def select_json_file():
    """ User selects a .json file to load in """
    # Create a Tkinter window for file selection
    root = Tk()
    root.filename = filedialog.askopenfilename(
        title="Select a .json file", filetypes=(("Json files", "*.json"),
                                               ("All files", "*.*")))
    json_file=root.filename
    root.destroy()
        
    return json_file  
          

def save_dict_as_json(ae_json_file, dataset, label):
    """ save dictionary as .json file """
    dataset_name = ae_json_file.replace('.json', '_' + label + '.json')
    with open(dataset_name, "w") as outfile:
        json.dump(dataset, outfile)
    print("dataset .json saved  : {:>5s}".format(dataset_name))

    return


if __name__ == '__main__':
    
    SIG_LEN = 1024
    DT = 10**-7
    DURATION = SIG_LEN*DT*10**6 # convert to us
    TIME = np.linspace(0,DURATION,SIG_LEN) # discretization of signal time
    VERSION='1.0'
    filter_sensor='avg'
    energy_threshold=1.0

    # Create a StringIO object to capture the output
    output_buffer = io.StringIO()
    
    # Redirect the standard output to the buffer
    with redirect_stdout(output_buffer):
        # header
        current_datetime = datetime.datetime.now()
        print(current_datetime)
        print('daly_lab_ae_pipeline')
        print('filter_ae_energy')
        print(f"version: {VERSION}")
        print("Nick Tulshibagwale")
        print("Daly Lab, Mechanical Eng. Department")
        print("University of California, Santa Barbara")
        print('')
        print('')
        
        print("INPUTS")
        ae_json_file = select_json_file()
        print(f'selected .json file: {ae_json_file}')
        print(f'selected filter_sensor: {filter_sensor}')
        print(f'selected energy_threshold: {energy_threshold}')
        print('')
           
        print('FILTERING')
        filtered_energy_dataset = filter_ae_energy(ae_json_file,
                                                   filter_sensor,
                                                   energy_threshold)
        print('')
        
        
        print('PROGRAM END')
         
    # Output log
    captured_output = output_buffer.getvalue()
    log_name = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    with open(log_name+'_log.txt', 'w') as file:
        file.write(captured_output)
    
   
   
    


    
