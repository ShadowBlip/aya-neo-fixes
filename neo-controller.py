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

from BMI160_i2c import Driver
from evdev import InputDevice, InputEvent, UInput, ecodes as e, categorize, list_devices, RelEvent
from pathlib import PurePath as p
from shutil import move
from time import sleep

# Declare global variables
# Supported system type
system_type = None # 2021 or NEXT supported

# Track button on/off (prevents spam presses)
esc_pressed = False # ESC button (GEN1)
home_pressed = False # Steam/xbox/playsation button (GEN2)
kb_pressed = False # OSK Button (GEN1)
tm_pressed = False # Quick Aciton Menu button (GEN1, GEN2)
win_pressed = False # Dock Button (GEN1)

# Devices
gyro_device = Driver(0x68)
keyboard_device = None
new_device = None
xb360_device = None

# Paths
hide_path = "/dev/input/.hidden/"
keyboarb_event = None
keyboard_path = None
xb360_event = None
xb360_path = None

def __init__():

    global keyboard_event
    global keyboard_path
    global keyboard_device
    global new_device
    global system_type
    global xb360_device
    global xb360_event
    global xb360_path

    xb360_capabilities = None

    # Identify the current device type. Kill script if not compatible.
    system_id = open("/sys/devices/virtual/dmi/id/product_name", "r").read().strip()

    # All devices from Founders edition through 2021 Pro Retro Power use the same 
    # input hardware and keycodes.
    if system_id in ["AYANEO 2021 Pro Retro Power",
            "AYA NEO 2021 Pro Retro Power",
            "AYANEO 2021 Pro",
            "AYA NEO 2021 Pro",
            "AYANEO 2021",
            "AYA NEO 2021",
            "AYANEO FOUNDERS",
            "AYA NEO FOUNDERS",
            "AYANEO FOUNDER",
            "AYA NEO FOUNDER",
            ]:
        system_type = "GEN1"

    # NEXT uses new keycodes and has fewer buttons.
    elif system_id in ["NEXT",
            "Next Pro",
            "AYA NEO NEXT Pro",
            "AYANEO NEXT Pro",
            ]:
        system_type = "GEN2"

    # Block devices that aren't supported as this could cause issues.
    else:
        print(system_id, "is not currently supported by this tool. Open an issue on \
GitHub at https://github.com/ShadowBlip/aya-neo-fixes if this is a bug. If possible, \
please run the capture-system.py utility found on the GitHub repository and upload \
that file with your issue.")
        exit(1)

    # Identify system input event devices.
    attempts = 0
    while attempts < 3:
        try:
            devices_original = [InputDevice(path) for path in list_devices()]
        # Some funky stuff happens sometimes when booting. Give it another shot.
        except OSError:
            attempts += 1
            sleep(1)
            continue

        # Grab the built-in devices. This will give us exclusive acces to the devices and their capabilities.
        for device in devices_original:

            # Xbox 360 Controller
            if device.name == 'Microsoft X-Box 360 pad' and device.phys == 'usb-0000:03:00.3-4/input0':
                xb360_path = device.path
                xb360_device = InputDevice(xb360_path)
                xb360_capabilities = xb360_device.capabilities()
                xb360_device.grab()

            # Keyboard Device
            elif device.name == 'AT Translated Set 2 keyboard' and device.phys == 'isa0060/serio0/input0':
                keyboard_path = device.path
                keyboard_device = InputDevice(keyboard_path)
                keyboard_device.grab()

        # Sometimes the service loads before all input devices have full initialized. Try a few times.
        if not xb360_path or not keyboard_path:
            attempts += 1
            sleep(1)
        else:
            break

    # Catch if devices weren't found.
    if not xb360_device or not keyboard_device:
        print("Keyboard and/or X-Box 360 controller not found.\n \
If this service has previously been started, try rebooting.\n \
Exiting...")
        exit(1)

    # Create the virtual controller.
    new_device = UInput.from_device(xb360_device, keyboard_device, name='Aya Neo Controller', bustype=3, vendor=int('045e', base=16), product=int('028e', base=16), version=110)

    # Move the reference to the original controllers to hide them from the user/steam.
    os.makedirs(hide_path, exist_ok=True)
    keyboard_event = p(keyboard_path).name
    move(keyboard_path, hide_path+keyboard_event)
    xb360_event = p(xb360_path).name
    move(xb360_path, hide_path+xb360_event)


