import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import String

from cv_bridge import CvBridge


class MeasurementNode(Node):

    def __init__(self):
        super().__init__('measurement_node')

        self.bridge = CvBridge()

        # Subscriber
        self.subscription = self.create_subscription(
            Image,
            '/corrected_image',
            self.image_callback,
            10
        )

        # Publisher
        self.publisher_ = self.create_publisher(
            String,
            '/measurement_result',
            10
        )

        self.get_logger().info("Measurement Node Started")

    def image_callback(self, msg):

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        height, width, _ = frame.shape

        result_text = f"Image Size: {width}x{height}"

        result_msg = String()
        result_msg.data = result_text

        self.publisher_.publish(result_msg)

        self.get_logger().info(result_text)


def main(args=None):

    rclpy.init(args=args)

    node = MeasurementNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()