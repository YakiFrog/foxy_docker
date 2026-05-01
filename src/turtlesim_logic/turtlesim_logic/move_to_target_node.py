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
        
        self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10,
            callback_group=self.callback_group)
        
        self.cmd_vel_pub = self.create_publisher(
            Twist, '/turtle1/cmd_vel', 10)
        
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
        self.get_logger().info(f'Goal received: Move to ({target_x}, {target_y})')

        kp_linear = 1.0
        kp_angular = 4.0
        dist_tolerance = 0.1
        yaw_tolerance = 0.05
        
        while rclpy.ok():
            # Calculate distance and angle to target
            dx = target_x - self.current_x
            dy = target_y - self.current_y
            dist = math.sqrt(dx**2 + dy**2)
            angle_to_target = math.atan2(dy, dx)
            
            # Yaw error
            yaw_error = self.normalize_angle(angle_to_target - self.current_yaw)
            
            # Feedback
            goal_handle.publish_feedback(MoveToTarget.Feedback(
                distance=dist,
                status=f"Dist: {dist:.2f}, YawErr: {math.degrees(yaw_error):.1f}"
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
                msg.angular.z = kp_angular * yaw_error
                msg.linear.x = 0.0
            else:
                # Move forward while adjusting angle
                msg.linear.x = min(2.0, kp_linear * dist)
                msg.angular.z = kp_angular * yaw_error
                
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
