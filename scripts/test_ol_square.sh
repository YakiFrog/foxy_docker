#!/bin/bash
# test_ol_square.sh - Open Loop Square Sequence

echo "=== Open Loop Square Sequence Start ==="
for j in {1..3}
do
for i in {1..4}
do
    echo "[$i/4] Step 1: Moving Forward (Open Loop)"
    ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'move', target_value: 2.0, speed: 1.0}"
    
    echo "[$i/4] Step 2: Rotating 90 Degrees (Open Loop)"
    ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'rotate', target_value: -90.0, speed: 1.0}"
done
done
echo "=== Open Loop Square Sequence Complete! ==="
