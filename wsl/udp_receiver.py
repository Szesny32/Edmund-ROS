import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
import cv2
from cv_bridge import CvBridge
import numpy as np
import threading

class StereoUdpReceiver(Node):
    def __init__(self):
        super().__init__('stereo_udp_receiver')
        self.pub_left = self.create_publisher(Image, '/left/image_raw', 10)
        self.pub_right = self.create_publisher(Image, '/right/image_raw', 10)
        self.info_left = self.create_publisher(CameraInfo, '/left/camera_info', 10)
        self.info_right = self.create_publisher(CameraInfo, '/right/camera_info', 10)

        self.bridge = CvBridge()
        self.frame_count = 0
        self.last_frame_count = 0
        udp_url = 'udp://@:1234?overrun_nonfatal=1&fifo_size=50000000'
        self.cap = cv2.VideoCapture(udp_url, cv2.CAP_FFMPEG)
        
        self.lock = threading.Lock()
        self.current_frame = None
        self.running = True
        
        self.get_logger().info('Starting UDP Receiver Thread...')
        self.reader_thread = threading.Thread(target=self._reader_logic)
        self.reader_thread.daemon = True
        self.reader_thread.start()

        self.timer = self.create_timer(0.01, self.timer_callback)
        self.diag_timer = self.create_timer(1.0, self.diagnostics_callback)
        
        self.get_logger().info('Waiting for stereo images on port 1234...')

    def _reader_logic(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                with self.lock:
                    self.current_frame = frame
            else:
                continue

    def get_info(self, now, is_right=False):
        msg = CameraInfo()
        msg.header.stamp = now
        msg.header.frame_id = "camera_link_left"
        msg.width = 640
        msg.height = 480
        msg.k = [500.0, 0.0, 320.0, 0.0, 500.0, 240.0, 0.0, 0.0, 1.0]

        if is_right:
            msg.p = [500.0, 0.0, 320.0, -50.0, 0.0, 500.0, 240.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        else:
            msg.p = [500.0, 0.0, 320.0, 0.0, 0.0, 500.0, 240.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        msg.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        msg.d = [0.0, 0.0, 0.0, 0.0, 0.0]
        return msg

    def diagnostics_callback(self):
        current_fps = self.frame_count - self.last_frame_count
        self.last_frame_count = self.frame_count
        if current_fps == 0:
            self.get_logger().warning('Status: NO SIGNAL (0 FPS) on port 1234')
        else:
            self.get_logger().info(f'Status: OK | FPS: {current_fps}')

    def timer_callback(self):
        frame = None
        with self.lock:
            if self.current_frame is not None:
                frame = self.current_frame.copy()
                self.current_frame = None 

        if frame is not None:
            self.frame_count += 1
            now = self.get_clock().now().to_msg()
            h, w, _ = frame.shape
            half_w = w // 2
            left_img = frame[:, :half_w]
            right_img = frame[:, half_w:]
            try:
                l_msg = self.bridge.cv2_to_imgmsg(left_img, "bgr8")
                r_msg = self.bridge.cv2_to_imgmsg(right_img, "bgr8")       
                l_msg.header.stamp = r_msg.header.stamp = now
                l_msg.header.frame_id = r_msg.header.frame_id = "camera_link_left"
                self.pub_left.publish(l_msg)
                self.pub_right.publish(r_msg)
                self.info_left.publish(self.get_info(now, False))
                self.info_right.publish(self.get_info(now, True))
            except Exception as e:
                self.get_logger().error(f'Processing Error: {str(e)}')

def main():
    rclpy.init()
    node = StereoUdpReceiver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
    finally:
        node.running = False
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()