#!/sbin/python3

from evdev import InputDevice, list_devices
from os import remove
from time import sleep

def remove_phantoms():
    while True:
        # Grab all input devices.
        devices_orig = [InputDevice(path) for path in list_devices()]
        for device in devices_orig:
            # Delete any input devices with no physical address.
            if device.phys == "" or device.phys == None:
                remove(device.path)
                print("Removed ", device.path)
        sleep(1)

# Look for phantom controllers and delete them.
remove_phantoms()
