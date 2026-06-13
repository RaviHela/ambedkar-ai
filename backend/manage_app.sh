#!/bin/bash
# Dr. B.R. Ambedkar AI - Hourly schedule manager

HOUR=$(TZ='Asia/Kolkata' date +%H)
LOG="/var/log/ambedkar-scheduler.log"

# Between 11 PM (23) and 8 AM (8) - app should be OFF
if [ $HOUR -ge 23 ] || [ $HOUR -lt 8 ]; then
    if systemctl is-active --quiet ambedkar-ai; then
        sudo systemctl stop ambedkar-ai
        echo "$(TZ='Asia/Kolkata' date): App stopped (off hours)" >> $LOG
    fi
else
    # Between 8 AM and 11 PM - app should be ON
    if ! systemctl is-active --quiet ambedkar-ai; then
        sudo systemctl start ambedkar-ai
        echo "$(TZ='Asia/Kolkata' date): App started (peak hours)" >> $LOG
    fi
fi
