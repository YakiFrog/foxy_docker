FROM ros:foxy-ros-base

# GUI関連とTurtlesimのインストール
RUN apt-get update && apt-get install -y \
    ros-foxy-turtlesim \
    ros-foxy-action-msgs \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/foxy/setup.bash" >> ~/.bashrc
RUN echo "alias turtle_start='ros2 run turtlesim turtlesim_node &'" >> ~/.bashrc
RUN echo "alias logic_start='source /ros2_ws/install/setup.bash && ros2 run turtlesim_logic rotate_turtle'" >> ~/.bashrc
RUN echo "alias rotate_90='source /ros2_ws/install/setup.bash && ros2 action send_goal /rotate_degrees bt_msgs/action/RotateDegrees \"{target_degrees: 90.0}\" --feedback'" >> ~/.bashrc

# 必要であれば追加の依存関係をここに
RUN pip3 install --no-cache-dir \
    numpy

# ワークスペースの設定
WORKDIR /ros2_ws
COPY ./src /ros2_ws/src

# エントリーポイントの設定
COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
