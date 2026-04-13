"""ユーザー向け高レベル API。

バックエンドは importlib で遅延インポートするため、
片方のみインストールされた環境でも使用できる。
"""

from __future__ import annotations

import importlib
from typing import Any, Literal, Optional

from lorentz_viz.config import LorentzConfig

BackendName = Literal["matplotlib", "plotly"]

_BACKEND_REGISTRY: dict[str, str] = {
    "matplotlib": "lorentz_viz.backends.mpl_backend.MatplotlibBackend",
    "plotly": "lorentz_viz.backends.plotly_backend.PlotlyBackend",
}


def _get_backend(name: BackendName):
    if name not in _BACKEND_REGISTRY:
        raise ValueError(
            f"不明なバックエンド '{name}'。使用可能: {list(_BACKEND_REGISTRY)}"
        )
    module_path, class_name = _BACKEND_REGISTRY[name].rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls()


def plot_minkowski(
    beta: float,
    config: Optional[LorentzConfig] = None,
    backend: BackendName = "matplotlib",
) -> Any:
    """指定された β のミンコフスキー時空図を描画する。

    Parameters
    ----------
    beta : float
        ブーストパラメータ v/c。|β| < 1 が必要。
    config : LorentzConfig, optional
        描画設定。省略するとデフォルト値を使用。
    backend : 'matplotlib' | 'plotly'
        描画バックエンド。

    Returns
    -------
    matplotlib.figure.Figure  または  plotly.graph_objects.Figure
        バックエンド固有のフィギュアオブジェクト。

    Examples
    --------
    >>> from lorentz_viz import plot_minkowski
    >>> fig = plot_minkowski(beta=0.6)
    >>> fig.savefig("diagram.png")

    >>> fig = plot_minkowski(beta=0.6, backend="plotly")
    >>> fig.write_html("diagram.html")
    """
    if config is None:
        config = LorentzConfig()
    return _get_backend(backend).draw_static(beta, config)


def animate_boost(
    beta_max: float = 0.9,
    frames: int = 60,
    config: Optional[LorentzConfig] = None,
    backend: BackendName = "matplotlib",
) -> Any:
    """β=0 から beta_max まで掃引するアニメーションを生成する。

    Parameters
    ----------
    beta_max : float
        掃引する最大の β 値。0 < beta_max < 1 が必要。
    frames : int
        アニメーションのフレーム数。
    config : LorentzConfig, optional
        描画設定。省略するとデフォルト値を使用。
    backend : 'matplotlib' | 'plotly'
        描画バックエンド。

    Returns
    -------
    matplotlib.animation.FuncAnimation  または  plotly.graph_objects.Figure

    Notes
    -----
    **matplotlib バックエンドの場合:**
    返り値を変数に代入しないとガーベジコレクションされてアニメーションが消える。
    GIF 保存: ``anim.save("out.gif", writer="pillow", fps=20)``

    **plotly バックエンドの場合:**
    Play/Pause ボタンとスライダーを持つインタラクティブな Figure を返す。
    HTML 保存: ``fig.write_html("out.html")``

    Examples
    --------
    >>> from lorentz_viz import animate_boost
    >>> anim = animate_boost(beta_max=0.9, frames=60, backend="matplotlib")
    >>> anim.save("boost.gif", writer="pillow", fps=20)

    >>> fig = animate_boost(beta_max=0.9, frames=40, backend="plotly")
    >>> fig.write_html("boost.html")
    """
    if config is None:
        config = LorentzConfig()
    return _get_backend(backend).draw_animation(beta_max, frames, config)
