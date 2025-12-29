from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='v2x_recognition_converter',
            executable='v2x_recognition_converter_node',
            name='v2x_recognition_converter',
            parameters=[{
                'vehicle_id': 1
            }]
        )
    ])
