#!/bin/bash
# 1辺の長さ 1 の正方形を描くスクリプト

source /ros2_ws/install/setup.bash

echo "=== Square Sequence Start (Side: 1.0) ==="

# (5.5, 5.5) からスタートと仮定
echo "[1/8] Moving to (6.5, 5.5)..."
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: 6.5, y: 5.5}"
ros2 action send_goal /rotate_degrees bt_msgs/action/RotateDegrees "{target_degrees: 90.0}"

echo "[2/8] Moving to (6.5, 6.5)..."
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: 6.5, y: 6.5}"
ros2 action send_goal /rotate_degrees bt_msgs/action/RotateDegrees "{target_degrees: 90.0}"

echo "[3/8] Moving to (5.5, 6.5)..."
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: 5.5, y: 6.5}"
ros2 action send_goal /rotate_degrees bt_msgs/action/RotateDegrees "{target_degrees: 90.0}"

echo "[4/8] Moving to (5.5, 5.5)..."
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: 5.5, y: 5.5}"
ros2 action send_goal /rotate_degrees bt_msgs/action/RotateDegrees "{target_degrees: 90.0}"

echo "=== Square Complete! ==="
