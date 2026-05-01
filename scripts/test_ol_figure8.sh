#!/bin/bash
# test_ol_figure8.sh - Open Loop Smooth Figure-8 (Straight + Arc)

echo "=== Open Loop Smooth Figure-8 Start ==="

# Loop 1: Left Rounded Square
echo "--- Starting Left Loop ---"
for i in {1..3}
do
    echo "[Left $i/3] Step 1: Straight 1m"
    ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'move', target_value: 1.0, speed: 1.0}"
    
    echo "[Left $i/3] Step 2: Left Arc (R=1.0m, 90deg)"
    ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'arc', target_value: 90.0, speed: 1.0, radius: 1.0}"
done

# 直進
echo "Straight 1m + 1m"
ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'move', target_value: 2.0, speed: 1.0}"

# Loop 2: Right Rounded Square
echo "--- Starting Right Loop ---"
for i in {1..3}
do
    echo "[Right $i/3] Step 1: Straight 1m"
    ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'move', target_value: 1.0, speed: 1.0}"
    
    echo "[Right $i/3] Step 2: Right Arc (R=1.0m, -90deg)"
    ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'arc', target_value: -90.0, speed: 1.0, radius: 1.0}"
done

# 直進
echo "Straight 1m + 1m"
ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'move', target_value: 2.0, speed: 1.0}"

echo "=== Open Loop Smooth Figure-8 Complete! ==="
