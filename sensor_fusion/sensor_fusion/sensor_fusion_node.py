#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, PointCloud2
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile, QoSReliabilityPolicy

import cv2
import numpy as np
import torch
import sensor_msgs_py.point_cloud2 as pc2
from message_filters import Subscriber, ApproximateTimeSynchronizer



class FusionDisplay(Node):
    def __init__(self):
        super().__init__('fusion_display_node')

        qos_profile = QoSProfile(depth=10, reliability=QoSReliabilityPolicy.BEST_EFFORT)

        # Subscribers
        self.image_sub = Subscriber(self, CompressedImage, '/camera', qos_profile=qos_profile)
        self.lidar_sub = Subscriber(self, PointCloud2, '/lidar', qos_profile=qos_profile)
        self.ts = ApproximateTimeSynchronizer([self.image_sub, self.lidar_sub], queue_size=10, slop=0.2)
        self.ts.registerCallback(self.synced_callback)

        self.bridge = CvBridge()
        self.device = select_device('0')
        self.model = None

        self.weights = '/your/weight'


        self.da_seg_mask = None
        self.ll_seg_mask = None
        self.objects = []


        self.frame_count = 0

        self.get_logger().info("Fusion + Display Node Ready ✅")

    def synced_callback(self, img_msg: CompressedImage, lidar_msg: PointCloud2):
        cv_image = self.bridge.compressed_imgmsg_to_cv2(img_msg, "bgr8")
        img_out = self.detect_and_overlay(cv_image, lidar_msg)

        self.frame_count += 1
        if self.frame_count % 5 == 0:
            fname = f"/result/fusion_result_{self.frame_count}.png"
            cv2.imwrite(fname, img_out)
            self.get_logger().info(f"[💾] Saved {fname}")


    # -------------------------------
    # YOLO detect + Overlay
    # -------------------------------
    def detect_and_overlay(self, cv_image, lidar_msg):
        if self.model is None:
            self.model = torch.jit.load(self.weights).to(self.device).half().eval()
            dummy = torch.zeros(1, 3, 320, 320).to(self.device).half()
            with torch.inference_mode():
                self.model(dummy)

        input_size = (320, 320)
        output_size = (1937, 1533)

        img_resized = cv2.resize(cv_image, input_size)
        img_tensor = torch.from_numpy(img_resized).to(self.device).half() / 255.0
        im = img_tensor.permute(2, 0, 1).unsqueeze(0)

        with torch.inference_mode():
            [pred, anchor_grid], seg, ll = self.model(im)

        pred = split_for_trace_model(pred, anchor_grid)
        detections = non_max_suppression(pred, 0.4, 0.5)

        self.objects = []
        for det in detections:
            if len(det):
                for *xyxy, conf, cls in det:
                    x1, y1, x2, y2 = map(int, xyxy)
                    scale_x = output_size[0] / input_size[0]
                    scale_y = output_size[1] / input_size[1]
                    x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
                    y1, y2 = int(y1 * scale_y), int(y2 * scale_y)
                    self.objects.append((x1, y1, x2, y2, conf))

        self.da_seg_mask = driving_area_mask(seg).astype(np.uint8)
        self.ll_seg_mask = lane_line_mask(ll).astype(np.uint8)

        overlay = cv2.resize(cv_image, output_size)
        da_mask_resized = cv2.resize(self.da_seg_mask, output_size, interpolation=cv2.INTER_NEAREST)
        ll_mask_resized = cv2.resize(self.ll_seg_mask, output_size, interpolation=cv2.INTER_NEAREST)

        overlay[da_mask_resized == 1] = (0, 255, 0)     # drivable area: green
        overlay[ll_mask_resized == 1] = (0, 255, 255)   # lane line: yellow

        for (x1, y1, x2, y2, conf) in self.objects:
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 255), 2)

        pts = np.fromiter(
            pc2.read_points(lidar_msg, field_names=("x", "y", "z"), skip_nans=True),
            dtype=[("x", np.float32), ("y", np.float32), ("z", np.float32)]
        )
        if len(pts) > 0:
            points = np.vstack((pts["x"], pts["y"], pts["z"])).T
            xyz_h = np.hstack((points, np.ones((points.shape[0], 1), dtype=np.float32)))
            xyz_cam = (self.T_lidar_to_cam @ xyz_h.T).T[:, :3]

            mask_front = xyz_cam[:, 2] > 0
            xyz_cam = xyz_cam[mask_front]

            proj = (self.K @ xyz_cam.T).T
            proj[:, 0] /= proj[:, 2]
            proj[:, 1] /= proj[:, 2]
            uvs = proj[:, :2].astype(int)

            w, h = output_size
            proj_valid = (uvs[:, 0] >= 0) & (uvs[:, 0] < w) & (uvs[:, 1] >= 0) & (uvs[:, 1] < h)
            uvs = uvs[proj_valid]

            for (u, v) in uvs:
                cv2.circle(overlay, (u, v), 1, (0, 165, 255), -1)

        return overlay


def main(args=None):
    rclpy.init(args=args)
    node = FusionDisplay()
    rclpy.spin(node)
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
