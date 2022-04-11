#!/bin/bash
set -e

MODULES=$(cat suspend-modules.conf)

echo "Removing WiFi fix for MT7921K"
rm -v /etc/modprobe.d/rz608.conf
rm -v /etc/udev/rules.d/99-rz608.rules

echo "Removing reboot kernel panic fix."
rm -v /usr/lib/systemd/system-shutdown/mt7921e.shutdown

echo "Removing suspend-modules fix."
for line in $MODULES; do
	echo "Removing $line from /etc/suspend-modules.conf"
	sed -i "/^$line/d" /etc/suspend-modules.conf 	
done

echo "Disabling unmapped buttons."
systemctl stop  neo-controller && systemctl disable neo-controller
rm -v /etc/systemd/system/neo-controller.service
rm -rfv /usr/share/ayaneo
exit 0
