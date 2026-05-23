#!/bin/bash
# test_ol_square_unified.sh - Send unified Open-Loop Rounded Square action goal

# --- 設定値 ---
SIDE=5.0       # 一辺の長さ
RADIUS=2.5     # 角の半径
SPEED=1.0      # 走行速度
# --------------

echo "=== Sending Unified Open Loop Rounded Square Action Goal (Side: $SIDE, Radius: $RADIUS, Speed: $SPEED) ==="
ros2 action send_goal /open_loop_square bt_msgs/action/Square "{side: $SIDE, radius: $RADIUS, speed: $SPEED, p_control_mode: 0}"
