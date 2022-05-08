#!/bin/bash
set -e

echo "Removing WiFi fix for MT7921K"
rm -v /etc/modprobe.d/rz608.conf

echo "Removing reboot kernel panic fix."
rm -v /usr/lib/systemd/system-shutdown/mt7921e.shutdown

echo "Removing loss of WiFi on suspend fix."
rm -v /etc/systemd-suspend-mods.conf
rm /usr/lib/systemd/system-sleep/systemd-suspend-mods.sh

echo "Disabling unmapped buttons."
systemctl stop neo-controller && systemctl disable neo-controller
rm -v /etc/systemd/system/neo-controller.service
rm -v /usr/local/bin/neo-controller.py

echo "Disabling phantom Steam Input fix."
systemctl stop phantom-input && systemctl disable phantom-input
rm -v /usr/local/bin/phantom-input.py
rm -v /etc/systemd/system/phantom-input.service

exit 0
