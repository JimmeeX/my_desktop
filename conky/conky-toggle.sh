#!/bin/sh

# Script to toggle on/off. I binded this script to a shortcut
if pidof conky | grep [0-9] > /dev/null
then
    killall conky
else
    conky -dq -c /home/jimmeex/conky-cards/today_rc
    conky -dq -c /home/jimmeex/conky-cards/processes_rc
fi