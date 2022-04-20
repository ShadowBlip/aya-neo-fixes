# Aya Neo Controller
# Copyright 2022 Derek J. Clark <derekjohn dot clark at gmail dot com>
# This will create a virtual UInput device and pull data from the built-in
# controller and "keyboard". Right side buttons are keyboard buttons that
# send macros (i.e. CTRL/ALT/DEL). We capture those events and send button
# presses that Steam understands.

import asyncio
from evdev import InputDevice, InputEvent, UInput, ecodes as e, categorize, list_devices
from os import remove

# Declare global variables
# Supported system type
sys_type = None # 2021 or NEXT supported

# Buttons
quick_pressed = False # Quick Aciton Menu button (2021/NEXT)
home_pressed = False # Steam/xbox/playstaion button (2021/NEXT)
kb_pressed = False # OSK Button (2021)
tm_pressed = False # TM button (2021)
win_pressed = False # Docking screen replication button (2021)

# Device Paths
xb_path = None
kb_path = None

# Identify the current device type. Kill script if not compatible.
sys_id = open("/sys/devices/virtual/dmi/id/product_name", "r").read().strip()
print("sys_id: ", sys_id)
if sys_id in ["AYANEO 2021 Pro Retro Power", "AYANEO 2021 Pro", "AYANEO 2021"]:
    sys_type = "2021"
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

    # Delete any steam input devices from the original controller.
    elif device.phys == "" or device.phys == None:
        remove(device.path)

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
    global quick_pressed
    global home_pressed
    global kb_pressed
    global tm_pressed
    global win_pressed
    global sys_type

    async for event in device.async_read_loop():

        # we use active keys instead of ev1.code as we will override ev1 and
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
                if active == [24, 97, 125] and not kb_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_NORTH, 1)
                    kb_pressed = True
                elif ev1.code in [24, 97, 125] and kb_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_NORTH, 0)
                    kb_pressed = False

                # WIN BUTTON. Map to all detected screens for docking. Not working
                # TODO: Get this working. Tried SUPER+P and SUPER+D.
                elif active == [125] and not win_pressed:
                    #ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 1)
                    #ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_D, 1)
                    win_pressed = True
                elif ev1.code == 125 and win_pressed:
                    #ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 0)
                    #ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_D, 0)
                    win_pressed = False

                # ESC BUTTON. Unused. Passing so it functions as an "ESC" key for now.
                # Add 1 to below list if changed.
                elif active in [1] and not tm_pressed:
                    tm_pressed = True
                elif ev1.code  == 1 and tm_pressed:
                    tm_pressed = False

                # TM BUTTON. Quick Action Menu
                elif active == [97, 100, 111] and not quick_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 1)
                    quick_pressed = True
                elif ev1.code in [88, 96, 97, 105, 125, 133] and home_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 0)
                    quick_pressed = False

            case "NEXT": # NEXT Model Buttons
                # AYA SPACE BUTTON. Home Button
                if active in [[96, 105, 133], [97, 125, 88]] and not home_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 1)
                    home_pressed = True
                elif ev1.code in [96, 105, 133] and home_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 0)
                    home_pressed = False

                # CONFIGURABLE BUTTON. Quick Action Menu.
                elif active == [40, 133] and not quick_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 1)
                    quick_pressed = True
                elif ev1.code in [40, 133] and qucik_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 0)
                    quick_pressed = False

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

# Run asyncio loop to capture all events
# TODO: these are deprecated, research and ID new functions.
for device in xb360, keybd:
    asyncio.ensure_future(capture_events(device))
loop = asyncio.get_event_loop()
loop.run_forever()
