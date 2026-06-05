from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    param_file = PathJoinSubstitution([
        FindPackageShare('ros2_homework_basic_package'),
        'config',
        'turtle_params.yaml'
    ])

    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim',
        output='screen'
    )

    figure8_node = Node(
        package='ros2_homework_basic_package',
        executable='figure8_node',
        name='figure8_node',
        output='screen',
        parameters=[param_file]
    )

    return LaunchDescription([
        turtlesim_node,
        figure8_node
    ])