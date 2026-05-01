#!/bin/bash
# test_cl_figure8.sh - Figure-8 with Geometric Variables

# --- 設定値 ---
SCALE=1.0      # 直進部分の基本単位
RADIUS=0.5     # 円弧の半径
SPEED=1.0      # 走行速度
P_MODE=0       # 0: YAMLデフォルト
# --------------

echo "=== Full Closed Loop Figure-8 Start (Scale: $SCALE, Radius: $RADIUS) ==="

echo "Starting Straight $RADIUS m"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $RADIUS, speed: $SPEED, p_control_mode: $P_MODE}"

echo "--- Starting Left Loop ---"
for i in {1..3}
do
    echo "[Left $i/3] Step 1: Moving Straight ($SCALE m)"
    ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $SCALE, speed: $SPEED, p_control_mode: $P_MODE}"
    
    echo "[Left $i/3] Step 2: Left Arc (R=$RADIUS)"
    ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'arc', target_value: 90.0, speed: $SPEED, radius: $RADIUS, p_control_mode: $P_MODE}"
done

# つなぎの直線距離を計算: RADIUS * 2 + SCALE
CONN_DIST=$(awk "BEGIN {print $RADIUS * 2 + $SCALE}")
echo "Connecting Straight $CONN_DIST m"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $CONN_DIST, speed: $SPEED, p_control_mode: $P_MODE}"

echo "--- Starting Right Loop ---"
for i in {1..3}
do
    echo "[Right $i/3] Step 1: Moving Straight ($SCALE m)"
    ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $SCALE, speed: $SPEED, p_control_mode: $P_MODE}"
    
    echo "[Right $i/3] Step 2: Right Arc (R=$RADIUS)"
    ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'arc', target_value: -90.0, speed: $SPEED, radius: $RADIUS, p_control_mode: $P_MODE}"
done

# 最後の直線距離も同様に計算
FINAL_DIST=$(awk "BEGIN {print $RADIUS + $SCALE}")
echo "Final Straight $FINAL_DIST m"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $FINAL_DIST, speed: $SPEED, p_control_mode: $P_MODE}"

echo "=== Full Closed Loop Figure-8 Complete! ==="
