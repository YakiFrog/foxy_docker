# Foxy Test Environment (ROS 2 Foxy / Turtlesim)

このリポジトリは、ROS 2 Jazzy で開発された移動ロジックを ROS 2 Foxy 環境へ移植し、動作検証を行うためのテスト環境です。

## 1. 準備 (Requirements)

- Docker / Docker Compose
- X11 Server (Ubuntu 等の GUI 環境、または Windows/macOS での X サーバー設定)

## 2. 環境の起動

ホスト側の `~/.bashrc` に設定されたエイリアスを使用します。

```bash
# ビルド・起動・コンテナへのログインを一括実行
foxy_up
```

※ 初回実行時や `Dockerfile` を変更した後は自動的にビルドが走ります。

## 3. 開発ワークフロー (Inside Container)

コンテナ内では以下のエイリアスを使用して効率的に開発を行えます。

### ビルドと反映
- `build`: ワークスペースのビルド (`colcon build`)
- `src`: ビルド後の環境反映 (`source install/setup.bash`)

### サーバーの起動
1.  **ターミナル1**: `turtle_start` (Turtlesim GUI 起動)
2.  **ターミナル2**: `launch_all` (移動・回転用アクションサーバー起動)

### テスト実行・記録
- `run_seq`: 正方形走行テスト
- `run_8`: 8の字走行テスト
- `record`: rosbag 記録 (cmd_vel, pose, tf を記録)
- `move_2_2`: 特定座標 (2, 2) への移動テスト

## 4. 設定のカスタマイズ

### ROS_DOMAIN_ID
`docker-compose.yml` の `ROS_DOMAIN_ID` を書き換えることで通信グループを変更できます。
(現在は `.bashrc_foxy` 内の設定をコメントアウトし、compose 側が優先されるようになっています)

### 制御パラメータ
`src/turtlesim_logic/config/turtlesim_params.yaml` を書き換えて `build` することで、ゲインや速度制限を調整できます。

## 5. 通信設定 (DDS)

本環境では、異なる ROS バージョン間や Docker 越しの通信を安定させるため、以下の構成を採用しています。

- **RMW**: `rmw_fastrtps_cpp` (Fast-DDS)
- **共有メモリ禁止**: `fastdds_noshm.xml` を適用。
  - 同一ホスト内での ROS バージョン違いによる `Deserialization failed` や `bad_alloc` などのクラッシュを防ぎます。

## 6. ファイル構成
- `Dockerfile`: Foxy ベースのビルド定義
- `.bashrc_foxy`: コンテナ内の環境変数・エイリアス定義 (ホストから編集可能)
- `scripts/`: テスト用自動実行スクリプト群