# Captures keyboard events and translates them to virtual device events.
async def capture_keyboard_events(device):

    # Get access to global variables. These are globalized because the funtion
    # is instanciated twice and need to persist accross both instances.
    global esc_pressed
    global home_pressed
    global kb_pressed
    global tm_pressed
    global win_pressed
    global system_type

    # Capture events for the given device.
    async for event in device.async_read_loop():

        # We use active keys instead of ev1.code as we will override ev1 and
        # we don't want to trigger additional/different events when doing that
        active = device.active_keys()

        event1 = event # pass through the current event, override if needed.
        event2 = None # optional second button (i.e. home + select or super + p)
        if active != []:
            print(active, system_type)
        match system_type:

            case "GEN1": # 2021 Models and previous.
                # TODO: shortcut changes from MODE+SELECT to MODE+NORTH when running
                # export STEAMCMD="steam -gamepadui -steampal -steamos3 -steamdeck"
                # in the user session. We will need to detect this somehow so it works.
                # on any install and session.

                # KB BUTTON. Open OSK. Works in-game in BPM but globally in gamepadui
                if active == [24, 97, 125] and not kb_pressed and event1.value == 1:
                    event1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 1)
                    event2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_NORTH, 1)
                    kb_pressed = True
                elif active == [97] and kb_pressed and event1.value == 0:
                    event1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 0)
                    event2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_NORTH, 0)
                    kb_pressed = False

                # WIN BUTTON. Map to all detected screens for docking. Not working
                # TODO: Get this working. Tried SUPER+P and SUPER+D.
                # The extra conditions handle pressing WIN while pressing KB since
                # both use code 125. Letting go of KB first still clears win_pressed
                # as key 125 is released at the system level.
                elif not win_pressed and event1.value in [1,2] and (active == [125] or (active == [24, 97, 125] and kb_pressed)):
                    #ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 1)
                    #ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_D, 1)
                    win_pressed = True
                elif (active in [[], [24, 97]] and win_pressed) or (active == [125] and event1.code == 125 and win_pressed and event1.value == 0):
                    #ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 0)
                    #ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_D, 0)
                    win_pressed = False

                # ESC BUTTON. Unused. Passing so it functions as an "ESC" key for now.
                # Add 1 to below list if changed.
                elif event1.code == 1 and not esc_pressed and event1.value == 1:
                    esc_pressed = True
                elif event1.code == 1 and esc_pressed and event1.value == 0:
                    esc_pressed = False

                # TM BUTTON. Quick Action Menu
                elif active == [97, 100, 111] and not tm_pressed and event1.value == 1:
                    event1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 1)
                    event2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 1)
                    tm_pressed = True
                elif event1.code in [97, 100, 111] and tm_pressed and event1.value == 0:
                    event1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 0)
                    event2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 0)
                    tm_pressed = False

            case "GEN2": # NEXT Model and beyond.
                # AYA SPACE BUTTON. -> Home Button
                if active in [[96, 105, 133], [97, 125, 88], [88, 97, 125]] and not home_pressed and event1.value == 1:
                    event1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 1)
                    home_pressed = True
                elif event1.code in [88, 96, 97, 105, 133] and home_pressed and event1.value == 0:
                    event1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 0)
                    home_pressed = False

                # CONFIGURABLE BUTTON. -> Quick Action Menu.
                # NOTE: Some NEXT models use SUPER+D, Aya may be trying to use this as fullscreen docking.
                # TODO: Investigate if configuring in AYA SPACE changes these keycodes in firmware.
                elif active in [[40, 133], [32, 125]] and not tm_pressed and event1.value == 1:
                    event1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 1)
                    event2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 1)
                    tm_pressed = True
                elif event1.code in [40, 133, 32] and tm_pressed and event1.value == 0:
                    event1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTCTRL, 0)
                    event2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_2, 0)
                    tm_pressed = False

        # Kill events that we override. Keeps output clean.
        if event1.code in [4, 24, 32, 40, 88, 96, 97, 100, 105, 111, 133] and event1.type in [e.EV_MSC, e.EV_KEY]:
            continue # Add 1 to list if ESC used above
        elif event1.code in [125] and event2 == None: # Only kill KEY_LEFTMETA if its not used as a key combo.
            continue

        # Push out all events. Includes all button/joy events from controller we dont override.
        new_device.write_event(event1)
        print(event1)
        if event2:
            print(event2)
            new_device.write_event(event2)
        new_device.syn()


# Captures the xb360_device events and passes them through.
async def capture_controller_events(device):
    async for event in device.async_read_loop():
        new_device.write_event(event)
        new_device.syn()


# Captures BMI160 events and translates them to virtual device events.
async def capture_gyro_events(device):
    while True:
        data = device.getMotion6()
        # fetch all gyro and acclerometer values
        event1 = RelEvent(InputEvent(0, 0, e.EV_ABS, e.ABS_RX, data[0]))
        event2 = RelEvent(InputEvent(0, 0, e.EV_ABS, e.ABS_RY, data[1]))
        #ev3 = RelEvent(InputEvent(0, 0, e.EV_ABS, e.ABS_RZ, data[2]))
        #ev1 = RelEvent(InputEvent(0, 0, e.EV_ABS, e.ANS_RX, data[3]))
        #ev2 = RelEvent(InputEvent(0, 0, e.EV_ABS, e.ABS_RY, data[4]))
        #ev3 = RelEvent(InputEvent(0, 0, e.EV_ABS, e.ABS_RZ, data[5]))

        for event in [event1, event2]: #, ev3]:
            new_device.write_event(event)
        new_device.syn()
        await asyncio.sleep(0.05)

# Gracefull shutdown.
async def restore(loop):

    print('Receved exit signal. Restoring Devices.')

    # Both devices threads will attempt this, so ignore if they have been moved.
    try:
        move(hide_path+keyboard_event, keyboard_path)
    except FileNotFoundError:
        pass
    try:
        move(hide_path+xb360_event, xb360_path)
    except FileNotFoundError:
        pass

    # Kill all tasks. They are infinite loops so we will wait forver.
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    loop.stop()
    print("Device restore complete. Stopping...")


# Main loop
def main():

    # Run asyncio loop to capture all events.
    loop = asyncio.get_event_loop()
    loop.create_future()

    # Attach the event loop of each device to the asyncio loop.
    asyncio.ensure_future(capture_controller_events(xb360_device))
    asyncio.ensure_future(capture_keyboard_events(keyboard_device))
    asyncio.ensure_future(capture_gyro_events(gyro_device))

    # Establish signaling to handle gracefull shutdown.
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT, signal.SIGQUIT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(restore(loop)))

    try:
        loop.run_forever()
    except Exception as e:
        print("OBJECTION!\n", e)
    finally:
        loop.stop()

if __name__ == "__main__":
    __init__()
    main()
