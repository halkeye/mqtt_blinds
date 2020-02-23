#!/bin/bash
set -e
set -x

SRV=$(dig _mqtt._tcp srv +short +search)
# possible options for processing
MQTT_SERVER=$(echo $SRV | awk '{print $4}' | sed 's/\.$//')
MQTT_PORT=$(echo $SRV | awk '{print $3}' | sed 's/\.$//')
TOPIC=home/blinds/set
OVERRIDE_HOST=""

if [ ! -z $MQTT_SERVER ]; then
  OVERRIDE_HOST=$OVERRIDE_HOST -h "$MQTT_SERVER"
fi
if [ ! -z $MQTT_PORT ]; then
  OVERRIDE_HOST=$OVERRIDE_HOST -p "$MQTT_PORT"
fi
# read data
while read -r message
do
  echo $message
  for blind in 1 2 3 4 5 6 7 8; do
    if [ "$message" == "$blind|on" ]; then
        python ./blinds.py $blind close || true
    fi
    if [ "$message" == "$blind|off" ]; then
        python ./blinds.py $blind open || true
    fi
  done

done < <(mosquitto_sub $OVERRIDE_HOST -u "$USER" -P "$PASSWORD" -t "$TOPIC" -q 1)
