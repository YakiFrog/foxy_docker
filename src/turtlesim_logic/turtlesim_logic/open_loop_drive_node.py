import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import math
import time

from geometry_msgs.msg import Twist
from bt_msgs.action import OpenLoopDrive

class OpenLoopDriveNode(Node):
    def __init__(self):
        super().__init__('open_loop_drive_node')
        
        # パラメータ設定
        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 1.0)
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value

        self.callback_group = ReentrantCallbackGroup()
        
        # パブリッシャ (サブスクライバは不要！)
        self.publisher_ = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        
        self._action_server = ActionServer(
            self,
            OpenLoopDrive,
            'open_loop_drive',
            execute_callback=self.execute_callback,
            callback_group=self.callback_group,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback
        )
        
        self.get_logger().info('OpenLoopDrive Action Server (Odometry-Free) started')

    def goal_callback(self, goal_request):
        self.get_logger().info(f'Received OpenLoop goal: type={goal_request.type}, value={goal_request.target_value}')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received cancel request')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        drive_type = goal_handle.request.type
        target_value = goal_handle.request.target_value
        speed = abs(goal_handle.request.speed)
        
        # 時間の計算 (オープンループ制御の核心)
        if drive_type == "rotate":
            # 目標速度の決定 (Goalで0が指定された場合は YAML パラメータを使用)
            if speed <= 0:
                speed = abs(self.get_parameter('angular_speed').value)
                self.get_logger().info(f'Using default angular_speed: {speed}')
            
            # 走行時間(秒) = 回転角度(rad) / 角速度(rad/s)
            # math.radians() で度(deg)からラジアン(rad)に変換
            duration = abs(math.radians(target_value) / speed)
            
            msg = Twist()
            # 目標角度(target_value)の符号で、左回転(+)か右回転(-)かを判断
            msg.angular.z = float(speed if target_value > 0 else -speed)
            self.get_logger().info(f'Rotating {target_value} degrees at {speed} rad/s (Duration: {duration:.2f}s)')
        
        elif drive_type == "move":
            # 目標速度の決定 (Goalで0が指定された場合は YAML パラメータを使用)
            if speed <= 0:
                speed = abs(self.get_parameter('linear_speed').value)
                self.get_logger().info(f'Using default linear_speed: {speed}')
            
            # 走行時間(秒) = 移動距離(m) / 速度(m/s)
            duration = abs(target_value / speed)
            
            msg = Twist()
            # 目標距離(target_value)の符号で、前進(+)か後退(-)かを判断
            msg.linear.x = float(speed if target_value > 0 else -speed)
            self.get_logger().info(f'Moving {target_value} meters at {speed} m/s (Duration: {duration:.2f}s)')
        
        elif drive_type == "arc":
            # 目標速度の決定
            if speed <= 0:
                speed = abs(self.get_parameter('linear_speed').value)
            
            radius = abs(goal_handle.request.radius)
            if radius <= 0:
                self.get_logger().error('Radius must be positive for arc drive')
                goal_handle.abort()
                return OpenLoopDrive.Result(success=False)
            
            # 走行時間(秒) = 弧の長さ(m) / 速度(m/s)
            # 弧の長さ = 半径 * 中心角(rad)
            target_angle_rad = abs(math.radians(target_value))
            duration = (radius * target_angle_rad) / speed
            
            # 角速度 w = v / R
            angular_speed = speed / radius
            
            msg = Twist()
            msg.linear.x = float(speed)
            # 目標角度の符号で、左旋回か右旋回かを決定
            msg.angular.z = float(angular_speed if target_value > 0 else -angular_speed)
            self.get_logger().info(f'Arc driving: Radius {radius}m, Angle {target_value}deg (Duration: {duration:.2f}s)')
        
        else:
            self.get_logger().error(f'Unknown drive type: {drive_type}')
            goal_handle.abort()
            return OpenLoopDrive.Result(success=False)

        # 制御開始時刻を記録
        start_time = self.get_clock().now()
        feedback_msg = OpenLoopDrive.Feedback()
        
        rate = self.create_rate(20) # 20Hz (0.05秒に1回コマンドを送信)
        
        try:
            # 現在時刻と開始時刻の差(経過時間)が、計算した duration に達するまでループ
            while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    self.stop_turtle()
                    return OpenLoopDrive.Result(success=False)
                
                # フィードバック更新
                feedback_msg.elapsed_time = (self.get_clock().now() - start_time).nanoseconds / 1e9
                goal_handle.publish_feedback(feedback_msg)
                
                # 指令送信
                self.publisher_.publish(msg)
                rate.sleep()
                
            self.stop_turtle()
            goal_handle.succeed()
            self.get_logger().info('Open loop drive completed')
            return OpenLoopDrive.Result(success=True)
            
        except Exception as e:
            self.get_logger().error(f'Error: {str(e)}')
            self.stop_turtle()
            goal_handle.abort()
            return OpenLoopDrive.Result(success=False)

    def stop_turtle(self):
        self.publisher_.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    node = OpenLoopDriveNode()
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
