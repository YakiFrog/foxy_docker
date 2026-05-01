import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import math
import time

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from bt_msgs.action import Drive

class ClosedLoopDriveNode(Node):
    def __init__(self):
        super().__init__('closed_loop_drive_node')
        
        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        self.declare_parameter('pose_topic', '/turtle1/pose')
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 1.0)
        self.declare_parameter('max_linear_speed', 2.0)
        self.declare_parameter('min_linear_speed', 0.1)
        self.declare_parameter('max_angular_speed', 2.0)
        self.declare_parameter('min_angular_speed', 0.1)
        self.declare_parameter('dist_tolerance', 0.05)
        self.declare_parameter('yaw_tolerance', 0.02)
        self.declare_parameter('default_use_p_move', False)
        self.declare_parameter('default_use_p_rotate', True)
        self.declare_parameter('default_use_p_arc', True)
        self.declare_parameter('kp_arc', 1.0)
        self.declare_parameter('kp_linear', 2.0)
        self.declare_parameter('kp_angular', 4.0)
        
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.pose_topic = self.get_parameter('pose_topic').value
        
        self.current_pose = None
        self.create_subscription(Pose, self.pose_topic, self.pose_callback, 10)
        self.publisher_ = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        
        self._action_server = ActionServer(
            self, Drive, 'closed_loop_drive',
            execute_callback=self.execute_callback,
            callback_group=ReentrantCallbackGroup()
        )
        self.get_logger().info('High-Precision ClosedLoopDrive Node Started')

    def pose_callback(self, msg):
        self.current_pose = msg

    def clamp(self, value, min_val, max_val):
        if abs(value) < min_val:
            return min_val if value >= 0 else -min_val
        if abs(value) > max_val:
            return max_val if value >= 0 else -max_val
        return value

    async def execute_callback(self, goal_handle):
        drive_type = goal_handle.request.type
        speed_request = abs(goal_handle.request.speed)
        p_mode = goal_handle.request.p_control_mode
        
        max_v = self.get_parameter('max_linear_speed').value
        min_v = self.get_parameter('min_linear_speed').value
        max_w = self.get_parameter('max_angular_speed').value
        min_w = self.get_parameter('min_angular_speed').value
        d_tol = self.get_parameter('dist_tolerance').value
        y_tol = self.get_parameter('yaw_tolerance').value
        kp_linear = self.get_parameter('kp_linear').value
        kp_angular = self.get_parameter('kp_angular').value
        kp_arc = self.get_parameter('kp_arc').value

        # --- P減速を使うかどうかの決定ロジック ---
        use_p = False
        if p_mode == 1: # 強制 ON
            use_p = True
        elif p_mode == 2: # 強制 OFF
            use_p = False
        else: # 0: YAML デフォルトに従う
            if drive_type == 'move': use_p = self.get_parameter('default_use_p_move').value
            elif drive_type == 'rotate': use_p = self.get_parameter('default_use_p_rotate').value
            elif drive_type == 'arc': use_p = self.get_parameter('default_use_p_arc').value
            elif drive_type == 'move_to': use_p = True # move_to は常に ON

        try:
            while self.current_pose is None:
                time.sleep(0.1)
            rate = self.create_rate(100)
            
            # --- 1. 絶対座標移動 (move_to) ---
            if drive_type == "move_to":
                target_x = goal_handle.request.x
                target_y = goal_handle.request.y
                while rclpy.ok():
                    dx = target_x - self.current_pose.x
                    dy = target_y - self.current_pose.y
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist < d_tol: break
                    target_yaw = math.atan2(dy, dx)
                    yaw_error = target_yaw - self.current_pose.theta
                    while yaw_error > math.pi: yaw_error -= 2*math.pi
                    while yaw_error < -math.pi: yaw_error += 2*math.pi
                    v = self.clamp(kp_linear * dist, min_v, max_v)
                    w = self.clamp(kp_angular * yaw_error, min_w, max_w)
                    msg = Twist()
                    msg.linear.x = float(v)
                    msg.angular.z = float(w)
                    self.publisher_.publish(msg)
                    rate.sleep()

            # --- 2. 相対移動 (rotate / move / arc) ---
            else:
                target_value = goal_handle.request.target_value
                accumulated = 0.0
                last_x, last_y = self.current_pose.x, self.current_pose.y
                last_theta = self.current_pose.theta
                
                if drive_type == "rotate":
                    speed_base = speed_request if speed_request > 0 else abs(self.get_parameter('angular_speed').value)
                    limit = abs(math.radians(target_value))
                elif drive_type == "move":
                    speed_base = speed_request if speed_request > 0 else abs(self.get_parameter('linear_speed').value)
                    limit = abs(target_value)
                elif drive_type == "arc":
                    speed_base = speed_request if speed_request > 0 else abs(self.get_parameter('linear_speed').value)
                    radius = abs(goal_handle.request.radius)
                    limit = abs(math.radians(target_value))
                    w_nominal = speed_base / radius
                    if target_value < 0: w_nominal = -w_nominal
                    center_offset = last_theta + (math.pi/2.0 if target_value > 0 else -math.pi/2.0)
                    cx = last_x + radius * math.cos(center_offset)
                    cy = last_y + radius * math.sin(center_offset)

                while rclpy.ok():
                    if goal_handle.is_cancel_requested:
                        self.stop_turtle()
                        goal_handle.canceled()
                        return Drive.Result(success=False)

                    if drive_type == "move":
                        dx, dy = self.current_pose.x - last_x, self.current_pose.y - last_y
                        accumulated += math.sqrt(dx**2 + dy**2)
                        last_x, last_y = self.current_pose.x, self.current_pose.y
                        if accumulated >= (limit - d_tol): break
                        
                        v = speed_base
                        if use_p:
                            remaining = limit - accumulated
                            v = min(speed_base, kp_linear * remaining)
                        msg = Twist()
                        msg.linear.x = float(self.clamp(v, min_v, max_v) if target_value > 0 else -self.clamp(v, min_v, max_v))
                    else:
                        diff = self.current_pose.theta - last_theta
                        if diff > math.pi: diff -= 2*math.pi
                        if diff < -math.pi: diff += 2*math.pi
                        accumulated += diff
                        last_theta = self.current_pose.theta
                        if abs(accumulated) >= (limit - y_tol): break

                        msg = Twist()
                        if drive_type == "rotate":
                            w = speed_base
                            if use_p:
                                remaining = limit - abs(accumulated)
                                w = min(speed_base, kp_angular * remaining)
                            val = self.clamp(w, min_w, max_w)
                            msg.angular.z = float(val if target_value > 0 else -val)
                        elif drive_type == "arc":
                            v = speed_base
                            if use_p:
                                remaining_angle = limit - abs(accumulated)
                                v = min(speed_base, kp_linear * (remaining_angle * radius))
                            
                            v_clamped = self.clamp(v, min_v, max_v)
                            w_ref = v_clamped / radius
                            if target_value < 0: w_ref = -w_ref
                            err = math.sqrt((self.current_pose.x-cx)**2 + (self.current_pose.y-cy)**2) - radius
                            w_final = w_ref - kp_arc*err if target_value < 0 else w_ref + kp_arc*err
                            if abs(w_final) > max_w:
                                w_final = max_w if w_final >= 0 else -w_final
                            msg.linear.x = float(v_clamped)
                            msg.angular.z = float(w_final)

                    self.publisher_.publish(msg)
                    rate.sleep()

            self.stop_turtle()
            goal_handle.succeed()
            return Drive.Result(success=True)
        except Exception as e:
            self.stop_turtle()
            goal_handle.abort()
            return Drive.Result(success=False)

    def stop_turtle(self):
        self.publisher_.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(ClosedLoopDriveNode(), executor=MultiThreadedExecutor())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
