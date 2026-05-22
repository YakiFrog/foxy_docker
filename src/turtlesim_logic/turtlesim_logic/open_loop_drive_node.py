import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import time
import math

from geometry_msgs.msg import Twist
from bt_msgs.action import Drive

class OpenLoopDriveNode(Node):
    def __init__(self):
        super().__init__('open_loop_drive_node')
        
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 1.0)
        
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.publisher_ = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        
        self._action_server = ActionServer(
            self, Drive, 'open_loop_drive',
            execute_callback=self.execute_callback,
            callback_group=ReentrantCallbackGroup()
        )
        self.get_logger().info('Pure OpenLoopDrive Node Started (Using Drive Action)')

    async def execute_callback(self, goal_handle):
        drive_type = goal_handle.request.type
        target_value = goal_handle.request.target_value
        speed = abs(goal_handle.request.speed)
        radius = abs(goal_handle.request.radius)
        
        # デフォルト速度の設定
        if speed <= 0.0:
            speed = abs(self.get_parameter('linear_speed').value) if drive_type != 'rotate' else abs(self.get_parameter('angular_speed').value)

        msg = Twist()
        duration = 0.0

        # --- ステップ1: 目標移動量と速度から、動作させる秒数(duration)を計算 ---
        if drive_type == "move":
            # 距離 / 速度 = 秒数
            duration = abs(target_value) / speed
            msg.linear.x = float(speed if target_value > 0 else -speed)
        elif drive_type == "rotate":
            # 角度(ラジアン) / 角速度 = 秒数
            duration = abs(math.radians(target_value)) / speed
            msg.angular.z = float(speed if target_value > 0 else -speed)
        elif drive_type == "arc":
            # 円弧の長さ / 速度 = 秒数
            # (円弧の角度(rad) * 半径) / 速度 = 秒数
            duration = (abs(math.radians(target_value)) * radius) / speed
            msg.linear.x = float(speed)
            w = speed / radius
            msg.angular.z = float(w if target_value > 0 else -w)

        self.get_logger().info(f'Starting {drive_type}: duration={duration:.2f}s')

        start_time = self.get_clock().now()
        rate = self.create_rate(100) # 100Hz (0.01秒ごとにループ)

        # --- ステップ2: 計算された秒数が経過するまでループ ---
        while rclpy.ok():
            elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
            
            # ステップ3: 経過時間が duration に達したらループを抜ける
            if elapsed >= duration:
                break
            
            if goal_handle.is_cancel_requested:
                self.stop_turtle()
                goal_handle.canceled()
                return Drive.Result(success=False)

            # ステップ4: 一定速度の指令(Twist)をパブリッシュし続ける
            self.publisher_.publish(msg)
            rate.sleep()

        # ステップ5: 終了したら速度を0にして停止させる
        self.stop_turtle()
        goal_handle.succeed()
        return Drive.Result(success=True)

    def stop_turtle(self):
        self.publisher_.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    node = OpenLoopDriveNode()
    rclpy.spin(node, executor=MultiThreadedExecutor())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
