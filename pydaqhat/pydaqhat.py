"""
    This file contains essential functions to control the PiDAQ system
"""
from __future__ import print_function
from time import sleep
from sys import stdout, version_info
from math import sqrt
from daqhats import (mcc172, hat_list, OptionFlags, SourceType, HatIDs, 
                     HatError)
from daqhats_utils import (select_hat_device, enum_mask_to_string,
                           chan_list_to_mask)
from ipywidgets import widgets
from channel import Channel

scan = False

def finite_scan(
    channels=[Channel(0,3000,False),
              Channel(1,1234,True),
              Channel(2,4321,False)],
    sample_rate=24000,
    recording_length=1,
    verbose=False,
):
    """ This runs a scan of predetermined length on the PiDAQ
    Args:
        channels (list): List containing channels to use
        iepe_enable (bool): Enable IEPE if true
        sensitivity (float): Sensitivity of sensor in mV/unit
        sample_rate (float): Number of samples per second
        recording_length (float): Length of recording in seconds 
        
    Returns:
        hat (any): Returns the MCC172 hat object
    """
    
    MASTER = 0
    MAX_DEVICE_COUNT = 4
    CHANNELS_PER_HAT = 2
    timeout = 5.  # Seconds
    options = OptionFlags.DEFAULT
    channel_mask = [None] * MAX_DEVICE_COUNT
    channel_count = [0] * MAX_DEVICE_COUNT
    
    ## Parse channels into correct format
    chans = chanlist_to_listlist(channels, 
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
        ## TODO Allow for multi-channel configurationyy
        for j, chan in enumerate(chans[i]):
            if (chan != None):
                # Configure IEPE.
                hat.iepe_config_write(chan, channels[int(i*CHANNELS_PER_HAT + j)].iepe_enable)
                # Configure sensitivity
                hat.a_in_sensitivity_write(chan, channels[int(i*CHANNELS_PER_HAT + j)].sensitivity)
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
            print("-----------------------------")
            print(f"Hat {n}")
            print("-----------------------------")
            print(f"    Channels                : {chans[n]}")
            print(f"    Channel mask            : {channel_mask[n]}")
            print(f"    Number of channels used : {channel_count[n]}")
            print(f"    Actual sample rate      : {sr}")
            print(f"    Total number of samples : {total_samples}")
            print("-----------------------------")
            for i, chan in enumerate(chans[n]):
                if chan != None:
                        print(f"    Channel {chan}")
                        print(f"        Sensitivity         : {hat.a_in_sensitivity_read(chan)}")
                        print(f"        IEPE Enable         : {bool(hat.iepe_config_read(chan))}")
            print("-----------------------------")
            print("")
 
        
    data = [None] * MAX_DEVICE_COUNT
    # Read the data from each HAT device.
    for i, hat in enumerate(hats):
        if(channel_mask[i] != None):
            hat.a_in_scan_start(channel_mask[i], total_samples, options)
        
    for i, hat in enumerate(hats):
        if(channel_mask[i] != None):
            data[i] = hat.a_in_scan_read_numpy(total_samples, -1)
        
    for i, hat in enumerate(hats):
        hat.a_in_scan_cleanup()
    
    return data


## TODO convert parameters to a named tuple
def continous_scan_start(channels=[0], iepe_enable=False, sensitivity=1000, sample_rate=20000, buffer_size=10000):
    """ This runs a continous scan on the PiDAQ 
    Args:
        channels (list): List containing channels to use
        iepe_enable (bool): Enable IEPE if true
        sensitivity (float): Sensitivity of sensor in mV/unit
        sample_rate (float): Number of samples per second
        buffer_size (float): Number of samples to keep in buffer

    Returns:
        hat (any): Returns MCC172 hat object
    """
    global hat 
    
    channel_mask = chan_list_to_mask(channels) # Returns equivalent integer representing channels
    channel_count = len(channels)
    
    options = OptionFlags.CONTINUOUS
    
    # Finds address of MCC172 and allocates it as hat
    # TODO allow this to work for multiple boards (hat[])
    address = select_hat_device(HatIDs.MCC_172)
    hat = mcc172(address)
    
    print("Found a board at address: " + str(address))
    
    # Set channel specific parameters
    ## TODO Allow for multi-chanel configuration (different sensitivities)
    for channel in channels:
        hat.iepe_config_write(channel, iepe_enable)
        hat.a_in_sensitivity_write(channel, sensitivity)
    
    #Set clock rate
    ## TODO This must be change to master/slave for multi-board config
    hat.a_in_clock_config_write(SourceType.LOCAL, sample_rate)
    
    # Wait for clocks to sync
    clock_sync = False
    while clock_sync == False:
        clock_sync = hat.a_in_clock_config_read().synchronized
        sleep(0.01)
        
    ## TODO Change to requested parameters and actual parameters for all (using config_read method)
    print("""Recording will start with parameters
                Channels: {0}
                IEPE: {1}
                Requested Scan Rate: {2} Hz
                Actual Scan Rate: {3:.3f} Hz
                Samples Per Channel: {4}
                Sensitivity: {5} mV/unit
                Option Flags: {6}
                """.format(str(channels), str(iepe_enable), sample_rate, hat.a_in_scan_actual_rate(sample_rate), buffer_size, sensitivity, (str(options).split('.'))[1]))
    
    # Start scan
    hat.a_in_scan_start(channel_mask, buffer_size, options)
    
    print("Starting scan...")
    
    sleep(0.1)

    return hat

def continously_write_csv(hat, filename):
    global scan
    
    logfile = open(filename, "w")
    logfile.write("Value\n")
    
    while scan:
        data = hat.a_in_scan_read(1,0).data
        for i in range(0,len(data)):
            logfile.write("{0:.6f}\n".format(data[i]))
        
        sleep(0.01)
    print("Exited loop")
    
    return 1
    
def stop_scan(hat):
    """ Stops scan for given hat """ 
    hat.a_in_scan_stop()
    hat.a_in_scan_cleanup()
        
    print("Scan has stopped")
                
def button_update(x):
    global scan
    if (scan == False):
        scan = True
        continous_scan_start([0],False,1000,20480,300)
    elif (scan == True):
        scan = False
        
        stop_scan()
        
def get_hat():
    address = select_hat_device(HatIDs.MCC_172)
    hat = mcc172(address)
    return hat

def chanlist_to_listlist(channels, maxdevices=6, numperhat=2):
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
