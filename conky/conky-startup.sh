#!/bin/sh

## Script run on startup

## Wait 1 seconds
sleep 1

## Run conky
conky -dq -c /home/jimmeex/conky-cards/today_rc
conky -dq -c /home/jimmeex/conky-cards/processes_rc