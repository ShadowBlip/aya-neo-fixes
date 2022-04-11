# aya-neo-fixes
Various fixes for the Aya Neo 2021 &amp; 2021 Pro in Linux using systemd.

- Enables Wifi on Pro models using MediaTek MT7921K.
- Fixes reboot kernel panic by unloading WiFi module mT7921e on shutdown/reboot. 
- Fixes loss of WiFi on suspend. (Depends on systemd-suspend-modules package)
- Enables use of buttons on the controller. (depends on python-evdev)

# Installing
- Install the systemd-suspend-modules package.
- Install the python-evdev package.
- Run ```make install``` as root.

# Configuring Controller
Once the controller fix has been installed, the original controller that is detected by steam will not function and you wont have input until you configure the new controller. It is recommended that you use a USB keyboard to set up the controller as the interface is not touch-screen friendly.
In Big Picture Mode:
- Open the settings cog.
- Open Controller Setting.
- Select the new controller.
- Select Define Layout.
- Navigate to each entry and select the appropriate button.

I've had good luck setting it as a Generic Gamepad and enabling Generic Gamepad Configuration Support. Please let me know if you have success/issues with setting it as another controller.

# Removing
- Run ```make clean``` as root.
