# aya-neo-fixes
Various fixes for the Aya Neo 2021 &amp; 2021 Pro in Linux using systemd.

- Enables Wifi on Pro models using MediaTek MT7921K.
- Fixes reboot kernel panic by unloading WiFi module mT7921e on shutdown/reboot.
- Fixes loss of WiFi on suspend.
- Enables use of buttons on the controller. (depends on python-evdev)

# Installing
- Install the python-evdev package.
- Run ```make install``` as root.

# Removing
- Run ```make clean``` as root.
