#!/bin/bash
# test_ol_figure8_unified.sh - Send unified Open-Loop Figure-8 action goal

# --- 設定値 ---
SCALE=1.0      # 基本単位
RADIUS=0.5     # 円弧の半径
SPEED=1.0      # 走行速度
# --------------

echo "=== Sending Unified Open Loop Figure-8 Action Goal (Scale: $SCALE, Radius: $RADIUS, Speed: $SPEED) ==="
ros2 action send_goal /open_loop_figure_eight bt_msgs/action/FigureEight "{scale: $SCALE, radius: $RADIUS, speed: $SPEED, p_control_mode: 0}"
