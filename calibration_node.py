import rclpy
from rclpy.node import Node

import cv2
import yaml
import numpy as np

from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class CalibrationNode(Node):
    def __init__(self):
        super().__init__('calibration_node')

        self.publisher_ = self.create_publisher(Image, 'corrected_image', 10)
        self.bridge = CvBridge()

        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        if self.cap.isOpened():
            self.get_logger().info("Camera opened successfully")
        else:
            self.get_logger().error("Camera failed to open")

        # Load calibration file
        calibration_file = "/home/rgstech002/camera_calibration_project/camera_calibration.yaml"

        try:
            with open(calibration_file, "r") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

            self.camera_matrix = np.array(data["camera_matrix"], dtype=np.float32)
            self.dist_coeffs = np.array(data["distortion_coefficients"], dtype=np.float32)

            self.get_logger().info("Calibration YAML loaded successfully")

        except Exception as e:
            self.get_logger().error(f"Failed to load calibration YAML: {e}")
            self.camera_matrix = None
            self.dist_coeffs = None

        self.timer = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().warning("Frame not received")
            return

        #self.get_logger().info("Frame received")

        if self.camera_matrix is not None and self.dist_coeffs is not None:
            corrected_frame = cv2.undistort(
                frame,
                self.camera_matrix,
                self.dist_coeffs
            )
        else:
            corrected_frame = frame

        msg = self.bridge.cv2_to_imgmsg(corrected_frame, encoding="bgr8")
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_frame"

        self.publisher_.publish(msg)
        #self.get_logger().info("Published corrected image")


def main(args=None):
    rclpy.init(args=args)

    node = CalibrationNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.cap.release()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()