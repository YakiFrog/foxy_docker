import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from bt_msgs.action import MoveToTarget
import math
import time

class MoveToTargetNode(Node):
    def __init__(self):
        super().__init__('move_to_target_node')
        
        self.callback_group = ReentrantCallbackGroup()
        
        # Turtlesim specific settings
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        
        # Declare and get topic parameters
        self.declare_parameter('pose_topic', '/turtle1/pose')
        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        
        pose_topic = self.get_parameter('pose_topic').value
        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        
        # Declare control parameters
        self.declare_parameter('max_linear_speed', 1.0)
        self.declare_parameter('min_linear_speed', 0.2)
        self.declare_parameter('max_angular_speed', 1.0)
        self.declare_parameter('min_angular_speed', 0.2)
        self.declare_parameter('kp_linear', 1.0)
        self.declare_parameter('kp_angular', 4.0)
        self.declare_parameter('dist_tolerance', 0.1)
        self.declare_parameter('yaw_tolerance', 0.05)
        
        self.create_subscription(
            Pose, pose_topic, self.pose_callback, 10,
            callback_group=self.callback_group)
        
        self.cmd_vel_pub = self.create_publisher(
            Twist, cmd_vel_topic, 10)
        
        self._action_server = ActionServer(
            self, MoveToTarget, 'move_to_target',
            execute_callback=self.execute_callback,
            callback_group=self.callback_group
        )
        
        self.get_logger().info('MoveToTarget Node (Foxy/Turtlesim) initialized')

    def pose_callback(self, msg):
        self.current_x = msg.x
        self.current_y = msg.y
        self.current_yaw = msg.theta

    def normalize_angle(self, angle):
        while angle > math.pi: angle -= 2.0 * math.pi
        while angle < -math.pi: angle += 2.0 * math.pi
        return angle

    def execute_callback(self, goal_handle):
        target_x = goal_handle.request.x
        target_y = goal_handle.request.y
        
        # 目標速度の取得 (指定がなければ YAML の max_linear_speed)
        goal_speed = goal_handle.request.speed
        max_linear_speed = goal_speed if goal_speed > 0 else self.get_parameter('max_linear_speed').value
        
        self.get_logger().info(f'Moving to ({target_x}, {target_y}) with max speed {max_linear_speed}')

        # Get parameters from YAML/Parameters
        min_linear_speed = self.get_parameter('min_linear_speed').value
        max_angular_speed = self.get_parameter('max_angular_speed').value
        min_angular_speed = self.get_parameter('min_angular_speed').value
        kp_linear = self.get_parameter('kp_linear').value
        kp_angular = self.get_parameter('kp_angular').value
        dist_tolerance = self.get_parameter('dist_tolerance').value
        yaw_tolerance = self.get_parameter('yaw_tolerance').value

        while rclpy.ok():
            # Refresh parameters in loop for real-time tuning
            max_linear_speed = goal_speed if goal_speed > 0 else self.get_parameter('max_linear_speed').value
            min_linear_speed = self.get_parameter('min_linear_speed').value
            max_angular_speed = self.get_parameter('max_angular_speed').value
            min_angular_speed = self.get_parameter('min_angular_speed').value
            kp_linear = self.get_parameter('kp_linear').value
            kp_angular = self.get_parameter('kp_angular').value
            dist_tolerance = self.get_parameter('dist_tolerance').value
            yaw_tolerance = self.get_parameter('yaw_tolerance').value
            # Calculate distance and angle to target
            dx = target_x - self.current_x
            dy = target_y - self.current_y
            dist = math.sqrt(dx**2 + dy**2)
            angle_to_target = math.atan2(dy, dx)
            
            # Yaw error
            yaw_error = self.normalize_angle(angle_to_target - self.current_yaw)
            
            # Feedback
            goal_handle.publish_feedback(MoveToTarget.Feedback(
                distance_to_target=dist
            ))
            
            # Check if reached
            if dist < dist_tolerance:
                break
                
            if goal_handle.is_cancel_requested:
                self.cmd_vel_pub.publish(Twist())
                goal_handle.canceled()
                return MoveToTarget.Result(success=False)

            msg = Twist()
            # If yaw error is large, rotate first (like Jazzy version)
            if abs(yaw_error) > 0.2:
                raw_w = kp_angular * yaw_error
                # Clamp Max
                w = max(-max_angular_speed, min(max_angular_speed, raw_w))
                # Apply Min
                if abs(w) < min_angular_speed:
                    w = min_angular_speed if w > 0 else -min_angular_speed
                msg.angular.z = w
                msg.linear.x = 0.0
            else:
                # Move forward while adjusting angle
                raw_v = kp_linear * dist
                v = max(0.0, min(max_linear_speed, raw_v))
                if v > 0 and v < min_linear_speed:
                    v = min_linear_speed
                msg.linear.x = v
                
                raw_w = kp_angular * yaw_error
                w = max(-max_angular_speed, min(max_angular_speed, raw_w))
                if abs(w) < min_angular_speed and abs(yaw_error) > 0.01:
                    w = min_angular_speed if w > 0 else -min_angular_speed
                msg.angular.z = w
                
            self.cmd_vel_pub.publish(msg)
            time.sleep(0.1)

        # Stop
        self.cmd_vel_pub.publish(Twist())
        goal_handle.succeed()
        self.get_logger().info('Goal Reached!')
        return MoveToTarget.Result(success=True)

def main(args=None):
    rclpy.init(args=args)
    node = MoveToTargetNode()
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
