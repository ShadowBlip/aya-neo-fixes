#!/sbin/python3
# Aya Neo Controller
# Copyright 2022 Derek J. Clark <derekjohn dot clark at gmail dot com>
# This will create a virtual UInput device and pull data from the built-in
# controller and "keyboard". Right side buttons are keyboard buttons that
# send macros (i.e. CTRL/ALT/DEL). We capture those events and send button
# presses that Steam understands.

import asyncio
import os
import signal
import sys
import dbus

from evdev import InputDevice, InputEvent, RelEvent, UInput, ecodes as e, categorize, list_devices, AbsInfo
from pathlib import PurePath as p
from shutil import move
from time import sleep
from BMI160_i2c import Driver

# Declare global variables
# Devices
gyro = Driver(0x68)
ui = None
def __init__():
    global ui
    gyro_dev = None
    xb360 = None

    devices_orig = [InputDevice(path) for path in list_devices()]
    for device in devices_orig:
        #if device.name == 'Microsoft X-Box 360 pad' and device.phys == 'usb-0000:03:00.3-4/input0':
        if device.name == 'AT Translated Set 2 keyboard':
            xb360 = InputDevice(device.path)
    
#    ui = UInput.from_device(xb360, name='test-controller', version=0x3)
 #   ui.capabilities().update(i
    caps = {e.EV_REL: [e.REL_X, e.REL_Y, e.REL_Z, e.REL_RX, e.REL_RY, e.REL_RZ]}
    ui = UInput(caps, name="test", version=0x3)
   # caps = ui.capabilities()

# Captures physical device events and translates them to virtual device events.
async def capture_gyro_events(device):
    global ui
    gyro_range = device.getFullScaleGyroRange()
    print(gyro_range)
    while True:
        data = device.getMotion6()
        # fetch all gyro and acclerometer values
        print({'gx': data[0], 'gy': data[1], 'gz': data[2], 'ax': data[3], 'ay': data[4], 'az': data[5]})
        print(device.getTemperature())
        print(device.get_device_id())
        ev0 = RelEvent(InputEvent(0, 0, e.EV_REL, e.REL_RX, data[0]))
        ev1 = RelEvent(InputEvent(0, 0, e.EV_REL, e.REL_RY, data[1]))
        ev2 = RelEvent(InputEvent(0, 0, e.EV_REL, e.REL_RZ, data[2]))
        ev3 = RelEvent(InputEvent(0, 0, e.EV_REL, e.REL_X, data[3]))
        ev4 = RelEvent(InputEvent(0, 0, e.EV_REL, e.REL_Y, data[4]))
        ev5 = RelEvent(InputEvent(0, 0, e.EV_REL, e.REL_Z, data[5]))
        
        for ev in [ev0, ev1, ev2, ev3, ev4, ev5]:
            ui.write_event(ev)
        ui.syn()
        sleep(0.5)

# Main loop
def main():

    # Run asyncio loop to capture all events.
    # TODO: these are deprecated, research and ID new functions.
    # NOTE: asyncio api will need update to fix. Maybe supress error for clean logs?
    asyncio.run(capture_gyro_events(gyro))
    loop = asyncio.get_event_loop()

if __name__ == "__main__":
    __init__()
    main()
