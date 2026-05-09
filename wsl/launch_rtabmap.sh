#!/bin/bash

source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=0
export ROS_LOCALHOST_ONLY=0

ros2 launch rtabmap_launch rtabmap.launch.py \
    rtabmap_viz:=true \
    stereo:=true \
    frame_id:=camera_link_left \
    left_image_topic:=/left/image_raw \
    right_image_topic:=/right/image_raw \
    left_camera_info_topic:=/left/camera_info \
    right_camera_info_topic:=/right/camera_info \
    approx_sync:=true \
    visual_odometry:=true \
    args:="-d --Rtabmap/DetectionRate 1 --Vis/CorType 0 --GFTT/MinDistance 10 --Odom/StampOffset 0.05"
