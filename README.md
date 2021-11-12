# PyDAQHAT : Python module to communicate with a MCC 172 DAQ HAT

This python module allows for the control of the [MCC172 DAQ HAT](https://www.mccdaq.com/DAQ-HAT/MCC-172.aspx) on a [Raspberry Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) (referred to as a "PiDAQ").

This module uses the [daqhats_utils.py](pydaqhat/daqhats_utils.py) which originated from the [MCC172 DAQ HAT examples folder](https://github.com/mccdaq/daqhats/blob/master/examples/python/mcc172/daqhats_utils.py).

## Requirements

This module requires the installation of the [DAQHATS](https://github.com/mccdaq/daqhats) module.

Please see <https://github.com/mccdaq/daqhats> for details.

### Update the EEPROM images

If you change your board stack, you must update the saved EEPROM images so that
the library has the correct board information. You can use the DAQ HAT Manager or the
command:

```sh
sudo daqhats_read_eeproms
```

## Installation 

```sh
cd
git clone git@github.com:uwasystemhealth/PyDAQHAT.git
cd ~/PyDAQHAT
pip3 install .
cd
```

## Uninstalling

```sh
pip3 uninstall PyDAQHAT -y
```

## Getting Started

```python
import pydaqhat
```