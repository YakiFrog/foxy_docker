# Turtlesim Navigation Logic (Foxy Test)

Turtlesim を使ったオープンループ（時間制御）およびクローズドループ（センサー制御）の統合制御システム。

## 0. セットアップ手順

### コンテナの起動・ビルド
ホストマシンのターミナルで実行してください。
```bash
docker compose build  # イメージのビルド (初回やDockerfile変更時)
foxy_up               # (中身: cd ~/foxy_test && docker compose up -d --build && docker exec -it foxy_bt_tester bash) 起動して即入る
foxy_shell            # (中身: docker exec -it foxy_bt_tester bash) コンテナに入る
```

### 環境の初期化
コンテナ内に入ったら、まずエイリアスを読み込み、ワークスペースをビルドします。
```bash
source .bashrc_foxy          # エイリアスのロード
build                        # (または colcon build --symlink-install)
src                          # (または source install/setup.bash)
```

### トラブルシューティング（クリーンビルド）
アクションの定義変更が反映されない、あるいは `undefined symbol` 等のエラーが出る場合は、一度ビルド成果物を削除してやり直してください。
```bash
# ビルド成果物の全削除と再ビルド
rm -rf build/ install/ log/ && build && src
```

### オフライン環境への導入手順
インターネット接続がないPCに本環境を移行する場合の手順です。

#### 1. オンライン環境での準備（イメージの保存）
本PCで以下のコマンドを実行し、ビルド済みのDockerイメージを `tar` ファイルとしてエクスポートします。
```bash
docker save -o foxy_tester_image.tar foxy_test-foxy_tester:latest
```
出力された `foxy_tester_image.tar` と、本フォルダ一式をUSBメモリ等にコピーします。

#### 2. オフライン環境での導入
オフラインPCにUSBメモリからフォルダを配置し、`tar` ファイルがあるディレクトリで以下を実行してイメージをインポートします。
```bash
docker load -i foxy_tester_image.tar
```
インポート完了後、コンテナを起動します（`--build` は不要です）。
```bash
docker compose up -d
docker exec -it foxy_bt_tester bash
```

---

## 1. ノード構成
2つの独立したノードが起動します。

| アクション名 | 実行バイナリ | 制御方式 | 特徴 |
| :--- | :--- | :--- | :--- |
| `/open_loop_drive` | `open_loop_drive` | 時間ベース | オドメトリ不要。計算された秒数だけ指令を送る。 |
| `/closed_loop_drive` | `closed_loop_drive` | センサーベース | Poseトピックを監視。P制御により高精度に停止・トレース。 |

---

## 2. アクション定義 (`Drive.action`)
すべての移動指示は共通の `bt_msgs/action/Drive` を使用します。

### Goal フィールド
- `type`: 動作モードを指定 (`move`, `rotate`, `arc`, `move_to`)
- `target_value`: 移動距離(m) または 回転角(deg)
- `speed`: 指定速度（正の値）
- `radius`: 円弧走行時の半径 (`arc`時のみ)
- `x`, `y`: 目標の絶対座標 (`move_to`時のみ)
- `p_control_mode`: P減速の挙動指定
    - `0`: YAML のデフォルト設定に従う
    - `1`: 強制的に P減速を有効にする (目標直前でゆっくり止まる)
    - `2`: 強制的に P減速を無効にする (一定速度で突っ切る)

---

## 3. 主要パラメータ (`turtlesim_params.yaml`)
`closed_loop_drive_node` 内の主要な調整項目です。

- **速度制限**: `max_linear_speed` / `min_linear_speed` 等
- **許容誤差**: `dist_tolerance` (m) / `yaw_tolerance` (rad)
- **P制御ゲイン**:
    - `kp_linear`: 直進・座標移動時の減速強度
    - `kp_angular`: 旋回・向き修正時の強度
    - `kp_arc`: 円弧走行時の軌道(半径)修正の強度
- **P減速デフォルト**:
    - `default_use_p_move`, `default_use_p_rotate`, `default_use_p_arc`

---

## 4. 実行コマンド (エイリアス)
`.bashrc_foxy` に登録されている便利なショートカットです。

- **基本操作**: `build` (ビルド), `src` (環境反映), `launch_all` (ノード起動)
- **環境リセット**: `turtle_reset` (カメを中央に戻して画面をクリア)
- **自動走行スクリプト**:
    - `run_cl_square` / `run_ol_seq` : 角丸正方形走行 (CL/OL)
    - `run_cl_8` / `run_ol_8` : スムーズな8の字走行 (CL/OL)

---

## 5. OL と CL の具体的な違い
各動作モードにおける、制御の仕組みの違いです。

| 動作モード | OL (Open Loop) の挙動 | CL (Closed Loop) の挙動 |
| :--- | :--- | :--- |
| **MOVE (直進)** | 指定速度で「計算上の時間」だけ走行する。途中のスリップ等は無視される。 | 常に **移動距離を計測** し、目標距離に達するまで走り続ける。 |
| **ROTATE (旋回)** | 指定速度で「計算上の時間」だけ回転する。 | 常に **角度の変化を計測** し、目標角度に達するまで回転し続ける。 |
| **ARC (円弧)** | 一定の線速度と角速度で旋回する。外乱で円からズレても修正しない。 | **軌道補正(P制御)** が働く。理想の円から膨らんだり内に入ったりすると、角速度を自動調整して軌道に戻る。 |

### P減速 (Goal Deceleration) について
CL版ではさらに `p_control_mode` を使うことで、目標地点に近づいた時に **「ブレーキ（減速）」** をかけることができます。これにより、高速走行時でもオーバーシュート（行き過ぎ）を最小限に抑えられます。
