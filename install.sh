#!/bin/bash

cp rz608.conf /etc/modprobe.d/
cp 99-rz608.rules /etc/udev/rules.d/
cp mt7921e.shutdown /usr/lib/systemd/system-shutdown
cat suspend-modules.conf | tee -a /etc/suspend-modules.conf

exit 0
