"""
daly_lab_ae_pipeline
load_in_processed_data
version: 1.0

Author: Nick Tulshibagwale
Date: 8/18/26 - Added to code to show example.

Code loads in filtered and processed .json file where ToA and Peak Polarity
has been selected. Waveforms can be paired according to event # and sensor #.

"""
import numpy as np
import matplotlib.pyplot as plt
import json 


def load_json_file(json_file):
    """ Loads in .json file from file path. """
    print(f"Loading in Dataset from {json_file}")
    with open(json_file) as file:
        data = json.load(file)
    for key in data.keys():
        data[key]  = np.array(data[key])
    print("Successfully loaded in .json file.\n")
    
    return data

          
if __name__ == '__main__':
    
    SIG_LEN = 1024
    DT = 10**-7
    DURATION = SIG_LEN*DT*10**6 # convert to us
    TIME = np.linspace(0,DURATION,SIG_LEN) # discretization of signal time
    VERSION='1.0'
       
    ae_json_file = r'3_filtered_AE_toa_peak_polarity\acoustic_data_2_channel_filter_toa_peak_polarity.json'
    dataset = load_json_file(ae_json_file)
    waves=dataset['waves']
    waves = [list(waveform) for waveform in waves]
    event=dataset['event'].tolist()
    parent_txt=dataset['parent_txt'].tolist()
    sensor=dataset['sensor'].tolist()
    toa=dataset['toa'].tolist()
    peak_polarity=dataset['peak_polarity'].tolist()
    
    plt.scatter(event,toa)
    plt.xlabel("Event #")
    plt.ylabel("Time of Arrival")
    plt.show()
    
    # ... Processing of Data
    # Note the list is flattened, use the event # and the sensor # to 
    # determine the pairs of waveforms...
    
    
   
   
    


    
