"""
minkowski_line_viz デモスクリプト

使い方:
    python examples/minkowski_line_viz/demo.py

生成されるファイル (examples/minkowski_line_viz/dist/ 以下):
    default_static.png          デフォルト設定での静的図（左右 2 パネル）
    custom_static.png           カスタム設定での静的図
    default_correction.gif      デフォルト設定の視点補正アニメーション
    custom_correction.gif       カスタム設定の視点補正アニメーション
"""

import os
import sys

# パッケージルートを PYTHONPATH に追加（pip install -e . なしで実行する場合）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import matplotlib
matplotlib.use("Agg")  # ヘッドレス環境でも動作するよう非インタラクティブバックエンドを使用

from minkowski_line_viz import (
    MinkowskiLineConfig,
    animate_frame_correction,
    plot_minkowski_line,
)


def main() -> None:
    out_dir = os.path.join(os.path.dirname(__file__), "dist")
    os.makedirs(out_dir, exist_ok=True)

    # ── 1. デフォルト設定での静的図 ──
    # β=0.6, 直線①: ω = 0.5x
    cfg_default = MinkowskiLineConfig()
    fig = plot_minkowski_line(config=cfg_default)
    path = os.path.join(out_dir, "default_static.png")
    fig.savefig(path, dpi=120)
    print(f"保存: {path}")

    # ── 2. カスタム設定での静的図 ──
    # β=0.8, 直線①: ω = 1.5x + 0.5, 光円錐なし
    cfg_custom = MinkowskiLineConfig(
        beta=0.8,
        line_slope=1.5,
        line_intercept=0.5,
        x_range=(-3.0, 3.0),
        omega_range=(-3.0, 3.0),
        show_light_cone=False,
    )
    fig = plot_minkowski_line(config=cfg_custom)
    path = os.path.join(out_dir, "custom_static.png")
    fig.savefig(path, dpi=120)
    print(f"保存: {path}")

    # ── 3. デフォルト設定の視点補正アニメーション → GIF ──
    anim = animate_frame_correction(config=cfg_default, frames=60)
    path = os.path.join(out_dir, "default_correction.gif")
    anim.save(path, writer="pillow", fps=cfg_default.fps)
    print(f"保存: {path}")

    # ── 4. カスタム設定の視点補正アニメーション → GIF ──
    anim_custom = animate_frame_correction(config=cfg_custom, frames=60)
    path = os.path.join(out_dir, "custom_correction.gif")
    anim_custom.save(path, writer="pillow", fps=cfg_custom.fps)
    print(f"保存: {path}")


if __name__ == "__main__":
    main()
