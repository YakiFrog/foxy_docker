cmake_minimum_required(VERSION 3.8)
project(bt_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(action_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/MoveToTarget.action"
  "action/RotateDegrees.action"
  "action/ArcDrive.action"
  DEPENDENCIES action_msgs
)

ament_package()
