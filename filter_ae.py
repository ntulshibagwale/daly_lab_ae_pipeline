"""
daly_lab_ae_pipeline
filter_ae
version: 1.0

Author: Nick Tulshibagwale
Date: October 13, 2023

Summary of code:
    1. User prompted to select ae .txt file, that is obtained from DW testing.
    2. User shown each AE event, choose between filter event or noise event.
    3. Filtered and noisy events are separate into two .json files.
    4. A record of the filtering process is saved in a .txt file.

"""
import numpy as np
import matplotlib.pyplot as plt
import json
from tkinter import filedialog
from tkinter import Tk
import datetime
import io
from contextlib import redirect_stdout


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


def save_dict_as_json(ae_file, dataset, label):
    """ save dictionary as .json file """
    dataset_name = ae_file.replace('.txt', '_' + label + '.json')
    with open(dataset_name, "w") as outfile:
        json.dump(dataset, outfile)
    print("dataset .json saved  : {:>5s}".format(dataset_name))

    return
    

def filter_ae_txt_file(ae_file, method='MANUAL'):
    """ loads in ae .txt file and separate events into noise and filtered """
    signals, ev, fs, channel_num, sig_length = read_ae_file(ae_file)
    print('ae file loaded succesfully.')
    print("num channels  : {:>5d}".format(len(signals)))
    print("num signals   : {:>5d}".format(len(ev)))
    print("sampling freq : {:>5d}".format(fs))
    print("signal length : {:>5d}".format(sig_length))
    print(f'begin {method} filtering...')
    if method == 'MANUAL': # Filter via visual inspection
        noise_ev, noise_idx, filter_ev, filter_idx,\
            noise_signals, filter_signals = manual_filtering(signals, ev, fs,
                                                       channel_num, sig_length)
    
    print('filtering completed.')
    print("num noise events : {:>5d}".format(len(noise_ev)))
    print("num filter events : {:>5d}".format(len(filter_ev)))
    print(f'noise events: {", ".join(map(str, noise_ev))}')
    print(f'filter events: {", ".join(map(str, filter_ev))}')

    # separate signals into noise and filtered dictionaries
    noise_dataset = create_dataset(ae_file, noise_ev, noise_signals)
    filter_dataset = create_dataset(ae_file, filter_ev, filter_signals)
        
    return noise_dataset, filter_dataset


def manual_filtering(signals, ev, fs, channel_num, sig_length):
    """ Split events into noise and actual events by visual inspection """
    noise_ev, noise_idx, filter_ev, filter_idx = [], [], [], []
    noise_signals = [[] for _ in range(channel_num)]
    filter_signals = [[] for _ in range(channel_num)]
    for ev_idx, event in enumerate(ev):
        # Plot waveforms
        fig, axes = plt.subplots(channel_num, 1, figsize=(15, 10), sharex=True)
        fig.suptitle(f'Event: {ev[ev_idx]}', fontsize=20)    
        for ch_idx, ax in enumerate(axes): 
            ax.plot(np.arange(0, sig_length) * 1/fs, signals[ch_idx][ev_idx])
            ax.set_title(f'Channel {ch_idx+1}')
            ax.tick_params(labelsize=14)
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

       
    return noise_ev, noise_idx, filter_ev, filter_idx, noise_signals, \
            filter_signals


def flatten(t): # flattens out a list of lists (CHECK)
    return [item for sublist in t for item in sublist]

def read_ae_file(ae_file):
    """ function loads in experimental AE data from .txt files from DW """
    # Read in .txt file generated from Digital Wave DAQ / Software
    f = open(ae_file)
    data = f.readlines()
    f.close()
    
    # Get the signal processing parameters from header
    header = data[0]
    fs = int(header.split()[0]) * 10**6  # DAQ sampling freq (usually 10 MHz)
    sig_length = int(header.split()[2])  # Number of samples in waveform event
    channel_num = int(header.split()[3]) # Number of AE sensors used
    
    # Read in waveform data and turn into list of sensors pointing to AE hits
    lines = data[1:]
    signals = [] 
    
    # Loop through the columns taken from .txt file (waves from each sensor)
    for channel in range(0,channel_num):
        # Get data from the sensor's respective column
        v = np.array([float(line.split()[channel]) for line in lines])
        # Turn the long appended column into separate AE hits using sample num
        z = []
        for i in range(0,len(v),sig_length):
            z.append(v[i:i+sig_length])    
        signals.append(z)
    
    # Create array of corresponding event numbers 
    ev = np.arange(len(signals[0]))+1 # all sensors have same number of events

    return signals, ev, fs, channel_num, sig_length


def select_txt_file():
    """ User selects a .txt file to load in """
    # Create a Tkinter window for file selection
    root = Tk()
    root.filename = filedialog.askopenfilename(
        title="Select a .txt file", filetypes=(("Text files", "*.txt"),
                                               ("All files", "*.*")))
    txt_file=root.filename
    root.destroy()
    
    return txt_file  
          
if __name__ == '__main__':
    
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
        print('filter_ae')
        print(f"version: {VERSION}")
        print("Nick Tulshibagwale")
        print("Daly Lab, Mechanical Eng. Department")
        print("University of California, Santa Barbara")
        print('')
        print('')
        
        print("INPUTS")
        ae_file = select_txt_file()
        #ae_file=r'C:\Users\nt\Desktop\in_situ_xct\230905_xctd\raw_data\ae\02_txt_files\02_loading.txt'
        print(f'selected .txt file: {ae_file}')
        print(f'selected filter method: {METHOD}')
        print('')
           
        print('FILTERING')
        noise_dataset, filter_dataset = filter_ae_txt_file(ae_file, 
                                                           method='MANUAL')
        print('')
        
        print('OUTPUT')
        save_dict_as_json(ae_file, noise_dataset, 'noise')
        save_dict_as_json(ae_file, filter_dataset, 'filter')
        print('noise and filter data saved succesfully.')
        print('')
        
        print('PROGRAM END')
         
    # Output log
    captured_output = output_buffer.getvalue()
    log_name = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    with open(log_name+'_log.txt', 'w') as file:
        file.write(captured_output)
    
