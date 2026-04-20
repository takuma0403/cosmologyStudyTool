"""Matplotlib バックエンド。"""

from __future__ import annotations

from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from numpy.typing import NDArray

from minkowski_line_viz.backends.base import MinkowskiLineBackend
from minkowski_line_viz.config import MinkowskiLineConfig

# lorentz_viz の数学コアを再利用（DRY 原則）
from lorentz_viz.core.transforms import lorentz_boost

# カラースキーム
# S 系軸: 寒色系
_COLOR_X_AXIS   = "#56B4E9"   # 水色 (solid): x 軸
_COLOR_W_AXIS  = "#0072B2"   # 青   (dotted): w 軸
# S' 系軸: 黄緑・緑系
_COLOR_XP_AXIS  = "#AADD00"   # 黄緑 (solid): x' 軸
_COLOR_WP_AXIS = "#228B22"   # 緑   (dotted): w' 軸
# その他
_COLOR_LIGHT_CONE = "#888888"  # 灰: 光円錐
_COLOR_LINE1      = "#D62728"  # 赤: 直線1


# ---------------------------------------------------------------------------
# 内部ヘルパー関数
# ---------------------------------------------------------------------------

def _ease_inout_sequence(
    start: float,
    end: float,
    n: int,
) -> NDArray[np.float64]:
    """cos カーブによる ease-in-out 補間列を返す。

    result[i] = start + (end - start) * (1 - cos(π * i / (n-1))) / 2

    Parameters
    ----------
    start, end : float
        補間の開始値と終了値。
    n : int
        要素数。n=1 の場合は start のみを返す。
    """
    if n == 1:
        return np.array([start])
    i = np.arange(n, dtype=float)
    t = (1.0 - np.cos(np.pi * i / (n - 1))) / 2.0
    result = start + (end - start) * t
    # 浮動小数点誤差を除去: 末尾を厳密に end に設定
    result[-1] = end
    return result


def _compute_line_data(
    config: MinkowskiLineConfig,
    beta_view: float,
) -> Dict[str, Tuple[NDArray, NDArray]]:
    """beta_view で全描画要素をローレンツ変換した座標を返す。

    「視点ブースト」beta_view を適用することで、
    - beta_view = 0         → S 系ビュー（x, w 直交、x', w' 斜め）
    - beta_view = +config.beta → S' 系ビュー（x', w' 直交）

    数学的根拠
    ----------
    x' 軸の S 系座標 (λ, β·λ) に lorentz_boost(..., +β) を適用すると
        x'' = γ(λ - β·β·λ) = λ(1-β²)·γ = λ/γ,  w'' = 0   → 水平
    w' 軸の S 系座標 (β·λ, λ) に同変換を適用すると
        x'' = 0,  w'' = λ/γ                                  → 垂直

    Notes
    -----
    lorentz_boost(x, ct, beta) の第2引数 ct は、
    ここでは w（時間的座標）として使用する。数学的構造は同一。
    """
    beta = config.beta
    n = config.n_points
    x_min, x_max = config.x_range
    w_min, w_max = config.wega_range

    # パラメータ配列
    lam_x  = np.linspace(x_min, x_max, n)   # x 方向のパラメータ
    lam_w = np.linspace(w_min, w_max, n)  # w 方向のパラメータ

    # S 系座標を定義してから beta_view で変換
    # x 軸: (λ, 0)
    x_ax_x, x_ax_w = lorentz_boost(lam_x, np.zeros(n), beta_view)

    # w 軸: (0, λ)
    w_ax_x, w_ax_w = lorentz_boost(np.zeros(n), lam_w, beta_view)

    # x' 軸: S 系での w' = 0 の軌跡 → w = β·x → 点 (λ, β·λ)
    xp_ax_x, xp_ax_w = lorentz_boost(lam_x, beta * lam_x, beta_view)

    # w' 軸: S 系での x' = 0 の軌跡 → x = β·w → 点 (β·λ, λ)
    wp_ax_x, wp_ax_w = lorentz_boost(beta * lam_w, lam_w, beta_view)

    # 直線1: x_const が指定されていれば垂直世界線、なければ slope/intercept 直線
    if config.x_const is not None:
        line1_x, line1_w_t = lorentz_boost(np.full(n, config.x_const), lam_w, beta_view)
    else:
        line1_w = config.line_slope * lam_x + config.line_intercept
        line1_x, line1_w_t = lorentz_boost(lam_x, line1_w, beta_view)

    result: Dict[str, Tuple[NDArray, NDArray]] = {
        "x_axis":    (x_ax_x,  x_ax_w),
        "wega_axis": (w_ax_x, w_ax_w),
        "xp_axis":   (xp_ax_x, xp_ax_w),
        "wp_axis":  (wp_ax_x, wp_ax_w),
        "line1":     (line1_x,  line1_w_t),
    }

    # 光円錐: w = ±x → 点 (λ, λ) と (λ, -λ)
    if config.show_light_cone:
        lc_pos_x, lc_pos_w = lorentz_boost(lam_x,  lam_x, beta_view)
        lc_neg_x, lc_neg_w = lorentz_boost(lam_x, -lam_x, beta_view)
        result["lightcone_pos"] = (lc_pos_x, lc_pos_w)
        result["lightcone_neg"] = (lc_neg_x, lc_neg_w)

    return result


