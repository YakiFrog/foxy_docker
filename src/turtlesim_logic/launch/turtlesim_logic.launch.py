import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # YAML ファイルのパスを取得
    config = os.path.join(
        get_package_share_directory('turtlesim_logic'),
        'config',
        'turtlesim_params.yaml'
    )

    return LaunchDescription([
        Node(
            package='turtlesim_logic',
            executable='open_loop_drive',
            name='open_loop_drive_node',
            parameters=[config],
            output='screen'
        ),
        Node(
            package='turtlesim_logic',
            executable='closed_loop_drive',
            name='closed_loop_drive_node',
            parameters=[config],
            output='screen'
        ),
        Node(
            package='turtlesim_logic',
            executable='open_loop_shape',
            name='open_loop_shape_node',
            parameters=[config],
            output='screen'
        ),
        Node(
            package='turtlesim_logic',
            executable='closed_loop_shape',
            name='closed_loop_shape_node',
            parameters=[config],
            output='screen'
        )
    ])
