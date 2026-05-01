#!/bin/bash
# test_ol_square.sh - Open Loop Rounded Square with Variables

# --- 設定値 ---
SIDE=1.0       # 一辺の長さ
RADIUS=0.5     # 角の半径
SPEED=1.0      # 走行速度
# --------------

echo "=== Open Loop Rounded Square Start (Side: $SIDE, Radius: $RADIUS) ==="

for j in {1..1}
do
    for i in {1..4}
    do
        echo "[Loop $j, Step $i/4] Step 1: Moving Forward ($SIDE m)"
        ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $SIDE, speed: $SPEED}"
        
        echo "[Loop $j, Step $i/4] Step 2: Arc Turn (R=$RADIUS, -90deg)"
        ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'arc', target_value: -90.0, speed: $SPEED, radius: $RADIUS}"
    done
done

echo "=== Open Loop Rounded Square Complete! ==="
