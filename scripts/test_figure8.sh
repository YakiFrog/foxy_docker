#!/bin/bash
# test_figure8.sh - FULL Closed Loop Smooth Figure-8 (Odometry ON)

echo "=== Full Closed Loop Figure-8 Start ==="
echo "Note: Make sure launch_all is running and use_odometry: true is set in YAML."

# 1. 最初の直進 (座標 5.5, 5.5 からスタートと仮定して、相対的に進む)
# 実際には現在の Turtlesim の座標を確認して送るのがベストですが、
# ここでは「指定した座標へ正確に向かう」MoveToTarget の特性を活かします。

echo "--- Starting Left Loop ---"
for i in {1..3}
do
    echo "[Left $i/3] Step 1: Moving Straight (CL)"
    # ここでは便宜上、現在の場所から正確に 1m 進む動作を期待
    # 本来は現在の座標 + 向きから計算が必要ですが、一旦 open_loop_drive の CLモードを使用します
    ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'move', target_value: 1.0, speed: 1.0}"
    
    echo "[Left $i/3] Step 2: Left Arc (CL + P-control)"
    ros2 action send_goal /arc_drive bt_msgs/action/ArcDrive "{radius: 1.0, angle_degrees: 90.0, linear_speed: 1.0}"
done

echo "Connecting Straight 2m (CL)"
ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'move', target_value: 2.0, speed: 1.0}"

echo "--- Starting Right Loop ---"
for i in {1..3}
do
    echo "[Right $i/3] Step 1: Moving Straight (CL)"
    ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'move', target_value: 1.0, speed: 1.0}"
    
    echo "[Right $i/3] Step 2: Right Arc (CL + P-control)"
    ros2 action send_goal /arc_drive bt_msgs/action/ArcDrive "{radius: 1.0, angle_degrees: -90.0, linear_speed: 1.0}"
done

echo "Final Straight 2m (CL)"
ros2 action send_goal /open_loop_drive bt_msgs/action/OpenLoopDrive "{type: 'move', target_value: 2.0, speed: 1.0}"

echo "=== Full Closed Loop Figure-8 Complete! ==="
