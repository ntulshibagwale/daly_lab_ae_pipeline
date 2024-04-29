"""
daly_lab_ae_pipeline
mark_time_of_arrival
version: 1.0

Author: Nick Tulshibagwale
Date: October 13, 2023

Summary of code:
    1. User prompted to select ae .json file of filtered waveforms
    2. User loops through all waveforms and selects TOA
    3. Dataset is saved along with TOAs

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

def load_json_file(json_file):
    """ Loads in .json file from file path. """
    print(f"Loading in Dataset from {json_file}")
    with open(json_file) as file:
        data = json.load(file)
    for key in data.keys():
        data[key]  = np.array(data[key])
    print("Successfully loaded in .json file.\n")
    
    return data


def tellme(s): # print statements to user for instructions
    plt.title(s, fontsize=30)
    plt.draw()
    

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]
                 
        
def manual_toa_selection(signals, event, sensor):
    """ User selects TOA on all signals """
    toa=[]
    
    # create toa array of same dimension 
    toa=np.zeros(len(signals))

    for ii, ev in enumerate(list(set(event))): # loop through all events once
        # obtain the indices for that event
        indices = [jj for jj,x in enumerate(event) if x == ev]
                            
        plt.figure(figsize=(10,10))
        ax1 = plt.subplot(211)
        ax1.plot(TIME,signals[indices[0]],'b')
        ax1.set_xlabel('Time ($\mu$s)', fontsize=30)
        ax1.set_ylabel('Amplitude', fontsize=30)
        ax1.tick_params(axis='x', labelsize=30) 
        ax1.tick_params(axis='y', labelsize=30) 
        ax1.set_xlim([0,TIME[400]])
        #ax1.set_ylim([-0.03,0.03])
        minimum = min(signals[indices[0]][0:400])-0.01
        maximum = max(signals[indices[0]][0:400])+0.01
        ax1.set_ylim([minimum,maximum])
        
        ax2 = plt.subplot(212)
        ax2.plot(TIME,signals[indices[1]],'b')
        ax2.set_xlabel('Time ($\mu$s)', fontsize=30)
        ax2.set_ylabel('Amplitude', fontsize=30)
        ax2.tick_params(axis='x', labelsize=30) 
        ax2.tick_params(axis='y', labelsize=30) 
        ax2.set_xlim([0,TIME[400]])
        #ax2.set_ylim([-0.03,0.03])
        minimum = min(signals[indices[1]][0:400])-0.01
        maximum = max(signals[indices[1]][0:400])+0.01
        ax2.set_ylim([minimum,maximum])
        
        plt.tight_layout()
        
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized() 
        
        for index, ax in enumerate([ax1, ax2]):
            plt.sca(ax)  # Set the current axis for ginput
        
            # Compute TOA for the current subplot
            while True:
                pts = []
                while len(pts) < 1:
                    #tellme('Select signal start time with mouse')
                    tellme("")
                    pts = np.asarray(plt.ginput(1, timeout=-1))
        
                # w_start = pts[:, 0][0]
                selected_point = pts[:, 0][0]
                print(f'Selected Point: {selected_point} microseconds')
                w_start = find_nearest(PULSE_TIME,selected_point)
                print(f'Nearest Sampled Point: {w_start} microseconds')
                ph = ax.axvline(w_start, color='b', linestyle='--', label=f'time = {np.round(w_start, 2)} $\mu$s')
                ax.legend(fontsize=34)
                #tellme('Hit spacebar to accept. Left click to repeat selection.')
                tellme("")
                if plt.waitforbuttonpress():
                    break
                ph.remove()

            # if user selected super far to the left
            if w_start < 2:
                toa[indices[index]]=(0) # indicating unknown start value
            else:
                toa[indices[index]]=(w_start)
            print("event : {:>5d}  channel : {:>5d}  toa : {:>5f}".format(ev, index+1, w_start))
            
        plt.close('all')
            
    toa=list(toa)
    
    return toa
    
   
def compute_toa(ae_json_file, method='MANUAL'):
    """ Determine time of arrival for AE waveforms """
    dataset = load_json_file(ae_json_file)
    
    waves=dataset['waves']
    waves = [list(waveform) for waveform in waves]
    event=dataset['event'].tolist()
    time=dataset['time'].tolist()
    parent_txt=dataset['parent_txt'].tolist()
    sensor=dataset['sensor'].tolist()

    if method == 'MANUAL':
        toa=manual_toa_selection(waves, event, sensor)
    
    toa_dataset={'waves': waves,
                 'sensor': sensor,
                 'event': event,
                 'parent_txt': parent_txt,                 
                 'time' : time,
                 'toa': toa}
    
    save_dict_as_json(ae_json_file, toa_dataset, 'toa')
    
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
    METHOD = 'MANUAL'

    # Create a StringIO object to capture the output
    output_buffer = io.StringIO()
    
    # Redirect the standard output to the buffer
    with redirect_stdout(output_buffer):
        # header
        current_datetime = datetime.datetime.now()
        print(current_datetime)
        print('daly_lab_ae_pipeline')
        print('mark_time_of_arrival')
        print(f"version: {VERSION}")
        print("Nick Tulshibagwale")
        print("Daly Lab, Mechanical Eng. Department")
        print("University of California, Santa Barbara")
        print('')
        print('')
        
        print("INPUTS")
        ae_json_file = select_json_file()
        print(f'selected .json file: {ae_json_file}')
        print(f'selected TOA method: {METHOD}')
        print('')
           
        print('TIME-OF-ARRIVAL')
        toa_dataset = compute_toa(ae_json_file, method='MANUAL')
        print('')
        
        
        print('PROGRAM END')
         
    # Output log
    captured_output = output_buffer.getvalue()
    log_name = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    with open(log_name+'_log.txt', 'w') as file:
        file.write(captured_output)
    
   
   
    


    
