# cosmologyStudyTool

宇宙論（特殊相対論）の学習を補助するための可視化ツール集です。
ローレンツ変換やミンコフスキー時空図をアニメーションで直感的に理解することを目的としています。

## モジュール構成

### `lorentz_viz`
ミンコフスキー時空図上でローレンツ不変量（双曲線）を可視化します。
- β値を指定して静的なミンコフスキー図を描画
- β=0 から任意の値まで掃引するブーストアニメーションを生成
- Matplotlib（PNG/GIF）と Plotly（インタラクティブHTML）に対応

### `minkowski_line_viz`
S系とS'系の2パネルで、直線の座標変換をミンコフスキー図上に可視化します。
- 左パネル（S系）と右パネル（S'系）を並べて比較表示
- S系からS'系への視点補正アニメーションを生成

## セットアップ

| コマンド | 説明 |
|---|---|
| `make setup` | 仮想環境の作成と依存パッケージのインストール |
| `make run <script>` | 仮想環境上でスクリプトを実行 |
| `make freeze` | 現在の環境を `requirements.txt` に書き出し |

```bash
# 初回セットアップ
make setup
```

## クイックスタート

```bash
# lorentz_viz のデモ（PNG/GIF/HTML を examples/lorentz_viz/dist/ に出力）
make run examples/lorentz_viz/demo.py

# minkowski_line_viz のデモ（PNG/GIF を examples/minkowski_line_viz/dist/ に出力）
make run examples/minkowski_line_viz/demo.py
```

## 使用例

### lorentz_viz

```python
from lorentz_viz import plot_minkowski, animate_boost, LorentzConfig

# 静的図（β=0.6）
fig = plot_minkowski(beta=0.6)
fig.savefig("minkowski.png")

# カスタム設定
cfg = LorentzConfig(
    x_range=(-4.0, 4.0),
    ct_range=(-4.0, 4.0),
    invariant_values=[0.5, 1.0, 2.0, -0.5, -1.0, -2.0],
)
fig = plot_minkowski(beta=0.8, config=cfg)

# アニメーション（GIF）
anim = animate_boost(beta_max=0.9, frames=60, backend="matplotlib")
anim.save("boost.gif", writer="pillow", fps=20)

# インタラクティブHTML（Plotly）
fig_html = plot_minkowski(beta=0.6, backend="plotly")
fig_html.write_html("minkowski.html")
```

### minkowski_line_viz

```python
from minkowski_line_viz import plot_minkowski_line, animate_frame_correction, MinkowskiLineConfig

# デフォルト設定（β=0.6, 直線: w=0.5x）
cfg = MinkowskiLineConfig()
fig = plot_minkowski_line(config=cfg)
fig.savefig("line.png")

# カスタム設定（β=0.8, 直線: w=1.5x+0.5）
cfg_custom = MinkowskiLineConfig(
    beta=0.8,
    line_slope=1.5,
    line_intercept=0.5,
    show_light_cone=False,
)

# 視点補正アニメーション
anim = animate_frame_correction(config=cfg, frames=60)
anim.save("correction.gif", writer="pillow", fps=cfg.fps)
```

## 依存関係

- Python >= 3.9
- numpy >= 1.24
- matplotlib >= 3.7
- plotly >= 5.18
- pillow >= 9.0
