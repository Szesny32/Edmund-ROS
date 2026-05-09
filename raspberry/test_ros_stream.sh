#!/bin/bash

if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$STREAM_DEST_IP" ]; then
    echo "ERROR: STREAM_DEST_IP variable is empty or missing in .env file!"
    echo "Please set it in .env (e.g., STREAM_DEST_IP=192.168.0.220)"
    exit 1
fi

if [ -z "$STREAM_PORT" ]; then
    echo "ERROR: STREAM_PORT variable is empty! Add it to .env (e.g., STREAM_PORT=1234)"
    exit 1
fi

echo "Connecting to ROS2 receiver at: $STREAM_DEST_IP:$STREAM_PORT..."

rpicam-vid \
  --width 1280 \
  --height 480 \
  --framerate 20 \
  --codec mjpeg \
  --inline \
  --timeout 0 \
  -o "udp://$STREAM_DEST_IP:$STREAM_PORT"