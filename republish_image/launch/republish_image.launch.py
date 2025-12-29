from launch import LaunchDescription
from launch_ros.actions import Node

def inst(name, in_img, out_ns, yaml_key):
    return Node(
        package='republish_image',
        executable='fast_republish_yaml_node',
        name=f'fast_yaml_{name}',
        output='screen',
        parameters=[{
            'in_image_compressed': in_img,
            'out_image_raw':       f'/{out_ns}/image_raw',
            'out_camera_info':     f'/{out_ns}/camera_info',
            'resize_width':  640,
            'resize_height': 480,
            'yaml_path': '/path/to/cameras.yaml',
            'yaml_camera_key': yaml_key,
            'frame_id_override': ''
        }],
    )

def generate_launch_description():
    nodes = [
        # inst('lf', '/camera_lf/image_raw/compressed', 'camera_lf', 'MiddleLeft'),
        # inst('rf', '/camera_rf/image_raw/compressed', 'camera_rf', 'MiddleRight'),
        inst('fl', '/camera_fl/image_raw/compressed', 'left',      'LeftFront'),
        inst('fr', '/camera_fr/image_raw/compressed', 'right',     'RightFront'),
        # inst('lb', '/camera_lb/image_raw/compressed', 'camera_lb', 'LeftBack'),
        # inst('rb', '/camera_rb/image_raw/compressed', 'camera_rb', 'RightBack'),
    ]
    return LaunchDescription(nodes)
