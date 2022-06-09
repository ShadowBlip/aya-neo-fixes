#!/bin/bash
set -e

echo "Adding reboot kernel panic fix."
cp -v mt7921e.shutdown /usr/lib/systemd/system-shutdown

echo "Adding suspend loss of WiFi on suspend fix"
cp -v systemd-suspend-mods.conf /etc/systemd-suspend-mods.conf
cp -v systemd-suspend-mods.sh /usr/lib/systemd/system-sleep/systemd-suspend-mods.sh

echo "Enabling controller functionality. NEXT users will need to configure the Home button in steam."
cp -v neo-controller.py /usr/local/bin/
cp -v neo-controller.service /etc/systemd/system/
cp -v 60-neo-controller.rules /etc/udev/rules.d/
cp -v bmi160_i2c.conf /etc/modules-load.d/
systemctl enable neo-controller && systemctl start neo-controller

exit 0
