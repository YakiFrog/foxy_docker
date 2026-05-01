#!/bin/bash
# test_cl_sequence.sh - Coordinate-based Square Sequence (Unified CL)

echo "=== Square Sequence Start (Unified CL) ==="
CENTER=5.5
SIDE=3.0

# 座標の計算
P1_X=$(python3 -c "print($CENTER + $SIDE)")
P1_Y=$CENTER
P2_X=$(python3 -c "print($CENTER + $SIDE)")
P2_Y=$(python3 -c "print($CENTER + $SIDE)")
P3_X=$CENTER
P3_Y=$(python3 -c "print($CENTER + $SIDE)")
P4_X=$CENTER
P4_Y=$CENTER

# 順次実行
echo "[1/4] Moving to ($P1_X, $P1_Y)"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move_to', x: $P1_X, y: $P1_Y, speed: 1.0}"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'rotate', target_value: 90.0, speed: 1.0}"

echo "[2/4] Moving to ($P2_X, $P2_Y)"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move_to', x: $P2_X, y: $P2_Y, speed: 1.0}"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'rotate', target_value: 90.0, speed: 1.0}"

echo "[3/4] Moving to ($P3_X, $P3_Y)"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move_to', x: $P3_X, y: $P3_Y, speed: 1.0}"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'rotate', target_value: 90.0, speed: 1.0}"

echo "[4/4] Moving back to ($P4_X, $P4_Y)"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move_to', x: $P4_X, y: $P4_Y, speed: 1.0}"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'rotate', target_value: 90.0, speed: 1.0}"

echo "=== Square Complete! ==="
