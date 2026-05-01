#!/bin/bash
set -e

# Setup ROS 2 Foxy environment
source "/opt/ros/foxy/setup.bash"

# Build local packages if they exist
if [ -d "/ros2_ws/src" ]; then
    cd /ros2_ws
    # 依存関係のチェックはスキップしてビルド
    # colcon build --symlink-install
fi

exec "$@"
