"""
lorentz_viz デモスクリプト

使い方:
    python examples/demo.py

生成されるファイル (examples/lorentz_viz/ 以下):
    minkowski_beta0.png          β=0 の静的図
    minkowski_beta06.png         β=0.6 の静的図
    minkowski_beta08_custom.png  カスタム設定での静的図
    boost_animation.gif          Matplotlib アニメーション GIF
    minkowski_plotly.html        Plotly 静的図 (インタラクティブ)
    boost_animation_plotly.html  Plotly アニメーション (スライダー付き)
"""

import os
import sys

# パッケージルートを PYTHONPATH に追加（pip install -e . なしで実行する場合）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import matplotlib
matplotlib.use("Agg")  # ヘッドレス環境でも動作するよう非インタラクティブバックエンドを使用

from lorentz_viz import LorentzConfig, animate_boost, plot_minkowski


def main() -> None:
    out_dir = os.path.join(os.path.dirname(__file__), "dist")
    os.makedirs(out_dir, exist_ok=True)

    # ── 1. β=0 (静止): primed 軸が unprimed 軸と一致することを確認 ──
    fig = plot_minkowski(beta=0.0, backend="matplotlib")
    path = os.path.join(out_dir, "minkowski_beta0.png")
    fig.savefig(path, dpi=120)
    print(f"保存: {path}")

    # ── 2. β=0.6 ──
    fig = plot_minkowski(beta=0.6, backend="matplotlib")
    path = os.path.join(out_dir, "minkowski_beta06.png")
    fig.savefig(path, dpi=120)
    print(f"保存: {path}")

    # ── 3. カスタム設定 (β=0.8、より多くの不変量) ──
    cfg = LorentzConfig(
        x_range=(-4.0, 4.0),
        ct_range=(-4.0, 4.0),
        invariant_values=[0.5, 1.0, 2.0, -0.5, -1.0, -2.0],
        show_tick_marks=True,
    )
    fig = plot_minkowski(beta=0.8, config=cfg, backend="matplotlib")
    path = os.path.join(out_dir, "minkowski_beta08_custom.png")
    fig.savefig(path, dpi=120)
    print(f"保存: {path}")

    # ── 4. Matplotlib アニメーション → GIF ──
    anim = animate_boost(beta_max=0.9, frames=60, backend="matplotlib")
    path = os.path.join(out_dir, "boost_animation.gif")
    anim.save(path, writer="pillow", fps=20)
    print(f"保存: {path}")

    # ── 5. Plotly 静的図 → HTML ──
    try:
        fig_plotly = plot_minkowski(beta=0.6, backend="plotly")
        path = os.path.join(out_dir, "minkowski_plotly.html")
        fig_plotly.write_html(path)
        print(f"保存: {path}")
    except ImportError:
        print("plotly が未インストールのためスキップします。")

    # ── 6. Plotly アニメーション → HTML ──
    try:
        fig_anim = animate_boost(beta_max=0.9, frames=40, backend="plotly")
        path = os.path.join(out_dir, "boost_animation_plotly.html")
        fig_anim.write_html(path)
        print(f"保存: {path}")
    except ImportError:
        print("plotly が未インストールのためスキップします。")


if __name__ == "__main__":
    main()
