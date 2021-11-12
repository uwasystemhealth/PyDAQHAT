# PyDAQHAT : Python module to communicate with a MCC 172 DAQ HAT

This python module allows for the control of the [MCC172 DAQ HAT](https://www.mccdaq.com/DAQ-HAT/MCC-172.aspx) on a [Raspberry Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) (referred to as a "PiDAQ").

This module uses the [daqhats_utils.py](pydaqhat/daqhats_utils.py) which originated from the [MCC172 DAQ HAT examples folder](https://github.com/mccdaq/daqhats/blob/master/examples/python/mcc172/daqhats_utils.py).

## Installation 

```sh
cd
git clone git@github.com:uwasystemhealth/PyDAQHAT.git
cd ~/PyDAQHAT
pip3 install .
cd
```

## Uninstalling



## Getting Started

```python
import pydaqhat
```