# Aya Neo Controller evdev mapping
# This will create a virtual UInput device and pull data from the built-in
# controller and "keyboard". Right side buttons are keyboard buttons that
# send macros (i.e. CTRL/ALT/DEL). We capture those events and send button
# presses that Steam understands.

import asyncio
from evdev import InputDevice, InputEvent, UInput, ecodes as e, categorize

# Get system input event devices
dmi_info = open("/sys/devices/virtual/dmi/id/product_name", "r")
sys_id = dmi_info.read().strip()
sys_type = None
if sys_id in ["AYANEO 2021 Pro Retro Power", "AYANEO 2021 Pro", "AYANEO 2021"]:
    sys_type = "2021"
    xb360 = InputDevice('/dev/input/event7')
    keybd = InputDevice('/dev/input/event4')
elif sys_id in ["NEXT", "NEXT Pro"]:
    sys_type = "NEXT"
    xb360 = InputDevice('/dev/input/event6')
    keybd = InputDevice('/dev/input/event4')
else:
    print(sys_id, "is not currently supported by this tool. Open an issue on\
 github at https://github.com/ShadowBlip/aya-neo-fixes if this is a bug.")
    exit()

# Grab the built-in devices. Prevents double input.
xb360.grab()
keybd.grab()

# Create the virtual controller.
ui = UInput.from_device(xb360, keybd, name='Aya Neo Controller')

# Track if we pressed our virtual keys so we can send keyup events
home_pressed = False
kb_pressed = False
win_pressed = False

async def capture_events(device):
    global home_pressed
    global kb_pressed
    global win_pressed
    async for event in device.async_read_loop():
        active= device.active_keys()
        ev1 = event # pass through the event
        ev2 = None # optional second button (i.e. home + select or super + p)

        # 2021 Model Buttons 
        # OSK from "KB" button 2021
        match sys_type:
            case "2021":
                # OSK from "KB"
                if active == [24, 97, 125] and not kb_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_SELECT, 1)
                    kb_pressed = True
                elif ev1.code in [24, 97, 125] and kb_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_SELECT, 0)
                    kb_pressed = False

                # Map to all detected screens for docking
                elif active == [97, 100, 111] and not win_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_P, 1)
                    win_pressed = True
                elif ev1.code in [97, 100, 111] and win_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_P, 0)
                    win_pressed = False
    
        # Next Model Buttons
        match sys_type:
            case "NEXT":
                # Home Button
                if active == [96, 105, 133] and not home_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 1)
                    home_pressed = True
                elif ev1.code in [96, 105, 133] and home_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 0)
                    home_pressed = False
        
                # Map to all detected screens for docking
                elif active == [40, 133] and not win_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_P, 1)
                    win_pressed = True
                elif ev1.code in [40, 133] and win_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_P, 0)
                    win_pressed = False

        # Kill event spam that we don't use
        if ev1.code in [4, 24, 40, 96, 97, 100, 105, 111, 133] and ev1.type in [e.EV_MSC, e.EV_KEY]:
            continue
        
        # Push out all events 
        ui.write_event(ev1)
        if ev2:
            ui.write_event(ev2)
        ui.syn()

# Run asyncio loop to capture all events
for device in xb360, keybd:
    asyncio.ensure_future(capture_events(device))
loop = asyncio.get_event_loop()
loop.run_forever()