def _draw_single_panel(
    ax: Axes,
    data: Dict[str, Tuple[NDArray, NDArray]],
    config: MinkowskiLineConfig,
    title: str,
    is_primed_view: bool = False,
) -> None:
    """単一パネルへの描画（静的図・アニメーション共用）。"""
    ax.cla()
    ax.set_xlim(config.x_range)
    ax.set_ylim(config.w_range)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title, fontsize=11)

    # 軸ラベル: S' 系ビューでは x', w' と表示
    if is_primed_view:
        ax.set_xlabel("x'", fontsize=12)
        ax.set_ylabel("w'", fontsize=12)
    else:
        ax.set_xlabel("x", fontsize=12)
        ax.set_ylabel("w", fontsize=12)

    # 光円錐
    if config.show_light_cone and "lightcone_pos" in data:
        ax.plot(
            *data["lightcone_pos"],
            color=_COLOR_LIGHT_CONE, linewidth=1.2, linestyle="--",
            zorder=2, label="light cone (w=±x)",
        )
        ax.plot(
            *data["lightcone_neg"],
            color=_COLOR_LIGHT_CONE, linewidth=1.2, linestyle="--",
            zorder=2,
        )

    # S 系座標軸（寒色: 水色 solid / 青 dotted）
    ax.plot(
        *data["x_axis"],
        color=_COLOR_X_AXIS, linewidth=2.0, linestyle="-",
        zorder=3, label="x axis" if not is_primed_view else "x axis (S)",
    )
    ax.plot(
        *data["w_axis"],
        color=_COLOR_W_AXIS, linewidth=2.0, linestyle=":",
        zorder=3, label="w axis" if not is_primed_view else "w axis (S)",
    )

    # S' 系座標軸（黄緑 solid / 緑 dotted）
    if config.show_primed_axes:
        ax.plot(
            *data["xp_axis"],
            color=_COLOR_XP_AXIS, linewidth=2.0, linestyle="-",
            zorder=4, label="x' axis",
        )
        ax.plot(
            *data["wp_axis"],
            color=_COLOR_WP_AXIS, linewidth=2.0, linestyle=":",
            zorder=4, label="w' axis",
        )

    # 直線1（赤 solid）
    if config.x_const is not None:
        line1_label = f"Line 1 (x={config.x_const:+.2f})"
    else:
        line1_label = f"Line 1 (w={config.line_slope:+.2f}x{config.line_intercept:+.2f})"
    ax.plot(
        *data["line1"],
        color=_COLOR_LINE1, linewidth=2.5, linestyle="-",
        zorder=5,
        label=line1_label,
    )

    # 原点マーカー
    ax.plot(0, 0, "ko", markersize=4, zorder=6)

    ax.legend(loc="upper left", fontsize=8, framealpha=0.85)
    ax.grid(True, linewidth=0.4, alpha=0.4)


# ---------------------------------------------------------------------------
# バックエンドクラス
# ---------------------------------------------------------------------------

class MinkowskiLineMatplotlibBackend(MinkowskiLineBackend):

    def draw_static(self, config: MinkowskiLineConfig) -> Figure:
        """左右 2 パネルの静的図を描画して Figure を返す。

        左: S 系ビュー（β_view=0）
        右: S' 系ビュー（β_view=+β → x', w' 直交）
        """
        fig, (ax_left, ax_right) = plt.subplots(
            1, 2, figsize=(14, 7), constrained_layout=True
        )
        gamma = 1.0 / np.sqrt(1.0 - config.beta ** 2)

        # 左パネル: S 系ビュー
        data_left = _compute_line_data(config, beta_view=0.0)
        _draw_single_panel(
            ax_left, data_left, config,
            title=f"S frame view   β={config.beta:.2f}   γ={gamma:.3f}",
            is_primed_view=False,
        )

        # 右パネル: S' 系ビュー（β_view=+β で x', w' が直交になる）
        data_right = _compute_line_data(config, beta_view=config.beta)
        _draw_single_panel(
            ax_right, data_right, config,
            title=f"S' frame view (corrected)   β={config.beta:.2f}   γ={gamma:.3f}",
            is_primed_view=True,
        )

        return fig

    def draw_animation(
        self,
        frames: int,
        config: MinkowskiLineConfig,
    ) -> FuncAnimation:
        """S 系ビュー → S' 系ビューへの視点補正アニメーションを返す。

        β_view を 0 から +β_target まで ease-in-out 補間で変化させる。
        β_view=+β のとき x', w' 軸が直交になる。

        Notes
        -----
        返り値の FuncAnimation オブジェクトを変数に代入しないと
        ガーベジコレクションされてアニメーションが動作しない。
        GIF 保存: ``anim.save("out.gif", writer="pillow", fps=config.fps)``
        """
        fig, ax = plt.subplots(figsize=(7, 7))
        gamma = 1.0 / np.sqrt(1.0 - config.beta ** 2)

        # ease-in-out で β_view を 0 → +β_target に補間
        # β_view=+β のとき x' 軸が水平・w' 軸が垂直になる
        beta_views: NDArray = _ease_inout_sequence(0.0, config.beta, frames)

        def update(frame_idx: int) -> List:
            bv = beta_views[frame_idx]
            data = _compute_line_data(config, bv)
            progress = frame_idx / max(frames - 1, 1) * 100
            is_primed = (frame_idx == frames - 1)
            _draw_single_panel(
                ax, data, config,
                title=(
                    f"Frame correction   β={config.beta:.2f}   γ={gamma:.3f}\n"
                    f"β_view={bv:.3f}   progress={progress:.0f}%"
                ),
                is_primed_view=is_primed,
            )
            return []

        interval_ms = int(1000 / config.fps)
        anim = FuncAnimation(
            fig,
            update,
            frames=frames,
            interval=interval_ms,
            blit=False,
        )
        return anim
