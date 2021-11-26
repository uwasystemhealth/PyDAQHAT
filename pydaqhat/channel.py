class Channel:
    """Class containing channel number, sensitivity (mV/unit) and 
    whether input input is powered (iepe_enable = True)
    
    channel number (int) : 0, 1, ... (number of hats * 2 - 1)
    sensitivity (float): Sensitivity of sensor in mV/unit
    iepe_enable (bool): Enable IEPE if true
"""
    def __init__(self, channel=0, sensitivity=1000, iepe_enable=False):
        self.channel = channel
        self.sensitivity = sensitivity
        self.iepe_enable = iepe_enable
