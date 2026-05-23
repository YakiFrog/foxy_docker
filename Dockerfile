FROM ros:foxy-ros-base

# 依存関係のインストール
RUN apt-get update && apt-get install -y \
    ros-foxy-action-msgs \
    && rm -rf /var/lib/apt/lists/*

RUN echo "source /opt/ros/foxy/setup.bash" >> ~/.bashrc
RUN echo "if [ -f /root/.bashrc_foxy ]; then source /root/.bashrc_foxy; fi" >> ~/.bashrc

# ワークスペースの設定
WORKDIR /ros2_ws
COPY ./src /ros2_ws/src

# エントリーポイントの設定
COPY ./entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
