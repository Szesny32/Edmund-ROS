# Edmund-ROS

## [TERMINAL-0] [RASPBERRY]
./test_ros_stream.sh

## [TERMINAL-1] [WSL]
docker run -it -p 1234:1234/udp --ipc=host --privileged -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ros2_slam_image

apt update && apt install nano ros-humble-rmw-cyclonedds-cpp -y

nano udp_receiver.py
- paste wsl/upd_receiver.py

source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=0
export ROS_LOCALHOST_ONLY=0

python3 udp_receiver.py

## [TERMINAL-2] [WSL]
docker ps
docker exec -it <CONTAINER_ID> bash

nano launch_rtabmap.sh
- paste wsl/launch_rtabmap.sh

chmod +x launch_rtabmap.sh
./launch_rtabmap.sh