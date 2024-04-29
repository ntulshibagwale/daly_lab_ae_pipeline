"""
daly_lab_ae_pipeline
filter_ae
version: 1.0

Author: Nick Tulshibagwale
Date: March 06, 2024

Summary of code:
    1. User prompted to select ae .txt file, that is obtained from DW testing.
    2. User shown each AE event, choose between filter event or noise event.
    3. Filtered and noisy events are separate into two .json files.
    4. A record of the filtering process is saved in a .txt file.

"""
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from tkinter import filedialog
from tkinter import *
import sys 
import datetime
import io
from contextlib import redirect_stdout

from utils import select_txt_file, flatten, save_dict_as_json_file
  

def load_acquisition(file):
    """ Load .txt file from acquisition test. """
    with open(file) as f:    
        txt_file = f.readlines()
        data_start_idx = 0
        for idx, line in enumerate(txt_file):
            if 'Waveform Size' in line:
                waveform_size = int(line.split(':')[1].strip())
            elif 'Ch1' in line and 'Ch2' in line:
                data_start_idx = idx + 1
                break
        data = txt_file[data_start_idx:]
        ch1 = []
        ch2 = []
        for line in data:
            ch1.append(float(line.split()[0]))
            ch2.append(float(line.split()[1]))
        ch1=np.array(ch1)
        ch2=np.array(ch2)
        w1 = []
        w2 = []
        for i in range(0,len(ch1),waveform_size):
            w1.append(ch1[i:i+waveform_size])    
            w2.append(ch2[i:i+waveform_size])
        
    return [w1, w2]

def filter_ae_txt_file(signals, ev, dt, channel_num, num_samples):
    """ loads in ae .txt file and separate events based on visual inspect. """
    noise_ev, noise_idx = [], []
    filter_ev, filter_idx = [], []
    noise_signals = [[] for _ in range(channel_num)]
    filter_signals = [[] for _ in range(channel_num)]
    for ev_idx, event in enumerate(ev):
        # Plot waveforms
        fig, axes = plt.subplots(channel_num, 1, figsize=(15, 10), sharex=True)
        fig.suptitle(f'Event: {ev[ev_idx]}', fontsize=20)    
        for ch_idx, ax in enumerate(axes): 
            ax.plot(np.arange(0, num_samples) * dt, signals[ch_idx][ev_idx])
            ax.set_title(f'Channel {ch_idx+1}')
            ax.tick_params(labelsize=14)
            #ax.set_xlim([0.000015,0.000025])
        plt.show()
        #User indicates whether to keep
        inp = input(f"To DISCARD event #{ev[ev_idx]} press 'n/N' | "+
                    f"To KEEP event #{ev[ev_idx]} press any key | \n")
        if inp.lower() == 'n' or inp.lower() == 'N':
            noise_ev.append(event)
            noise_idx.append(ev_idx)
            for ch_idx,_ in enumerate(signals): # signals is [channel][events]
                noise_signals[ch_idx].append(signals[ch_idx][ev_idx])
            print("event : {:>5d}  NOISE".format(event))
        else:
            filter_ev.append(event)
            filter_idx.append(ev_idx)
            for ch_idx,_ in enumerate(signals):
                filter_signals[ch_idx].append(signals[ch_idx][ev_idx])
        print("event : {:>5d}  FILTER".format(event))
    print('filtering completed.')
    print("num noise events : {:>5d}".format(len(noise_ev)))
    print("num filter events : {:>5d}".format(len(filter_ev)))
    print(f'noise events: {", ".join(map(str, noise_ev))}')
    print(f'filter events: {", ".join(map(str, filter_ev))}')
    
    return noise_ev, filter_ev, noise_signals, filter_signals


def create_dataset(ae_file, ev, signals):
    """ separate multi-channel signals into one array, put into dict """
    waves, event, sensor = [], [], []    
    # Append waves with corresponding event number and sensor channel
    for channel_idx, channel in enumerate(signals):
        waves.append(channel)
        event.append([int(item) for item in ev])
        sensor.append([(channel_idx+1) for i in range(len(ev))])
    # Remove a dimension 
    waves = flatten(waves)
    event = flatten(event)
    sensor = flatten(sensor)
    waves = [list(waveform) for waveform in waves] # np array not .json compat.
    parent_txt = [ae_file for _ in range(len(waves))]
    # Create dataset in appropriate folder
    dataset = {'parent_txt' : parent_txt,
               'waves' : waves,
               'event' : event, 
               'sensor': sensor}
    
    return dataset

          
if __name__ == '__main__':
    
    VERSION='1.0'
    METHOD = 'MANUAL'
    TIME_FILE = None #True

    # Create a StringIO object to capture the output
    output_buffer = io.StringIO()
    
    # Redirect the standard output to the buffer
    with redirect_stdout(output_buffer):
        # header
        current_datetime = datetime.datetime.now()
        print(current_datetime)
        print('daly_lab_ae_pipeline')
        print('filter_labview_ae')
        print(f"version: {VERSION}")
        print("Nick Tulshibagwale")
        print("Daly Lab, Mechanical Eng. Department")
        print("University of California, Santa Barbara")
        print('')
        print('')
        
        print("INPUTS")
        ae_file = select_txt_file()
        x_div = 10e-6 # 50 microseconds / div [s] # CHANGE
        total_time = x_div * 10 # 10 divisions
        num_samples = 50000
        dt = total_time / num_samples
        duration = num_samples*dt*10**6 # convert to us|
        pulse_time = np.linspace(0,duration,num_samples) # discretization
        channel_num = 2
        
        #ae_file=r'C:\Users\nt\Desktop\in_situ_xct\230905_xctd\raw_data\ae\02_txt_files\02_loading.txt'
        print(f'selected ae .txt file: {ae_file}')

        print('')
           
        print("LOAD IN LABVIEW .TXT FILE")
        signals=load_acquisition(ae_file)
        ev=np.arange(len(signals[0]))
        
        print('ae file loaded succesfully.')
        print("num channels  : {:>5d}".format(len(signals)))
        print("num signals   : {:>5d}".format(len(signals[0])))


        print('FILTERING')
        print(f'Filtering method: {METHOD}')
        dataset_name = ae_file.replace('.txt', '')
        if METHOD == 'MANUAL':
            noise_ev, filter_ev, noise_signals, filter_signals, \
                 = filter_ae_txt_file(signals, ev, dt, channel_num, num_samples)
                    
            print('OUTPUT')
            # separate signals into noise and filtered files
            save_dict_as_json_file(create_dataset(ae_file, noise_ev,
                                                  noise_signals), 
                                                  dataset_name+'_noise')
            save_dict_as_json_file(create_dataset(ae_file, filter_ev, 
                                                  filter_signals),
                                                  dataset_name+'_filter')
            print('noise and filter data saved succesfully into .json.')
        elif METHOD == 'NOFILTER':
            print('All signals processed into .json file.')
            print("num events : {:>5d}".format(len(ev)))   
            print('OUTPUT')
            save_dict_as_json_file(create_dataset(ae_file, ev, signals), 
                                   dataset_name)
            print('AE data saved succesfully into .json.')
        print('')               
        print('PROGRAM END')
         
    # Output log
    captured_output = output_buffer.getvalue()
    log_name = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    with open(log_name+'_log.txt', 'w') as file:
        file.write(captured_output)
    
