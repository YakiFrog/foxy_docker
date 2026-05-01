#!/bin/bash
# test_ol_square.sh - Open Loop Rounded Square

echo "=== Open Loop Rounded Square Start ==="

for j in {1..1}
do
    for i in {1..4}
    do
        echo "[Loop $j, Step $i/4] Step 1: Moving Forward (OL)"
        ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'move', target_value: 2.0, speed: 1.0}"
        
        echo "[Loop $j, Step $i/4] Step 2: Arc Turn (OL, R=0.5m, -90deg)"
        ros2 action send_goal /open_loop_drive bt_msgs/action/Drive "{type: 'arc', target_value: -90.0, speed: 1.0, radius: 0.5}"
    done
done

echo "=== Open Loop Rounded Square Complete! ==="
