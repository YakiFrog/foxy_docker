#!/bin/bash
# test_cl_square.sh - Square with Variables (Fixed for compatibility)

# --- 設定値 ---
SIDE=1.0       # 正方形の一辺の長さ
RADIUS=0.5     # 角の半径
SPEED=1.0      # 走行速度
P_MODE=0       # 0: YAMLデフォルト
# -------------

echo "=== Closed Loop Rounded Square Start (Side: $SIDE, Radius: $RADIUS) ==="

for j in {1..1}
do
    for i in {1..4}
    do
        echo "[Loop $j, Step $i/4] Step 1: Moving Forward ($SIDE m)"
        ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: $SIDE, speed: $SPEED, p_control_mode: $P_MODE}"
        
        echo "[Loop $j, Step $i/4] Step 2: Arc Turn (R=$RADIUS, -90deg)"
        ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'arc', target_value: -90.0, speed: $SPEED, radius: $RADIUS, p_control_mode: $P_MODE}"
    done
done

echo "=== Closed Loop Rounded Square Complete! ==="
