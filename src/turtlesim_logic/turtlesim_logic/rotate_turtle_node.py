import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from bt_msgs.action import RotateDegrees
import math

class RotateTurtleNode(Node):
    def __init__(self):
        super().__init__('rotate_turtle_node')
        
        # Turtlesim uses /turtle1/pose and /turtle1/cmd_vel
        self.current_yaw = 0.0
        self.callback_group = ReentrantCallbackGroup()
        
        # Declare and get topic parameters
        self.declare_parameter('pose_topic', '/turtle1/pose')
        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        
        pose_topic = self.get_parameter('pose_topic').value
        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value

        self.create_subscription(
            Pose, pose_topic, self.pose_callback, 10,
            callback_group=self.callback_group)
        self.cmd_vel_pub = self.create_publisher(Twist, cmd_vel_topic, 10)
        
        # Declare control parameters
        self.declare_parameter('max_angular_speed', 1.0)
        self.declare_parameter('min_angular_speed', 0.2)
        self.declare_parameter('kp_angular', 2.0)
        self.declare_parameter('tolerance', 0.02)
        
        self._action_server = ActionServer(
            self, RotateDegrees, 'rotate_degrees',
            execute_callback=self.execute_callback,
            callback_group=self.callback_group
        )
        self.get_logger().info('RotateTurtle Node (Foxy) initialized')

    def pose_callback(self, msg):
        # Turtlesim pose.theta is already in radians
        self.current_yaw = msg.theta

    def normalize_angle(self, angle):
        while angle > math.pi: angle -= 2.0 * math.pi
        while angle < -math.pi: angle += 2.0 * math.pi
        return angle

    def execute_callback(self, goal_handle):
        target_deg = goal_handle.request.target_degrees
        self.get_logger().info(f'Rotating turtle by {target_deg} degrees...')
        
        target_offset_rad = math.radians(target_deg)
        target_yaw = self.normalize_angle(self.current_yaw + target_offset_rad)
        
        # 目標速度の取得 (指定がなければ YAML の max_angular_speed)
        goal_speed = goal_handle.request.speed
        max_angular_speed = goal_speed if goal_speed > 0 else self.get_parameter('max_angular_speed').value
        
        kp_angular = self.get_parameter('kp_angular').value
        tolerance = self.get_parameter('tolerance').value
        
        rate = self.create_rate(10)
        while rclpy.ok():
            # Refresh parameters
            max_angular_speed = goal_speed if goal_speed > 0 else self.get_parameter('max_angular_speed').value
            min_angular_speed = self.get_parameter('min_angular_speed').value
            kp_angular = self.get_parameter('kp_angular').value
            tolerance = self.get_parameter('tolerance').value
            yaw_error = self.normalize_angle(target_yaw - self.current_yaw)
            
            # Feedback
            goal_handle.publish_feedback(RotateDegrees.Feedback(
                current_yaw=math.degrees(self.current_yaw),
                status=f"Rotating... Err: {math.degrees(yaw_error):.1f}"
            ))
            
            if abs(yaw_error) < tolerance:
                break
                
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return RotateDegrees.Result(success=False)
            
            msg = Twist()
            raw_w = kp_angular * yaw_error
            w = max(-max_angular_speed, min(max_angular_speed, raw_w))
            if abs(w) < min_angular_speed and abs(yaw_error) > 0.01:
                w = min_angular_speed if w > 0 else -min_angular_speed
            msg.angular.z = w
            self.cmd_vel_pub.publish(msg)
            
            # No await here, but MultiThreadedExecutor will handle pose_callback
            # To be more "async", we could use await asyncio.sleep(0.1)
            # but rate.sleep() in a loop is common in ROS 2.
            # In Foxy, rate.sleep() might block. Let's see if it works.
            time_to_wait = 0.1
            import time
            time.sleep(time_to_wait) # Blocking sleep for simplicity in this test
            
        # Stop
        self.cmd_vel_pub.publish(Twist())
        goal_handle.succeed()
        return RotateDegrees.Result(success=True)

def main(args=None):
    rclpy.init(args=args)
    node = RotateTurtleNode()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
