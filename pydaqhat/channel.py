class Channel:
    
    def __init__(self, channel, sensitivity, iepe_enable=False):
        self.channel = channel
        self.sensitivity = sensitivity
        self.iepe_enable = iepe_enable
    
        