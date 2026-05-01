import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from bt_msgs.action import MoveToTarget
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math
import time

class FoxyRotateServer(Node):
    def __init__(self):
        super().__init__('foxy_rotate_server')
        self.callback_group = ReentrantCallbackGroup()
        
        self._action_server = ActionServer(
            self,
            MoveToTarget,
            'MoveToTarget',
            execute_callback=self.execute_callback,
            callback_group=self.callback_group)
        
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10,
            callback_group=self.callback_group)
        
        self.current_yaw = 0.0
        self.get_logger().info('Foxy Action Server (90deg Rotate Test) Started.')

    def pose_callback(self, msg):
        self.current_yaw = msg.theta

    def execute_callback(self, goal_handle):
        self.get_logger().info('Goal received! Rotating 90 degrees (approx 1.57 rad)...')
        
        # Target is current + 90 degrees
        target_yaw = self.current_yaw + 1.5708
        # Normalize to -pi to pi
        target_yaw = math.atan2(math.sin(target_yaw), math.cos(target_yaw))
        
        feedback_msg = MoveToTarget.Feedback()
        
        while True:
            # Calculate error
            error = target_yaw - self.current_yaw
            error = math.atan2(math.sin(error), math.cos(error))
            
            if abs(error) < 0.02:
                break
                
            # Publish velocity
            msg = Twist()
            msg.angular.z = 0.5 if error > 0 else -0.5
            self.publisher_.publish(msg)
            
            # Send feedback
            feedback_msg.status = f"Remaining: {abs(error):.2f} rad"
            goal_handle.publish_feedback(feedback_msg)
            
            time.sleep(0.1)

        # Stop
        self.publisher_.publish(Twist())
        
        goal_handle.succeed()
        result = MoveToTarget.Result()
        result.success = True
        self.get_logger().info('Goal Reached!')
        return result

def main(args=None):
    rclpy.init(args=args)
    node = FoxyRotateServer()
    # MultiThreadedExecutor is the key for Foxy!
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
