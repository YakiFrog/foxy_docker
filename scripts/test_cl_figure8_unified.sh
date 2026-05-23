#!/bin/bash
# test_cl_figure8_unified.sh - Send unified Closed-Loop Figure-8 action goal

# --- 設定値 ---
SCALE=5.0      # 直進部分の基本単位
RADIUS=2.5     # 円弧の半径
SPEED=1.0      # 走行速度
P_MODE=0       # 0: YAMLデフォルト
# --------------

echo "=== Sending Unified Closed Loop Figure-8 Action Goal (Scale: $SCALE, Radius: $RADIUS, Speed: $SPEED) ==="
ros2 action send_goal /closed_loop_figure_eight bt_msgs/action/FigureEight "{scale: $SCALE, radius: $RADIUS, speed: $SPEED, p_control_mode: $P_MODE}"
