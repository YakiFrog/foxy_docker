#!/bin/bash
# test_cl_sequence.sh - Coordinate-based Square Sequence (Unified CL, Clockwise)

echo "=== Square Sequence Start (Unified CL, Clockwise) ==="
CENTER=5.5
SIDE=3.0

# 時計回りの座標計算
# P1: 右へ
P1_X=$(python3 -c "print($CENTER + $SIDE)")
P1_Y=$CENTER

# P2: 下へ (時計回りなので、Yを引く)
P2_X=$(python3 -c "print($CENTER + $SIDE)")
P2_Y=$(python3 -c "print($CENTER - $SIDE)")

# P3: 左へ
P3_X=$CENTER
P3_Y=$(python3 -c "print($CENTER - $SIDE)")

# P4: 上へ (元に戻る)
P4_X=$CENTER
P4_Y=$CENTER

# 順次実行
echo "[1/4] Moving to ($P1_X, $P1_Y) then rotate -90"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move_to', x: $P1_X, y: $P1_Y, speed: 1.0}"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'rotate', target_value: -90.0, speed: 1.0}"

echo "[2/4] Moving to ($P2_X, $P2_Y) then rotate -90"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move_to', x: $P2_X, y: $P2_Y, speed: 1.0}"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'rotate', target_value: -90.0, speed: 1.0}"

echo "[3/4] Moving to ($P3_X, $P3_Y) then rotate -90"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move_to', x: $P3_X, y: $P3_Y, speed: 1.0}"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'rotate', target_value: -90.0, speed: 1.0}"

echo "[4/4] Moving back to ($P4_X, $P4_Y) then rotate -90"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move_to', x: $P4_X, y: $P4_Y, speed: 1.0}"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'rotate', target_value: -90.0, speed: 1.0}"

echo "=== Square Complete (Clockwise)! ==="
