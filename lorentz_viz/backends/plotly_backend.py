"""Plotly バックエンド。

アニメーション時にフレーム間でトレース数が変化しないよう、
目盛り線は NaN 区切りで 1 トレースに統合している。
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
import plotly.graph_objects as go

from lorentz_viz.backends.base import PlotBackend
from lorentz_viz.config import LorentzConfig
from lorentz_viz.core import invariants, transforms

# カラースキーム（matplotlib と同系統）
_COLOR_LIGHT_CONE = "gray"
_COLOR_TIMELIKE = "royalblue"
_COLOR_SPACELIKE = "crimson"
_COLOR_PRIMED_X = "green"
_COLOR_PRIMED_CT = "darkcyan"
_COLOR_TICK = "#777777"


def _ticks_to_arrays(
    ticks: List[Tuple[Tuple[float, float], Tuple[float, float]]],
) -> Tuple[List[float], List[float]]:
    """目盛り端点リストを NaN 区切りの平坦配列に変換する。

    フレーム間でトレース数を固定するために、可変本数の短線分を
    NaN で区切った 1 本の折れ線として表現する。
    """
    xs: List[float] = []
    cts: List[float] = []
    for (x_pair, ct_pair) in ticks:
        xs.extend([x_pair[0], x_pair[1], float("nan")])
        cts.extend([ct_pair[0], ct_pair[1], float("nan")])
    return xs, cts


def _build_traces(beta: float, config: LorentzConfig) -> List[go.BaseTraceType]:
    """指定された beta の全トレースを構築して返す。

    Notes
    -----
    アニメーション時にすべてのフレームでトレース数・順序が同一でなければ
    Plotly が正しく更新できない。このためトレースの種類と順序は固定している。
    空のデータは x=[], y=[] で表現する。
    """
    traces: List[go.BaseTraceType] = []

    # 1. 光円錐 (2本)
    lc_lines = invariants.lightcone_lines(config.x_range, config.ct_range) if config.show_light_cone else []
    for i in range(2):
        if i < len(lc_lines):
            x_lc, ct_lc = lc_lines[i]
            x_data, y_data = x_lc.tolist(), ct_lc.tolist()
        else:
            x_data, y_data = [], []
        traces.append(go.Scatter(
            x=x_data, y=y_data,
            mode="lines",
            line=dict(color=_COLOR_LIGHT_CONE, dash="dash", width=1.5),
            name="光円錐" if i == 0 else "",
            showlegend=(i == 0),
        ))

    # 2. 時間的双曲線 (各 s²>0 につき上下 2 本)
    timelike_vals = [s2 for s2 in config.invariant_values if s2 > 0]
    spacelike_vals = [s2 for s2 in config.invariant_values if s2 < 0]

    for s2 in timelike_vals:
        x_h, ct_pos, ct_neg = invariants.timelike_hyperbola(s2, config.x_range)
        label = f"s²={s2:+.1f}"
        traces.append(go.Scatter(
            x=x_h.tolist(), y=ct_pos.tolist(),
            mode="lines",
            line=dict(color=_COLOR_TIMELIKE, width=1.5),
            name=label,
            legendgroup=label,
            showlegend=True,
        ))
        traces.append(go.Scatter(
            x=x_h.tolist(), y=ct_neg.tolist(),
            mode="lines",
            line=dict(color=_COLOR_TIMELIKE, width=1.5),
            name=label,
            legendgroup=label,
            showlegend=False,
        ))

    # 3. 空間的双曲線 (各 s²<0 につき左右 2 本)
    for s2 in spacelike_vals:
        ct_h, x_pos, x_neg = invariants.spacelike_hyperbola(s2, config.ct_range)
        label = f"s²={s2:+.1f}"
        traces.append(go.Scatter(
            x=x_pos.tolist(), y=ct_h.tolist(),
            mode="lines",
            line=dict(color=_COLOR_SPACELIKE, width=1.5),
            name=label,
            legendgroup=label,
            showlegend=True,
        ))
        traces.append(go.Scatter(
            x=x_neg.tolist(), y=ct_h.tolist(),
            mode="lines",
            line=dict(color=_COLOR_SPACELIKE, width=1.5),
            name=label,
            legendgroup=label,
            showlegend=False,
        ))

    # 4. x' 軸
    if config.show_primed_axes:
        x_xax, ct_xax = transforms.primed_x_axis_in_S(beta, config.x_range)
        traces.append(go.Scatter(
            x=x_xax.tolist(), y=ct_xax.tolist(),
            mode="lines",
            line=dict(color=_COLOR_PRIMED_X, width=2.5),
            name="x' 軸",
        ))
        # 5. ct' 軸
        x_ctax, ct_ctax = transforms.primed_ct_axis_in_S(beta, config.ct_range)
        traces.append(go.Scatter(
            x=x_ctax.tolist(), y=ct_ctax.tolist(),
            mode="lines",
            line=dict(color=_COLOR_PRIMED_CT, width=2.5),
            name="ct' 軸",
        ))
    else:
        # トレース数固定のためダミーを追加
        traces.append(go.Scatter(x=[], y=[], mode="lines", showlegend=False))
        traces.append(go.Scatter(x=[], y=[], mode="lines", showlegend=False))

    # 6. 目盛り (x' 軸・ct' 軸それぞれ 1 トレース、NaN 区切り)
    if config.show_tick_marks and config.show_primed_axes:
        ticks_x = transforms.tick_marks_on_primed_x_axis(beta, config.x_range)
        xs_x, cts_x = _ticks_to_arrays(ticks_x)
        ticks_ct = transforms.tick_marks_on_primed_ct_axis(beta, config.ct_range)
        xs_ct, cts_ct = _ticks_to_arrays(ticks_ct)
    else:
        xs_x, cts_x = [], []
        xs_ct, cts_ct = [], []

    traces.append(go.Scatter(
        x=xs_x, y=cts_x,
        mode="lines",
        line=dict(color=_COLOR_TICK, width=1.0),
        showlegend=False,
    ))
    traces.append(go.Scatter(
        x=xs_ct, y=cts_ct,
        mode="lines",
        line=dict(color=_COLOR_TICK, width=1.0),
        showlegend=False,
    ))

    return traces


def _make_layout(beta: float, config: LorentzConfig) -> go.Layout:
    gamma = transforms.lorentz_gamma(beta)
    return go.Layout(
        title=dict(text=f"ミンコフスキー時空図   β = {beta:.3f}   γ = {gamma:.3f}"),
        xaxis=dict(
            title="x",
            range=list(config.x_range),
            scaleanchor="y",
            scaleratio=1,
        ),
        yaxis=dict(
            title="ct",
            range=list(config.ct_range),
        ),
        width=680,
        height=680,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
    )


class PlotlyBackend(PlotBackend):

    def draw_static(self, beta: float, config: LorentzConfig) -> go.Figure:
        """静的ミンコフスキー図を描画して Plotly Figure を返す。"""
        traces = _build_traces(beta, config)
        layout = _make_layout(beta, config)
        return go.Figure(data=traces, layout=layout)

    def draw_animation(
        self,
        beta_max: float,
        frames: int,
        config: LorentzConfig,
    ) -> go.Figure:
        """β=0 から beta_max まで掃引する Plotly アニメーション Figure を返す。

        返された Figure は .write_html() でインタラクティブな HTML として保存できる。
        Play/Pause ボタンとスライダーを備える。
        """
        betas = np.linspace(0.0, beta_max, frames)

        initial_traces = _build_traces(0.0, config)
        layout = _make_layout(0.0, config)

        plotly_frames = []
        slider_steps = []

        for b in betas:
            frame_traces = _build_traces(b, config)
            gamma = transforms.lorentz_gamma(b)
            frame_name = f"{b:.4f}"
            plotly_frames.append(go.Frame(
                data=frame_traces,
                name=frame_name,
                layout=go.Layout(
                    title=dict(
                        text=f"ミンコフスキー時空図   β = {b:.3f}   γ = {gamma:.3f}"
                    )
                ),
            ))
            slider_steps.append(dict(
                args=[
                    [frame_name],
                    {"frame": {"duration": 50, "redraw": True}, "mode": "immediate"},
                ],
                label=f"{b:.2f}",
                method="animate",
            ))

        layout.update(
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                x=0.1,
                y=0,
                xanchor="right",
                yanchor="top",
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[
                            None,
                            {"frame": {"duration": 50, "redraw": True},
                             "fromcurrent": True,
                             "mode": "immediate"},
                        ],
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[
                            [None],
                            {"frame": {"duration": 0}, "mode": "immediate"},
                        ],
                    ),
                ],
            )],
            sliders=[dict(
                active=0,
                steps=slider_steps,
                x=0.1,
                y=0,
                len=0.9,
                currentvalue=dict(prefix="β: ", visible=True, xanchor="center"),
                transition=dict(duration=0),
            )],
        )

        return go.Figure(data=initial_traces, layout=layout, frames=plotly_frames)
