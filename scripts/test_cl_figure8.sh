#!/bin/bash
# test_cl_figure8.sh - FULL Closed Loop Smooth Figure-8 (YAML Managed)

echo "=== Full Closed Loop Figure-8 Start (Following YAML Defaults) ==="

echo "--- Starting Left Loop ---"
for i in {1..3}
do
    echo "[Left $i/3] Step 1: Moving Straight"
    ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: 1.0, speed: 1.0, p_control_mode: 0}"
    
    echo "[Left $i/3] Step 2: Left Arc"
    ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'arc', target_value: 90.0, speed: 1.0, radius: 1.0, p_control_mode: 0}"
done

echo "Connecting Straight 2m"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: 2.0, speed: 1.0, p_control_mode: 0}"

echo "--- Starting Right Loop ---"
for i in {1..3}
do
    echo "[Right $i/3] Step 1: Moving Straight"
    ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: 1.0, speed: 1.0, p_control_mode: 0}"
    
    echo "[Right $i/3] Step 2: Right Arc"
    ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'arc', target_value: -90.0, speed: 1.0, radius: 1.0, p_control_mode: 0}"
done

echo "Final Straight 2m"
ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: 2.0, speed: 1.0, p_control_mode: 0}"

echo "=== Full Closed Loop Figure-8 Complete! ==="
