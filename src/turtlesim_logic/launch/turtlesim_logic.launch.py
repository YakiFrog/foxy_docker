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
            executable='rotate_turtle',
            name='rotate_turtle_node',
            parameters=[config],
            output='screen'
        ),
        Node(
            package='turtlesim_logic',
            executable='move_to_target',
            name='move_to_target_node',
            parameters=[config],
            output='screen'
        ),
        Node(
            package='turtlesim_logic',
            executable='arc_drive',
            name='arc_drive_node',
            parameters=[config],
            output='screen'
        ),
        Node(
            package='turtlesim_logic',
            executable='open_loop_drive',
            name='open_loop_drive_node',
            parameters=[config],
            output='screen'
        )
    ])
