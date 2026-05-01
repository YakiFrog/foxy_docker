import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import math
import time

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from bt_msgs.action import OpenLoopDrive

class OpenLoopDriveNode(Node):
    def __init__(self):
        super().__init__('open_loop_drive_node')
        
        # パラメータ設定
        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        self.declare_parameter('pose_topic', '/turtle1/pose')
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 1.0)
        self.declare_parameter('use_odometry', True)
        
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.pose_topic = self.get_parameter('pose_topic').value

        self.current_pose = None
        self.create_subscription(Pose, self.pose_topic, self.pose_callback, 10)

        self.callback_group = ReentrantCallbackGroup()
        
        # パブリッシャ
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
        
        self.get_logger().info('OpenLoopDrive Node (Hybrid OL/CL) started')

    def pose_callback(self, msg):
        self.current_pose = msg

    def goal_callback(self, goal_request):
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        drive_type = goal_handle.request.type
        target_value = goal_handle.request.target_value
        speed = abs(goal_handle.request.speed)
        use_odom = self.get_parameter('use_odometry').value
        
        try:
            # --- オープンループ（時間制御）モード ---
            if not use_odom:
                self.get_logger().info(f'OPEN-LOOP MODE: Driving {drive_type} by time')
                
                # パラメータ/目標値に基づく速度と時間の計算
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

                start_time = self.get_clock().now()
                rate = self.create_rate(100)
                while (self.get_clock().now() - start_time).nanoseconds / 1e9 < duration:
                    if goal_handle.is_cancel_requested:
                        self.stop_turtle()
                        goal_handle.canceled()
                        return OpenLoopDrive.Result(success=False)
                    self.publisher_.publish(msg)
                    rate.sleep()

            # --- クローズドループ（オドメトリ利用）モード ---
            else:
                self.get_logger().info(f'CLOSED-LOOP MODE: Driving {drive_type} with sensor feedback')
                while self.current_pose is None:
                    self.get_logger().info('Waiting for pose...')
                    time.sleep(0.1)

                start_pose = self.current_pose
                accumulated_dist = 0.0
                accumulated_angle = 0.0
                last_x, last_y = start_pose.x, start_pose.y
                last_theta = start_pose.theta
                
                msg = Twist()
                if drive_type == "rotate":
                    if speed <= 0: speed = abs(self.get_parameter('angular_speed').value)
                    msg.angular.z = float(speed if target_value > 0 else -speed)
                    target_limit = abs(math.radians(target_value))
                elif drive_type == "move":
                    if speed <= 0: speed = abs(self.get_parameter('linear_speed').value)
                    msg.linear.x = float(speed if target_value > 0 else -speed)
                    target_limit = abs(target_value)
                elif drive_type == "arc":
                    if speed <= 0: speed = abs(self.get_parameter('linear_speed').value)
                    radius = abs(goal_handle.request.radius)
                    msg.linear.x = float(speed)
                    msg.angular.z = float((speed/radius) if target_value > 0 else -(speed/radius))
                    target_limit = abs(math.radians(target_value))

                rate = self.create_rate(100)
                while rclpy.ok():
                    if goal_handle.is_cancel_requested:
                        self.stop_turtle()
                        goal_handle.canceled()
                        return OpenLoopDrive.Result(success=False)

                    # 進捗の更新
                    if drive_type == "move":
                        dx = self.current_pose.x - last_x
                        dy = self.current_pose.y - last_y
                        accumulated_dist += math.sqrt(dx**2 + dy**2)
                        last_x, last_y = self.current_pose.x, self.current_pose.y
                        current_progress = accumulated_dist
                    else:
                        diff = self.current_pose.theta - last_theta
                        if diff > math.pi: diff -= 2*math.pi
                        if diff < -math.pi: diff += 2*math.pi
                        accumulated_angle += diff
                        last_theta = self.current_pose.theta
                        current_progress = abs(accumulated_angle)

                    if current_progress >= target_limit:
                        break

                    self.publisher_.publish(msg)
                    rate.sleep()

            # 共通の終了処理
            self.stop_turtle()
            goal_handle.succeed()
            return OpenLoopDrive.Result(success=True)

        except Exception as e:
            self.get_logger().error(f'Error in execute_callback: {str(e)}')
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
