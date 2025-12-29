from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='republish_image',
            executable='fast_republish_yaml_node',
            name='fast_yaml_leftfront',
            output='screen',
            parameters=[{
                'in_image_compressed': '/camera_fl/image_raw/compressed',
                'out_image_raw':       '/left/image_raw',
                'out_camera_info':     '/left/camera_info',
                'resize_width':  0,   # 필요 시 1920 등 지정
                'resize_height': 0,
                'yaml_path': '/path/to/cameras.yaml',
                'yaml_camera_key': 'LeftFront',          # ⇦ YAML 키 (예: RightFront, MiddleLeft …)
                'frame_id_override': ''                   # 비우면 입력 이미지 frame_id 사용
            }],
        )
    ])
