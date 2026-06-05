from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    map_visualizer_node = Node(
        package='ros2_homework_advanced_package',
        executable='map_visualizer_node',
        name='map_visualizer_node',
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-f', 'world']
    )

    return LaunchDescription([
        map_visualizer_node,
        rviz_node
    ])
