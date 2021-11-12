"""
    This file contains essential functions to control the PiDAQ system
"""
from __future__ import print_function
from time import sleep
from sys import stdout, version_info
from math import sqrt
from daqhats import mcc172, OptionFlags, SourceType, HatIDs, HatError
from daqhats_utils import select_hat_device, enum_mask_to_string, chan_list_to_mask
from ipywidgets import widgets

scan = False

def finite_scan(channels=[0], iepe_enable=False, sensitivity=1000, sample_rate=20000, recording_length=1):
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
    
    channel_mask = chan_list_to_mask(channels) # Returns equivalent integer representing channels
    channel_count = len(channels)

    total_samples = recording_length*sample_rate
    
    options = OptionFlags.DEFAULT ## Make this a parameter in future
    
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
                Length of Recording: {4} seconds
                Sensitivity: {5} mV/unit
                Option Flags: {6}
                """.format(str(channels), str(iepe_enable), sample_rate, hat.a_in_scan_actual_rate(sample_rate), recording_length, sensitivity, (str(options).split('.'))[1]))
    
    # Start scan
    hat.a_in_scan_start(channel_mask, total_samples, options)
    
    print("Starting scan...")
    
    data = hat.a_in_scan_read(total_samples, -1)
    print("Recording finished with {} samples".format(len(data.data)))
    
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
        