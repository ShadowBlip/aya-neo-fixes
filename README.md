# aya-neo-fixes
Various fixes for the Aya Neo 2021 &amp; 2021 Pro in Linux using systemd.

- Fixes reboot kernel panic by unloading WiFi module mT7921e on shutdown/reboot.
- Fixes loss of WiFi on suspend.
- Enables use of extra buttons on the controller. (depends on python-evdev)

# Installing

## From the AUR
- Run ```pikaur -S aya-neo-fixes-git``` as root.
- Run ```systemctl enable neo-controller``` as root.
- Run ```systemctl enable phantom-input``` as root.
- Run ```systemctl start neo-controller``` as root.
- Run ```systemctl start phantom-input``` as root.

## From source
- Install the python-evdev package.
- Run ```make install``` as root.


# Steam Configuration
After installing the package and enabling the services, Aya Neo NEXT devices require an additional step to fully configure the Home/Guide/Xbox button.

## Configuring through Big Picture Mode
It is typically easiest to use the touchscreen or an external keyboard to perform these steps.
- Open Settings (gear)
- Select Controller Settings
- Select the detected controller (Xbox 360 Controller)
- Select Define Layout
- Select Guide
- Press the Aya Space button
- Select Save

# Removing

## From the AUR
- Run ```pikaur -R aya-neo-fixes-git``` as root.

## From source
- Run ```make clean``` as root.

# Contributing

## Add New Device to neo-controller service
Please open a bug in [issues](https://github.com/ShadowBlip/aya-neo-fixes/issues) with the following information:
- Output of ```cat /sys/devices/virtual/dmi/id/product_name```
- Output of ```cat /proc/bus/input/devices```

I will also need you to install and run the ```evtest``` package per your distro package management. In most cases, unsupported buttons are attached to the ```AT Translated Set 2 keyboard``` device. Match the event# of that device when running as root. Provide the output of evtest for each button. Please label each button and corresponding keycode. I.E.:
```
Small button: 
Event: time 1652292081.491162, type 4 (EV_MSC), code 4 (MSC_SCAN), value db
Event: time 1652292081.491162, type 1 (EV_KEY), code 125 (KEY_LEFTMETA), value 1
Event: time 1652292081.491162, -------------- SYN_REPORT ------------
Event: time 1652292081.493659, type 4 (EV_MSC), code 4 (MSC_SCAN), value 20
Event: time 1652292081.493659, type 1 (EV_KEY), code 32 (KEY_D), value 1
Event: time 1652292081.493659, -------------- SYN_REPORT ------------
Event: time 1652292081.500637, type 4 (EV_MSC), code 4 (MSC_SCAN), value db
Event: time 1652292081.500637, type 1 (EV_KEY), code 125 (KEY_LEFTMETA), value 0
Event: time 1652292081.500637, -------------- SYN_REPORT ------------
Event: time 1652292081.505575, type 4 (EV_MSC), code 4 (MSC_SCAN), value 20
Event: time 1652292081.505575, type 1 (EV_KEY), code 32 (KEY_D), value 0
Event: time 1652292081.505575, -------------- SYN_REPORT ------------
```
