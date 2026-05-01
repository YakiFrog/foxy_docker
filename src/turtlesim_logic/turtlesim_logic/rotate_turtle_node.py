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
        self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10,
            callback_group=self.callback_group)
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
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
        
        # Simple P-control logic
        kp = 2.0
        tolerance = 0.02
        
        rate = self.create_rate(10)
        while rclpy.ok():
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
            msg.angular.z = kp * yaw_error
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
