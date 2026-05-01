#!/bin/bash
# Foxy 記録用 ROS 2 Bag スクリプト

BAG_DIR="/ros2_ws/bags"
mkdir -p "$BAG_DIR"

# タイムスタンプの取得
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BAG_NAME="rosbag_$TIMESTAMP"

echo "=== ROS 2 Bag Recording (Foxy) ==="
echo "Recording topics:"
echo "  - /turtle1/cmd_vel"
echo "  - /turtle1/pose"
echo "  - /tf"
echo "  - /tf_static"
echo ""
echo "Saving to: $BAG_DIR/$BAG_NAME"
echo "Press Ctrl+C to stop recording."

# 記録開始
ros2 bag record -o "$BAG_DIR/$BAG_NAME" /turtle1/cmd_vel /turtle1/pose /tf /tf_static
