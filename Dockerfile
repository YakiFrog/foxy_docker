FROM ros:foxy-ros-base

# GUI関連とTurtlesimのインストール
RUN apt-get update && apt-get install -y \
    ros-foxy-turtlesim \
    ros-foxy-action-msgs \
    ros-foxy-rmw-cyclonedds-cpp \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/foxy/setup.bash" >> ~/.bashrc
RUN echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> ~/.bashrc
RUN echo "if [ -f /root/.bashrc_foxy ]; then source /root/.bashrc_foxy; fi" >> ~/.bashrc

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
