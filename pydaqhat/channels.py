class Channels:
    """Class containing channel number, sensitivity (mV/unit) and 
    whether input input is powered (iepe_enable = True)
    
    channel number (int) : 0, 1, ... (number of hats * 2 - 1)
    sensitivity (float): Sensitivity of sensor in mV/unit
    iepe_enable (bool): Enable IEPE if true
"""
    def __init__(self, *channel_list):
        self.channel_list = channel_list
        self.channel_mask = get_channel_mask(channel_list)
    
    #Static variables
    MAX_DEVICE_COUNT = 4
    CHANNELS_PER_HAT = 2
    
        
    def get_channel_mask(channel_list):
        """
        This function converts a list of channel numbers (e.g. [0,1,3])
        into channels
        """
        chans = get_channel_numbers(channel_list)
    
    def get_channel_numbers(channel_list):
        numbers = []
        
        for channel in channel_list:
            numbers.append(channel.channel)
        
        return numbers
        
        
    