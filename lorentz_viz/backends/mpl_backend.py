"""Matplotlib バックエンド。"""

from __future__ import annotations

from typing import List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from lorentz_viz.backends.base import PlotBackend
from lorentz_viz.config import LorentzConfig
from lorentz_viz.core import invariants, transforms

# カラースキーム
_COLOR_LIGHT_CONE = "#888888"
_COLOR_TIMELIKE = "#1f77b4"    # 青: 時間的双曲線
_COLOR_SPACELIKE = "#d62728"   # 赤: 空間的双曲線
_COLOR_PRIMED_X = "#2ca02c"    # 緑: x' 軸
_COLOR_PRIMED_CT = "#17becf"   # シアン: ct' 軸
_COLOR_TICK = "#555555"        # 灰: 目盛り


def _draw_frame(ax: Axes, beta: float, config: LorentzConfig) -> None:
    """ax をクリアし、指定された beta のミンコフスキー図を描画する。"""
    ax.cla()
    ax.set_xlim(config.x_range)
    ax.set_ylim(config.ct_range)
    ax.set_xlabel("x", fontsize=12)
    ax.set_ylabel("ct", fontsize=12)
    gamma = transforms.lorentz_gamma(beta)
    ax.set_title(f"Minkowski Diagram   b = {beta:.3f}   g = {gamma:.3f}", fontsize=11)
    ax.set_aspect("equal", adjustable="box")
    ax.axhline(0, color="black", linewidth=0.8, zorder=1)
    ax.axvline(0, color="black", linewidth=0.8, zorder=1)

    # Light cone
    if config.show_light_cone:
        for i, (x_lc, ct_lc) in enumerate(
            invariants.lightcone_lines(config.x_range, config.ct_range)
        ):
            ax.plot(
                x_lc, ct_lc,
                color=_COLOR_LIGHT_CONE,
                linewidth=1.2,
                linestyle="--",
                zorder=2,
                label="light cone (ct=+/-x)" if i == 0 else None,
            )

    # Lorentz invariant hyperbolae
    for s2 in config.invariant_values:
        label = f"s2={s2:+.1f}"
        if s2 > 0:
            x_h, ct_pos, ct_neg = invariants.timelike_hyperbola(s2, config.x_range)
            ax.plot(x_h, ct_pos, color=_COLOR_TIMELIKE, linewidth=1.2, zorder=3,
                    label=label)
            ax.plot(x_h, ct_neg, color=_COLOR_TIMELIKE, linewidth=1.2, zorder=3)
        elif s2 < 0:
            ct_h, x_pos, x_neg = invariants.spacelike_hyperbola(s2, config.ct_range)
            ax.plot(x_pos, ct_h, color=_COLOR_SPACELIKE, linewidth=1.2, zorder=3,
                    label=label)
            ax.plot(x_neg, ct_h, color=_COLOR_SPACELIKE, linewidth=1.2, zorder=3)

    # S' coordinate axes
    if config.show_primed_axes:
        x_xax, ct_xax = transforms.primed_x_axis_in_S(beta, config.x_range)
        ax.plot(x_xax, ct_xax, color=_COLOR_PRIMED_X, linewidth=2.0,
                zorder=4, label="x' axis")

        x_ctax, ct_ctax = transforms.primed_ct_axis_in_S(beta, config.ct_range)
        ax.plot(x_ctax, ct_ctax, color=_COLOR_PRIMED_CT, linewidth=2.0,
                zorder=4, label="ct' axis")

    # 目盛り線
    if config.show_tick_marks and config.show_primed_axes:
        for (xs, cts) in transforms.tick_marks_on_primed_x_axis(beta, config.x_range):
            ax.plot(xs, cts, color=_COLOR_TICK, linewidth=0.9, zorder=5)
        for (xs, cts) in transforms.tick_marks_on_primed_ct_axis(beta, config.ct_range):
            ax.plot(xs, cts, color=_COLOR_TICK, linewidth=0.9, zorder=5)

    ax.legend(loc="upper left", fontsize=8, framealpha=0.8)


class MatplotlibBackend(PlotBackend):

    def draw_static(self, beta: float, config: LorentzConfig) -> Figure:
        """静的ミンコフスキー図を描画して Figure を返す。"""
        fig, ax = plt.subplots(figsize=(7, 7))
        _draw_frame(ax, beta, config)
        fig.tight_layout()
        return fig

    def draw_animation(
        self,
        beta_max: float,
        frames: int,
        config: LorentzConfig,
    ) -> FuncAnimation:
        """β を 0 から beta_max まで掃引するアニメーションを返す。

        Notes
        -----
        返り値の FuncAnimation オブジェクトを変数に代入しないと
        ガーベジコレクションされてアニメーションが動作しない。
        """
        fig, ax = plt.subplots(figsize=(7, 7))
        betas = np.linspace(0.0, beta_max, frames)

        def update(frame_idx: int) -> List:
            _draw_frame(ax, betas[frame_idx], config)
            return []

        anim = FuncAnimation(
            fig,
            update,
            frames=frames,
            interval=50,    # ms/frame → 約20fps
            blit=False,     # ax.cla() を使うので blit=False
        )
        return anim
