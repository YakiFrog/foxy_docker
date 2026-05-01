#!/bin/bash
# 指定された座標シーケンスで8の字を描くスクリプト

source /ros2_ws/install/setup.bash

# パラメータ設定 (中心 5.5, 5.5)
CENTER=5.5
OFFSET=1.5

# 各目標ポイントの計算
P1_X=$(python3 -c "print($CENTER + $OFFSET)"); P1_Y=$CENTER
P2_X=$(python3 -c "print($CENTER + $OFFSET)"); P2_Y=$(python3 -c "print($CENTER + $OFFSET)")
P3_X=$CENTER; P3_Y=$(python3 -c "print($CENTER + $OFFSET)")
P4_X=$CENTER; P4_Y=$CENTER
P5_X=$CENTER; P5_Y=$(python3 -c "print($CENTER - $OFFSET)")
P6_X=$(python3 -c "print($CENTER - $OFFSET)"); P6_Y=$(python3 -c "print($CENTER - $OFFSET)")
P7_X=$(python3 -c "print($CENTER - $OFFSET)"); P7_Y=$CENTER
P8_X=$CENTER; P8_Y=$CENTER

echo "=== Custom Figure-8 Sequence Start ==="

# --- 第1ループ (右上) ---
echo "[1/8] Move to ($P1_X, $P1_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P1_X, y: $P1_Y}"

echo "[2/8] Move to ($P2_X, $P2_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P2_X, y: $P2_Y}"

echo "[3/8] Move to ($P3_X, $P3_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P3_X, y: $P3_Y}"

echo "[4/8] Back to Center ($P4_X, $P4_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P4_X, y: $P4_Y}"

# --- 第2ループ (左下) ---
echo "[5/8] Move to ($P5_X, $P5_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P5_X, y: $P5_Y}"

echo "[6/8] Move to ($P6_X, $P6_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P6_X, y: $P6_Y}"

echo "[7/8] Move to ($P7_X, $P7_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P7_X, y: $P7_Y}"

echo "[8/8] Back to Center ($P8_X, $P8_Y)"
ros2 action send_goal /move_to_target bt_msgs/action/MoveToTarget "{x: $P8_X, y: $P8_Y}"

echo "=== Custom Figure-8 Complete! ==="
