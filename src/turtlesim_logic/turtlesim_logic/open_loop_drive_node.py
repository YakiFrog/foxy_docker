import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import math
import time

from geometry_msgs.msg import Twist
from bt_msgs.action import Drive

class OpenLoopDriveNode(Node):
    """
    オープンループ（時間制御）専用ノード
    オドメトリを一切使用せず、計算した時間だけコマンドを送信します。
    """
    def __init__(self):
        super().__init__('open_loop_drive_node')
        
        # パラメータ設定
        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 1.0)
        
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.callback_group = ReentrantCallbackGroup()
        self.publisher_ = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        
        self._action_server = ActionServer(
            self, Drive, 'open_loop_drive',
            execute_callback=self.execute_callback,
            callback_group=self.callback_group,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )
        self.get_logger().info('Pure OpenLoopDrive Node Started (Using Drive Action)')

    def goal_callback(self, goal_request):
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        drive_type = goal_handle.request.type
        target_value = goal_handle.request.target_value
        speed = abs(goal_handle.request.speed)
        
        try:
            # 時間の計算
            if drive_type == "rotate":
                if speed <= 0: speed = abs(self.get_parameter('angular_speed').value)
                duration = abs(math.radians(target_value) / speed)
                msg = Twist()
                msg.angular.z = float(speed if target_value > 0 else -speed)
            elif drive_type == "move":
                if speed <= 0: speed = abs(self.get_parameter('linear_speed').value)
                duration = abs(target_value / speed)
                msg = Twist()
                msg.linear.x = float(speed if target_value > 0 else -speed)
            elif drive_type == "arc":
                if speed <= 0: speed = abs(self.get_parameter('linear_speed').value)
                radius = abs(goal_handle.request.radius)
                duration = abs(math.radians(target_value) * radius / speed)
                msg = Twist()
                msg.linear.x = float(speed)
                msg.angular.z = float((speed/radius) if target_value > 0 else -(speed/radius))
            else:
                self.get_logger().error(f'Unknown type: {drive_type}')
                goal_handle.abort()
                return Drive.Result(success=False)

            self.get_logger().info(f'OL {drive_type}: Duration {duration:.2f}s')
            
            start_time = self.get_clock().now()
            feedback_msg = Drive.Feedback()
            rate = self.create_rate(100)
            
            while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
                if goal_handle.is_cancel_requested:
                    self.stop_turtle()
                    goal_handle.canceled()
                    return Drive.Result(success=False)
                
                # フィードバック更新
                feedback_msg.elapsed_time = (self.get_clock().now() - start_time).nanoseconds / 1e9
                goal_handle.publish_feedback(feedback_msg)
                
                self.publisher_.publish(msg)
                rate.sleep()

            self.stop_turtle()
            goal_handle.succeed()
            return Drive.Result(success=True)

        except Exception as e:
            self.get_logger().error(f'Error: {str(e)}')
            self.stop_turtle()
            goal_handle.abort()
            return Drive.Result(success=False)

    def stop_turtle(self):
        self.publisher_.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    node = OpenLoopDriveNode()
    rclpy.spin(node, executor=MultiThreadedExecutor())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
