#!/bin/bash
# 変数を使って正方形を描くスクリプト

source /ros2_ws/install/setup.bash

# --- パラメータ設定 ---
CENTER=5.5
SIDE=3.0

# 各ポイントの座標計算 (Pythonで少数計算)
P1_X=$(python3 -c "print($CENTER + $SIDE)")
P1_Y=$CENTER

P2_X=$(python3 -c "print($CENTER + $SIDE)")
P2_Y=$(python3 -c "print($CENTER + $SIDE)")

P3_X=$CENTER
P3_Y=$(python3 -c "print($CENTER + $SIDE)")

P4_X=$CENTER
P4_Y=$CENTER
# --------------------

echo "=== Square Sequence Start ==="
echo "Center: $CENTER, Side Length: $SIDE"

echo "[1/8] Moving to Right-Bottom ($P1_X, $P1_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P1_X, y: $P1_Y}"
ros2 action send_goal /rotate_degrees bt_msgs/action/RotateDegrees "{target_degrees: 90.0}"

echo "[2/8] Moving to Right-Top ($P2_X, $P2_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P2_X, y: $P2_Y}"
ros2 action send_goal /rotate_degrees bt_msgs/action/RotateDegrees "{target_degrees: 90.0}"

echo "[3/8] Moving to Left-Top ($P3_X, $P3_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P3_X, y: $P3_Y}"
ros2 action send_goal /rotate_degrees bt_msgs/action/RotateDegrees "{target_degrees: 90.0}"

echo "[4/8] Moving to Left-Bottom (Back to Start: $P4_X, $P4_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P4_X, y: $P4_Y}"
ros2 action send_goal /rotate_degrees bt_msgs/action/RotateDegrees "{target_degrees: 90.0}"

echo "=== Square Complete! ==="
