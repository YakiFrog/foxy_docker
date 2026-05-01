# Foxy Test Environment (ROS 2 Foxy / Turtlesim)

このリポジトリは、ROS 2 Jazzy で開発された移動ロジックを ROS 2 Foxy 環境へ移植し、動作検証を行うためのテスト環境です。Docker を使用して、安定した通信と GUI（Turtlesim）の表示を実現しています。

## 1. 準備 (Requirements)

- Docker / Docker Compose
- X11 Server (Ubuntu 等の GUI 環境、または Windows/macOS での X サーバー設定)
- `foxy_up` / `foxy_shell` エイリアスの設定（ホスト側の `~/.bashrc` 推奨）

## 2. 環境の起動

ホスト側で以下のコマンドを実行します。

```bash
# コンテナのビルドと起動
docker compose up -d --build

# コンテナ内に入る
docker exec -it foxy_test bash
```

## 3. 開発ワークフロー (Inside Container)

コンテナ内では便利なエイリアスが設定されています（`.bashrc_foxy`）。

### 初回・変更時のビルド
```bash
build  # colcon build --symlink-install
```

### サーバーの起動
1.  **ターミナル1**: カメの表示
    ```bash
    turtle_start
    ```
2.  **ターミナル2**: アクションサーバー（移動・回転）の起動
    ```bash
    launch_all
    ```

### テストの実行
- **正方形走行**: `run_seq`
- **8の字走行**: `run_8`
- **rosbag 記録**: `record` (別ターミナルで実行)
- **特定座標への移動テスト**: `move_2_2`

## 4. パラメータの調整

制御ゲインやトピック名は以下の YAML ファイルで管理されています。
ホスト側から編集可能で、変更後は `build` を行うことで反映されます。

- パス: `src/turtlesim_logic/config/turtlesim_params.yaml`

### 主要なパラメータ
- `kp_linear` / `kp_angular`: 比例ゲイン
- `max_linear_speed` / `max_angular_speed`: 最高速度制限
- `min_linear_speed` / `min_angular_speed`: 最小速度（スタック防止）
- `pose_topic` / `cmd_vel_topic`: 使用するトピック名

## 5. 通信の安定化について

Docker 越しの通信（特に `network_mode: host` 時）で発生する `Deserialization failed` エラーを回避するため、以下の設定を強制しています。

- **Fast-DDS 共有メモリ無効化**: `fastdds_noshm.xml` を使用。
- **Domain ID**: `57` (Jazzy 環境との混信防止)。

## 6. 実機への移植

Ubuntu 20.04 + ROS 2 Foxy の実機に移行する場合は、`scripts/` 内の絶対パス（`/ros2_ws/`）を実際のワークスペースのパスに置換してください。
コード自体は標準的な ROS 2 Python で書かれているため、そのまま動作します。
