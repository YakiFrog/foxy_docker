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
        self.declare_parameter('kp_arc', 2.0)
        self.declare_parameter('use_odometry', True) # 切り替えスイッチ
        
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
        target_radius = goal_handle.request.radius
        target_angle_deg = goal_handle.request.angle_degrees
        
        # 目標速度の取得
        linear_speed = goal_handle.request.linear_speed
        if linear_speed <= 0:
            linear_speed = self.get_parameter('linear_speed').value
            
        use_odom = self.get_parameter('use_odometry').value
        
        if target_radius <= 0:
            self.get_logger().error('Radius must be positive')
            goal_handle.abort()
            return ArcDrive.Result(success=False)

        # --- オープンループ（時間制御）モード ---
        if not use_odom:
            self.get_logger().info('OPEN-LOOP MODE: Driving by time (Odometry ignored)')
            target_angle_rad = abs(math.radians(target_angle_deg))
            angular_speed = linear_speed / target_radius
            duration = (target_radius * target_angle_rad) / linear_speed
            
            msg = Twist()
            msg.linear.x = float(linear_speed)
            msg.angular.z = float(angular_speed if target_angle_deg > 0 else -angular_speed)
            
            start_time = self.get_clock().now()
            rate = self.create_rate(100)
            while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
                if goal_handle.is_cancel_requested:
                    self.stop_turtle()
                    goal_handle.canceled()
                    return ArcDrive.Result(success=False)
                self.publisher_.publish(msg)
                rate.sleep()
            
            self.stop_turtle()
            goal_handle.succeed()
            return ArcDrive.Result(success=True)

        # --- クローズドループ（オドメトリ利用）モード ---
        self.get_logger().info('CLOSED-LOOP MODE: Driving with sensor feedback')
        while self.current_pose is None:
            self.get_logger().info('Waiting for pose...')
            time.sleep(0.1)

        # スタート地点と円の中心を計算
        start_x = self.current_pose.x
        start_y = self.current_pose.y
        start_theta = self.current_pose.theta
        
        # 進行方向に対して90度(左または右)の場所に中心がある
        # 角度正なら左旋回(中心は左)、角度負なら右旋回(中心は右)
        center_offset_angle = start_theta + (math.pi/2.0 if target_angle_deg > 0 else -math.pi/2.0)
        center_x = start_x + target_radius * math.cos(center_offset_angle)
        center_y = start_y + target_radius * math.sin(center_offset_angle)
        
        self.get_logger().info(f'Arc center calculated at: ({center_x:.2f}, {center_y:.2f})')

        accumulated_angle = 0.0
        last_theta = start_theta
        
        # 基本の角速度 w = v / R
        nominal_angular_speed = abs(linear_speed / target_radius)
        if target_angle_deg < 0:
            nominal_angular_speed = -nominal_angular_speed
        
        target_angle_rad = abs(math.radians(target_angle_deg))
        kp_arc = self.get_parameter('kp_arc').value
        
        result = ArcDrive.Result()
        feedback_msg = ArcDrive.Feedback()
        
        rate = self.create_rate(100) # 100Hz
        
        try:
            while abs(accumulated_angle) < target_angle_rad:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                    self.stop_turtle()
                    return ArcDrive.Result(success=False)

                # --- P制御による軌道補正 ---
                # 現在の中心からの距離を計算
                dx = self.current_pose.x - center_x
                dy = self.current_pose.y - center_y
                current_dist = math.sqrt(dx**2 + dy**2)
                
                # 誤差 e = 現在の距離 - 理想の半径
                error = current_dist - target_radius
                
                # 補正値の計算
                # 左旋回(w>0)時: 外に膨らんだ(error>0) -> wを増やす
                # 右旋回(w<0)時: 外に膨らんだ(error>0) -> wを減らす(絶対値を増やす)
                correction = kp_arc * error
                if target_angle_deg < 0:
                    current_angular_speed = nominal_angular_speed - correction
                else:
                    current_angular_speed = nominal_angular_speed + correction
                
                # 指令の作成
                msg = Twist()
                msg.linear.x = float(linear_speed)
                msg.angular.z = float(current_angular_speed)
                self.publisher_.publish(msg)

                # --- 回転量の計算 ---
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
