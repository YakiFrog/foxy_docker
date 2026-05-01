import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim_logic',
            executable='rotate_turtle',
            name='rotate_turtle_node',
            output='screen'
        ),
        Node(
            package='turtlesim_logic',
            executable='move_to_target',
            name='move_to_target_node',
            output='screen'
        )
    ])
