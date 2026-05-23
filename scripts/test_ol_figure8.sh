#!/bin/bash
# test_ol_figure8.sh - Open Loop Figure-8 with Variables

# --- 設定値 ---
SCALE=5.0      # 基本単位
RADIUS=2.5     # 円弧の半径
SPEED=1.0      # 走行速度
# --------------

echo "=== Open Loop Figure-8 Start (Scale: $SCALE, Radius: $RADIUS) ==="

echo "Starting Straight $RADIUS m"
ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $RADIUS, speed: $SPEED}"

echo "--- Starting Left Loop ---"
for i in {1..3}
do
    echo "[Left $i/3] Step 1: Moving Straight ($SCALE m)"
    ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $SCALE, speed: $SPEED}"
    
    echo "[Left $i/3] Step 2: Left Arc (R=$RADIUS)"
    ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'arc', target_value: 90.0, speed: $SPEED, radius: $RADIUS}"
done

# つなぎの直線距離: RADIUS * 2 + SCALE
CONN_DIST=$(awk "BEGIN {print $RADIUS * 2 + $SCALE}")
echo "Connecting Straight $CONN_DIST m"
ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $CONN_DIST, speed: $SPEED}"

echo "--- Starting Right Loop ---"
for i in {1..3}
do
    echo "[Right $i/3] Step 1: Moving Straight ($SCALE m)"
    ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $SCALE, speed: $SPEED}"
    
    echo "[Right $i/3] Step 2: Right Arc (R=$RADIUS)"
    ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'arc', target_value: -90.0, speed: $SPEED, radius: $RADIUS}"
done

# 最後の直線距離: RADIUS + SCALE
FINAL_DIST=$(awk "BEGIN {print $RADIUS + $SCALE}")
echo "Final Straight $FINAL_DIST m"
ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $FINAL_DIST, speed: $SPEED}"

echo "=== Open Loop Figure-8 Complete! ==="
