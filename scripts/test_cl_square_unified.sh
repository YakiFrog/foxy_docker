#!/bin/bash
# test_cl_square_unified.sh - Send unified Closed-Loop Rounded Square action goal

# --- 設定値 ---
SIDE=1.0       # 正方形の一辺の長さ
RADIUS=0.5     # 角の半径
SPEED=1.0      # 走行速度
P_MODE=0       # 0: YAMLデフォルト
# -------------

echo "=== Sending Unified Closed Loop Rounded Square Action Goal (Side: $SIDE, Radius: $RADIUS, Speed: $SPEED) ==="
ros2 action send_goal /closed_loop_square bt_msgs/action/Square "{side: $SIDE, radius: $RADIUS, speed: $SPEED, p_control_mode: $P_MODE}"
