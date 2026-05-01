#!/bin/bash
# test_cl_square.sh - Closed Loop Rounded Square (Using YAML Defaults)

echo "=== Closed Loop Rounded Square Start (Following YAML Defaults) ==="

for j in {1..1}
do
    for i in {1..4}
    do
        echo "[Loop $j, Step $i/4] Step 1: Moving Forward"
        ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: 2.0, speed: 1.0, p_control_mode: 0}"
        
        echo "[Loop $j, Step $i/4] Step 2: Arc Turn (R=1.0m, -90deg)"
        ros2 action send_goal /closed_loop_drive bt_msgs/action/Drive "{type: 'arc', target_value: -90.0, speed: 1.0, radius: 1.0, p_control_mode: 0}"
    done
done

echo "=== Closed Loop Rounded Square Complete! ==="
