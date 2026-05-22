import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import time
import math

from geometry_msgs.msg import Twist
from bt_msgs.action import Square, FigureEight

class OpenLoopShapeNode(Node):
    def __init__(self):
        super().__init__('open_loop_shape_node')
        
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('linear_speed', 1.0)
        self.declare_parameter('angular_speed', 1.0)
        
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.publisher_ = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        
        self._square_action_server = ActionServer(
            self, Square, 'open_loop_square',
            execute_callback=self.execute_square_callback,
            callback_group=ReentrantCallbackGroup()
        )
        self._figure_eight_action_server = ActionServer(
            self, FigureEight, 'open_loop_figure_eight',
            execute_callback=self.execute_figure_eight_callback,
            callback_group=ReentrantCallbackGroup()
        )
        self.get_logger().info('Pure OpenLoopShape Node Started (Hosting Square & FigureEight Actions)')

    async def run_motion(self, drive_type, target_value, speed, radius, goal_handle):
        msg = Twist()
        duration = 0.0

        if drive_type == "move":
            duration = abs(target_value) / speed
            msg.linear.x = float(speed if target_value > 0 else -speed)
        elif drive_type == "rotate":
            duration = abs(math.radians(target_value)) / speed
            msg.angular.z = float(speed if target_value > 0 else -speed)
        elif drive_type == "arc":
            duration = (abs(math.radians(target_value)) * radius) / speed
            msg.linear.x = float(speed)
            w = speed / radius
            msg.angular.z = float(w if target_value > 0 else -w)

        self.get_logger().info(f'Starting {drive_type}: duration={duration:.2f}s')

        start_time = self.get_clock().now()
        rate = self.create_rate(100) # 100Hz

        while rclpy.ok():
            elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
            if elapsed >= duration:
                break
            
            if goal_handle.is_cancel_requested:
                self.stop_turtle()
                return False

            self.publisher_.publish(msg)
            rate.sleep()

        self.stop_turtle()
        return True

    async def execute_square_callback(self, goal_handle):
        side = goal_handle.request.side
        radius = goal_handle.request.radius
        speed = goal_handle.request.speed
        if speed <= 0.0:
            speed = abs(self.get_parameter('linear_speed').value)

        self.get_logger().info(f'Starting Open Loop Square: side={side}, radius={radius}')
        
        for i in range(4):
            success = await self.run_motion("move", side, speed, 0.0, goal_handle)
            if not success:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                else:
                    goal_handle.abort()
                return Square.Result(success=False)
                
            success = await self.run_motion("arc", -90.0, speed, radius, goal_handle)
            if not success:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                else:
                    goal_handle.abort()
                return Square.Result(success=False)

        goal_handle.succeed()
        return Square.Result(success=True)

    async def execute_figure_eight_callback(self, goal_handle):
        scale = goal_handle.request.scale
        radius = goal_handle.request.radius
        speed = goal_handle.request.speed
        if speed <= 0.0:
            speed = abs(self.get_parameter('linear_speed').value)

        self.get_logger().info(f'Starting Open Loop Figure-8: scale={scale}, radius={radius}')

        # 1. Starting straight (RADIUS)
        success = await self.run_motion("move", radius, speed, 0.0, goal_handle)
        if not success:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
            else:
                goal_handle.abort()
            return FigureEight.Result(success=False)

        # 2. Left Loop (3 times of Straight + Left Arc)
        for i in range(3):
            success = await self.run_motion("move", scale, speed, 0.0, goal_handle)
            if not success:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                else:
                    goal_handle.abort()
                return FigureEight.Result(success=False)
            success = await self.run_motion("arc", 90.0, speed, radius, goal_handle)
            if not success:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                else:
                    goal_handle.abort()
                return FigureEight.Result(success=False)

        # 3. Connecting straight (RADIUS * 2 + SCALE)
        conn_dist = radius * 2.0 + scale
        success = await self.run_motion("move", conn_dist, speed, 0.0, goal_handle)
        if not success:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
            else:
                goal_handle.abort()
            return FigureEight.Result(success=False)

        # 4. Right Loop (3 times of Straight + Right Arc)
        for i in range(3):
            success = await self.run_motion("move", scale, speed, 0.0, goal_handle)
            if not success:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                else:
                    goal_handle.abort()
                return FigureEight.Result(success=False)
            success = await self.run_motion("arc", -90.0, speed, radius, goal_handle)
            if not success:
                if goal_handle.is_cancel_requested:
                    goal_handle.canceled()
                else:
                    goal_handle.abort()
                return FigureEight.Result(success=False)

        # 5. Final Straight (RADIUS + SCALE)
        final_dist = radius + scale
        success = await self.run_motion("move", final_dist, speed, 0.0, goal_handle)
        if not success:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
            else:
                goal_handle.abort()
            return FigureEight.Result(success=False)

        goal_handle.succeed()
        return FigureEight.Result(success=True)

    def stop_turtle(self):
        self.publisher_.publish(Twist())

def main(args=None):
    rclpy.init(args=args)
    node = OpenLoopShapeNode()
    rclpy.spin(node, executor=MultiThreadedExecutor())
    rclpy.shutdown()

if __name__ == '__main__':
    main()
