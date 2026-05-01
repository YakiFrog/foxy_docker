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
