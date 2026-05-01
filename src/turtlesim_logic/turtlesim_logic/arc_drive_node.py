import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import math
import time

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from bt_msgs.action import ArcDrive

class ArcDriveNode(Node):
    def __init__(self):
        super().__init__('arc_drive_node')
        
        # パラメータ設定
        self.declare_parameter('pose_topic', '/turtle1/pose')
        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        self.declare_parameter('linear_speed', 1.0)
        
        self.pose_topic = self.get_parameter('pose_topic').value
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value

        self.callback_group = ReentrantCallbackGroup()
        
        # パブリッシャとサブスクライバ
        self.publisher_ = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        self.subscription = self.create_subscription(
            Pose,
            self.pose_topic,
            self.pose_callback,
            10,
            callback_group=self.callback_group)
        
        self._action_server = ActionServer(
            self,
            ArcDrive,
            'arc_drive',
            execute_callback=self.execute_callback,
            callback_group=self.callback_group,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )
        
        self.current_pose = None
        self.get_logger().info('ArcDrive Action Server started')

    def pose_callback(self, msg):
        self.current_pose = msg

    def goal_callback(self, goal_request):
        self.get_logger().info(f'Received goal: radius={goal_request.radius}, angle={goal_request.angle_degrees}')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.get_logger().info('Executing arc drive...')
        
        target_radius = goal_handle.request.radius
        target_angle_deg = goal_handle.request.angle_degrees
        
        # 目標値が0以下の場合は YAML パラメータを使用
        linear_speed = goal_handle.request.linear_speed
        if linear_speed <= 0:
            linear_speed = self.get_parameter('linear_speed').value
            self.get_logger().info(f'Using default linear_speed from parameter: {linear_speed}')
        
        if target_radius <= 0:
            self.get_logger().error('Radius must be positive')
            goal_handle.abort()
            return ArcDrive.Result(success=False)

        # 初期位置の待機
        while self.current_pose is None:
            self.get_logger().info('Waiting for pose...')
            time.sleep(0.1)

        start_theta = self.current_pose.theta
        accumulated_angle = 0.0
        last_theta = start_theta
        
        # 角速度の計算 w = v / R
        # 角度が負なら右回転なので w も負にする
        angular_speed = abs(linear_speed / target_radius)
        if target_angle_deg < 0:
            angular_speed = -angular_speed
        
        target_angle_rad = abs(math.radians(target_angle_deg))
        
        msg = Twist()
        msg.linear.x = float(linear_speed)
        msg.angular.z = float(angular_speed)
        
        result = ArcDrive.Result()
        feedback_msg = ArcDrive.Feedback()
        
        rate = self.create_rate(20) # 20Hz
        
        try:
            while abs(accumulated_angle) < target_angle_rad:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    self.stop_turtle()
                    return ArcDrive.Result(success=False)
                
                # 回転量の計算 (180度跨ぎを考慮)
                diff = self.current_pose.theta - last_theta
                if diff > math.pi: diff -= 2*math.pi
                if diff < -math.pi: diff += 2*math.pi
                
                accumulated_angle += diff
                last_theta = self.current_pose.theta
                
                # フィードバック送信
                feedback_msg.current_angle_degrees = math.degrees(accumulated_angle)
                goal_handle.publish_feedback(feedback_msg)
                
                # 速度コマンド送信
                self.publisher_.publish(msg)
                
                rate.sleep()
                
            self.stop_turtle()
            goal_handle.succeed()
            result.success = True
            self.get_logger().info('Arc drive completed successfully')
            
        except Exception as e:
            self.get_logger().error(f'Error during execution: {str(e)}')
            self.stop_turtle()
            goal_handle.abort()
            result.success = False
            
        return result

    def stop_turtle(self):
        msg = Twist()
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ArcDriveNode()
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
