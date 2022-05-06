# Aya Neo Controller
# Copyright 2022 Derek J. Clark <derekjohn dot clark at gmail dot com>
# This will create a virtual UInput device and pull data from the built-in
# controller and "keyboard". Right side buttons are keyboard buttons that
# send macros (i.e. CTRL/ALT/DEL). We capture those events and send button
# presses that Steam understands.

import asyncio
import threading

from evdev import InputDevice, InputEvent, UInput, ecodes as e, categorize, list_devices
from os import remove
from time import sleep

# Declare global variables
# Supported system type
sys_type = None # 2021 or NEXT supported

# Buttons
esc_pressed = False # ESC button (2021)
home_pressed = False # Steam/xbox/playsation button (NEXT)
kb_pressed = False # OSK Button (2021)
tm_pressed = False # Quick Aciton Menu button (2021, NEXT)
win_pressed = False # Dock Button (2021)

# Device Paths
xb_path = None
kb_path = None

# Identify the current device type. Kill script if not compatible.
sys_id = open("/sys/devices/virtual/dmi/id/product_name", "r").read().strip()

# All devices from Founders edition through 2021 Pro Retro Power use the same input hardware and keycodes.
if sys_id in ["AYANEO 2021 Pro Retro Power", "AYA NEO 2021 Pro Retro Power", "AYANEO 2021 Pro", "AYA NEO 2021 Pro", "AYANEO 2021", "AYA NEO 2021", "AYANEO FOUNDERS", "AYA NEO FOUNDERS"]:
    sys_type = "2021"
# NEXT uses new keycodes and has fewer buttons.
elif sys_id in ["NEXT"]:
    sys_type = "NEXT"
else:
    print(sys_id, "is not currently supported by this tool. Open an issue on\
 github at https://github.com/ShadowBlip/aya-neo-fixes if this is a bug.")
    exit()

# Identify system input event devices.
devices_orig = [InputDevice(path) for path in list_devices()]
for device in devices_orig:
    # Xbox 360 Controller
    if device.name == 'Microsoft X-Box 360 pad' and device.phys == 'usb-0000:03:00.3-4/input0':
        xb_path = device.path

    # Keyboard Device
    elif device.name == 'AT Translated Set 2 keyboard' and device.phys == 'isa0060/serio0/input0':
        kb_path = device.path

if not xb_path or not kb_path:
    print("Keyboard and xbox360 controller not found. Exiting.")
    exit()

# Grab the built-in devices. Prevents double input.
xb360 = InputDevice(xb_path)
xb360.grab()
keybd = InputDevice(kb_path)
keybd.grab()

# Create the virtual controller.
ui = UInput.from_device(xb360, keybd, name='Aya Neo Controller', bustype=3, vendor=int('045e', base=16), product=int('028e', base=16), version=110)

# Delete the reference to the original controllers to hide them from the user/steam.
remove(xb_path)
remove(kb_path)

async def capture_events(device):

    # Get access to global variables. These are globalized because the funtion
    # is instanciated twice and need to persist accross both instances.
    global esc_pressed
    global home_pressed
    global kb_pressed
    global tm_pressed
    global win_pressed
    global sys_type

    # Capture events for the given device.
    async for event in device.async_read_loop():

        # We use active keys instead of ev1.code as we will override ev1 and
        # we don't want to trigger additional/different events when doing that
        active= device.active_keys()
        ev1 = event # pass through the current event, override if needed
        ev2 = None # optional second button (i.e. home + select or super + p)
        match sys_type:

            case "2021": # 2021 Model Buttons
                # TODO: shortcut changes from MODE+SELECT to MODE+NORTH when running
                # export STEAMCMD="steam -gamepadui -steampal -steamos3 -steamdeck"
                # in the user session. We will need to detect this somehow so it works.
                # on any install and session.

                # KB BUTTON. Open OSK. Works in-game in BPM but globally in gamepadui
                if active == [24, 97, 125] and not kb_pressed and ev1.value == 1:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_NORTH, 1)
                    kb_pressed = True
                elif active == [97] and kb_pressed and ev1.value == 0:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_NORTH, 0)
                    kb_pressed = False

                # WIN BUTTON. Map to all detected screens for docking. Not working
                # TODO: Get this working. Tried SUPER+P and SUPER+D.
                # The extra conditions handle pressing WIN while pressing KB since
                # both use code 125. Letting go of KB first still clears win_pressed
                # as key 125 is released at the system level.
                elif not win_pressed and ev1.value in [1,2] and (active == [125] or (active == [24, 97, 125] and kb_pressed)):
                    #ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 1)
                    #ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_D, 1)
                    win_pressed = True
                elif (active in [[], [24, 97]] and win_pressed) or (active == [125] and ev1.code == 125 and win_pressed and ev1.value == 0):
                    #ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 0)
                    #ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_D, 0)
                    win_pressed = False

                # ESC BUTTON. Unused. Passing so it functions as an "ESC" key for now.
                # Add 1 to below list if changed.
                elif ev1.code == 1 and not esc_pressed and ev1.value == 1:
                    esc_pressed = True
                elif ev1.code == 1 and esc_pressed and ev1.value == 0:
                    esc_pressed = False

                # TM BUTTON. Quick Action Menu
                elif active == [97, 100, 111] and not tm_pressed and ev1.value == 1:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 1)
                    tm_pressed = True
                elif ev1.code in [97, 100, 111] and tm_pressed and ev1.value == 0:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 0)
                    tm_pressed = False

            case "NEXT": # NEXT Model Buttons
                # AYA SPACE BUTTON. Home Button
                if active in [[96, 105, 133], [97, 125, 88]] and not home_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 1)
                    home_pressed = True
                elif ev1.code in [88, 96, 97, 105, 125, 133] and home_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 0)
                    home_pressed = False

                # CONFIGURABLE BUTTON. Quick Action Menu.
                elif active == [40, 133] and not tm_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 1)
                    tm_pressed = True
                elif ev1.code in [40, 133] and tm_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 0)
                    tm_pressed = False

        # Kill events that we override. Keeps output clean.
        if ev1.code in [4, 24, 40, 96, 97, 100, 105, 111, 133] and ev1.type in [e.EV_MSC, e.EV_KEY]:
            continue # Add 1 to list if ESC used above
        elif ev1.code in [125] and ev2 == None: # Only kill KEY_LEFTMETA if its not used as a key combo.
            continue

        # Push out all events. Includes all button/joy events from controller we dont override.
        ui.write_event(ev1)
        if ev2:
            ui.write_event(ev2)
        ui.syn()

def remove_phantoms():
    loops=0
    while True:
        devices_orig = [InputDevice(path) for path in list_devices()]
        for device in devices_orig:
            # Delete any steam input devices from the original controller.
            if device.phys == "" or device.phys == None:
                remove(device.path)
                print("Removed ", device.path)
        if loops <= 10:
            loops +=1
            sleep(1)
        else:
            break
# Run asyncio loop to capture all events
# TODO: these are deprecated, research and ID new functions.
for device in xb360, keybd:
    asyncio.ensure_future(capture_events(device))

# Look for phantom controllers for a few seconds and delete them.
t = threading.Thread(target=remove_phantoms())
t.start()
loop = asyncio.get_event_loop()
loop.run_forever()
