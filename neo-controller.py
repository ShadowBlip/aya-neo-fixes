# Aya Neo Controller evdev mapping
# This will create a virtual UInput device and pull data from the built-in
# controller and "keyboard". Right side buttons are keyboard buttons that
# send macros (i.e. CTRL/ALT/DEL). We capture those events and send button
# presses that Steam understands.

import asyncio
from evdev import InputDevice, InputEvent, UInput, ecodes as e, categorize

# Declare global variables
# Supported system type
sys_type = None # 2021 or NEXT supported

# Buttons
quick_pressed = False # Quick Aciton Menu button (2021/NEXT)
home_pressed = False # Steam/xbox/playstaion button (2021/NEXT)
kb_pressed = False # OSK Button (2021)
tm_pressed = False # TM button (2021)
win_pressed = False # Docking screen replication button (2021)

# Identify the current device type. Kill script if not compatible.
sys_id = open("/sys/devices/virtual/dmi/id/product_name", "r").read().strip()
print("sys_id: ", sys_id)
if sys_id in ["AYANEO 2021 Pro Retro Power", "AYANEO 2021 Pro", "AYANEO 2021"]:
    sys_type = "2021"
elif sys_id in ["NEXT", "NEXT Pro"]:
    sys_type = "NEXT"
else:
    print(sys_id, "is not currently supported by this tool. Open an issue on\
 github at https://github.com/ShadowBlip/aya-neo-fixes if this is a bug.")
    exit()

# Get system input event devices
xb360 = InputDevice('/dev/input/event7') # If touchscreen isn't loaded, event6
keybd = InputDevice('/dev/input/event4')

# Grab the built-in devices. Prevents double input.
xb360.grab()
keybd.grab()

# Create the virtual controller.
ui = UInput.from_device(xb360, keybd, name='Aya Neo Controller', bustype=3, vendor=int('045e', base=16), product=int('028e', base=16), version=110)

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
            # 2021 Model Buttons
            case "2021":
                # TODO: shortcut changes from MODE+SELECT to MODE+NORTH when running
                # export STEAMCMD="steam -gamepadui -steampal -steamos3 -steamdeck"
                # in the user session. we will need to detect this somehow so it works.
                # on any install and session.

                # OSK from "KB". Works in-game in BPM but globally in gamepadui
                if active == [24, 97, 125] and not kb_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_NORTH, 1)
                    kb_pressed = True
                elif ev1.code in [24, 97, 125] and kb_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_NORTH, 0)
                    kb_pressed = False

                # Map to all detected screens for docking
                elif active == [125] and not win_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_P, 1)
                    win_pressed = True
                elif ev1.code == 125 and win_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_P, 0)
                    win_pressed = False

                # TODO: ID the keycode that the steam deck uses for the "..." button to
                # bring up the right side action menu. use EV_KEY "ESC", code 1 key for
                # this action.

                # Quick Action Menu
                elif active in [1] and not quick_pressed:
                    quick_pressed = True
                elif ev1.code  == 1 and quick_pressed:
                    quick_pressed = False

                # "TM" button. Currently unused
                elif active == [97, 100, 111] and not tm_pressed:
                    tm_pressed = True
                elif ev1.code in [97, 100, 111] and tm_pressed:
                    tm_pressed = False

            # NEXT Model Buttons
            case "NEXT":
                # Home Button
                if active == [96, 105, 133] and not home_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 1)
                    home_pressed = True
                elif ev1.code in [96, 105, 133] and home_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.BTN_MODE, 0)
                    home_pressed = False

                # TODO: ID the keycode that the steam deck uses for the "..." button to
                # bring up the right side action menu. Replace below key for this action.

                # Map to all detected screens for docking
                elif active == [40, 133] and not win_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 1)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_P, 1)
                    win_pressed = True
                elif ev1.code in [40, 133] and win_pressed:
                    ev1 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_LEFTMETA, 0)
                    ev2 = InputEvent(event.sec, event.usec, e.EV_KEY, e.KEY_P, 0)
                    win_pressed = False

        # Kill event spam that we don't use. Keeps output of evtest clean and prevents 
        if ev1.code in [1, 4, 24, 40, 96, 97, 100, 105, 111, 133] and ev1.type in [e.EV_MSC, e.EV_KEY]:
            continue
        elif ev1.code in [125] and ev2 == None:
            continue

        # Push out all events
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
