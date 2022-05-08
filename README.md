# aya-neo-fixes
Various fixes for the Aya Neo 2021 &amp; 2021 Pro in Linux using systemd.

- Fixes reboot kernel panic by unloading WiFi module mT7921e on shutdown/reboot.
- Fixes loss of WiFi on suspend.
- Enables use of extra buttons on the controller. (depends on python-evdev)

# Installing

## From the AUR
- Run ```pikaur -S aya-neo-fixes-git``` as root.

## From source
- Install the python-evdev package.
- Run ```make install``` as root.

# Removing

## From the AUR
- Run ```pikaur -R aya-neo-fixes-git``` as root.

## From source
- Run ```make clean``` as root.
