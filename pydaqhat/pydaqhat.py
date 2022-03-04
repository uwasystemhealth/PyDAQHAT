"""
    This file contains essential functions to control the PiDAQ system
"""
from __future__ import print_function
from time import sleep
from sys import stdout, version_info
from math import sqrt
from daqhats import (mcc172, hat_list, OptionFlags, SourceType, HatIDs, 
                     HatError)
from .daqhats_utils import (select_hat_device, enum_mask_to_string,
                           chan_list_to_mask)
from ipywidgets import widgets
from collections import namedtuple

from .channel import Channel

scan = False

def finite_scan(
    channels=[Channel(0,"Channel 0",3000,False),
              Channel(1,"Channel 1",1234,True),
              Channel(2,"Channel 2",4321,False),
              Channel(3,"Custom name",3000,False),
              Channel(4,"Channel 4",3000,False),
              Channel(5,"Channel 5",3000,False)],
    sample_rate=24000,
    recording_length=1,
    verbose=False,
):
    """ This runs a scan of predetermined length on the PiDAQ
    Args:
        channels (list): List of class Channel containing channels to use
        sample_rate (float): Number of samples per second
        recording_length (float): Length of recording in seconds 
        verbose (bool): Verbose output
        
    Returns:
        ScanResult (namedtuple): Returns a named tuple containing the following
        information: 
        ( 
        inputs: array containing function inputs (channels, sample rate, recording length)
        channels: input channels converted to a channel mask array
        data: output data from scan. data[3] corresponds to channel 3 etc.
        )
    """
    
    MASTER = 0 # Master hat is the index 0 hat
    MAX_DEVICE_COUNT = 3 # Maximum number of hats on device
    CHANNELS_PER_HAT = 2
        
    timeout = 5.  # Seconds
    options = OptionFlags.DEFAULT
    channel_mask = [None] * MAX_DEVICE_COUNT
    channel_count = [0] * MAX_DEVICE_COUNT
    
    ## Parse channels into correct format
    chans = format_channels(channels, 
                            MAX_DEVICE_COUNT, 
                            CHANNELS_PER_HAT)
    if verbose:
        print(f"Channels: {chans}")
    
    # Get descriptors for all of the available HAT devices.
    hat_info = hat_list(filter_by_id=HatIDs.MCC_172)
    hats = [mcc172(x.address) for x in hat_info]
    number_of_hats = len(hats)
    
    if verbose:
        print("Hats:\n",hat_info)
        print(f"Number of hats : {number_of_hats}")
        
    for i, hat in enumerate(hats):
        for j, chan in enumerate(chans[i]):
            if (chan != None):
                # Configure IEPE.
                hat.iepe_config_write(
                    chan, 
                    channels[int(i*CHANNELS_PER_HAT + j)].iepe_enable)
                # Configure sensitivity
                hat.a_in_sensitivity_write(
                    chan, 
                    channels[int(i*CHANNELS_PER_HAT + j)].sensitivity)
        if hat.address() != MASTER:
            # Configure the slave clocks.
            hat.a_in_clock_config_write(SourceType.SLAVE, sample_rate)

    # Configure the master clock and start the sync.
    hat = hats[MASTER]
    hat.a_in_clock_config_write(SourceType.MASTER, sample_rate)
    synced = False
    while not synced:
        (_source_type, actual_rate, synced) = \
            hat.a_in_clock_config_read()
        if not synced:
            sleep(0.005)
    if verbose:
        print("Hats are now synced")

    for n, hat in enumerate(hats):
        if(chans[n] != [None]):
            channel_mask[n] = chan_list_to_mask(chans[n])
            channel_count[n] = len(chans[n])
        sr = hat.a_in_scan_actual_rate(sample_rate)
        total_samples = int(recording_length*sr)
        if verbose:
            print(f"""
-----------------------------
Hat {n}
-----------------------------
    Channels                : {chans[n]}
    Channel mask            : {channel_mask[n]}
    Number of channels used : {channel_count[n]}
    Actual sample rate      : {sr}
    Total number of samples : {total_samples}
-----------------------------""")
            for i, chan in enumerate(chans[n]):
                if chan != None:
                        print(f"""
    Channel {chan}            
        Sensitivity         : {hat.a_in_sensitivity_read(chan)}
        IEPE Enable         : {bool(hat.iepe_config_read(chan))}
-----------------------------""")

    if verbose:
        print("Preparing each hat to record")
    data = [None] * MAX_DEVICE_COUNT * CHANNELS_PER_HAT
    # Read the data from each HAT device.
    for i, hat in enumerate(hats):
        if(channel_mask[i] != None):
            print(f"Hat {i} has started recording")
            hat.a_in_scan_start(channel_mask[i], total_samples, options)
        
    for i, hat in enumerate(hats):
        if(channel_mask[i] != None):
            #Run through chans[i] and split based on that
            raw_data = hat.a_in_scan_read_numpy(total_samples, -1).data
            if(len(chans[i]) == 2):
                if verbose:
                    print("Splitting on 2")
                data[i*2] = raw_data[0::2]
                data[i*2 + 1] = raw_data[1::2]
            elif(len(chans[i]) == 1):
                data[i*2] = raw_data
            else:
                 print("List of channels is formatted incorrectly")
                    
    print("Recording has finished")
    
    for i, hat in enumerate(hats):
        hat.a_in_scan_cleanup()
        
        
    ScanResult = namedtuple("ScanResult", "inputs channels data")
    output = ScanResult([sample_rate, recording_length, channels], chans, data)
    
    return output


### Static functions ### 
def get_hat():
    address = select_hat_device(HatIDs.MCC_172)
    hat = mcc172(address)
    return hat

def format_channels(channels, maxdevices=4, numperhat=2):
    """
    This function converts a list of channels to be used (e.g. [0,1,3])
    into a list of lists [[0,1], [1], [None], [None]]
    
    Args:
        channels (list): List containing channels to use
        maxdevices (int): Maximum number of hats on device
        numperhat (int): Total number of channels per hat
    Returns:
        chans (list): List of lists describing channels in correct format
    """
    chans = []
    
    for i in range(maxdevices):
        chans.append([None])
        
    for i in channels:
        if(i.channel % 2 == 0):
            ind = i.channel//numperhat
            chans[ind].append(0)
            if(chans[ind].count(None) > 0):
                chans[ind].remove(None)
        else:
            ind = (i.channel-1)//numperhat
            chans[ind].append(1)
            if(chans[ind].count(None) > 0):
                chans[ind].remove(None)

    return chans

def channels_to_string():
    """
    Turns input list of channels into a readable string
    
    Args:
        channels (list): List of Channel objects
    Returns:
        (string): String in the format "0,1,2,3,4,5"""
