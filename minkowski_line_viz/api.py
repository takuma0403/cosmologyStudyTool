"""ユーザー向け高レベル API。

バックエンドは importlib で遅延インポートするため、
片方のみインストールされた環境でも使用できる。
"""

from __future__ import annotations

import importlib
from typing import Any, Literal, Optional

from minkowski_line_viz.config import MinkowskiLineConfig

BackendName = Literal["matplotlib"]

_BACKEND_REGISTRY: dict[str, str] = {
    "matplotlib": "minkowski_line_viz.backends.mpl_backend.MinkowskiLineMatplotlibBackend",
    # 将来的に plotly バックエンドを追加する場合はここに登録する
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


def plot_minkowski_line(
    config: Optional[MinkowskiLineConfig] = None,
    backend: BackendName = "matplotlib",
) -> Any:
    """ミンコフスキー直線変換図を左右 2 パネルで描画する。

    左パネル: S 系ビュー（x, ω 直交、x', ω' 軸が斜め、直線①）
    右パネル: S' 系ビュー（x', ω' 直交、変換後の直線①）

    Parameters
    ----------
    config : MinkowskiLineConfig, optional
        描画設定。省略するとデフォルト値を使用。
    backend : 'matplotlib'
        描画バックエンド。

    Returns
    -------
    matplotlib.figure.Figure
        バックエンド固有のフィギュアオブジェクト。

    Examples
    --------
    >>> from minkowski_line_viz import plot_minkowski_line, MinkowskiLineConfig
    >>> cfg = MinkowskiLineConfig(beta=0.6, line_slope=0.5)
    >>> fig = plot_minkowski_line(config=cfg)
    >>> fig.savefig("static.png")
    """
    if config is None:
        config = MinkowskiLineConfig()
    return _get_backend(backend).draw_static(config)


def animate_frame_correction(
    config: Optional[MinkowskiLineConfig] = None,
    frames: int = 60,
    backend: BackendName = "matplotlib",
) -> Any:
    """S 系ビュー → S' 系ビューへの視点補正アニメーションを生成する。

    β_view を 0 から -β_target まで ease-in-out 補間で変化させる。

    Parameters
    ----------
    config : MinkowskiLineConfig, optional
        描画設定。省略するとデフォルト値を使用。
    frames : int
        アニメーションのフレーム数。
    backend : 'matplotlib'
        描画バックエンド。

    Returns
    -------
    matplotlib.animation.FuncAnimation

    Notes
    -----
    返り値を変数に代入しないとガーベジコレクションされてアニメーションが消える。
    GIF 保存: ``anim.save("out.gif", writer="pillow", fps=config.fps)``

    Examples
    --------
    >>> from minkowski_line_viz import animate_frame_correction, MinkowskiLineConfig
    >>> cfg = MinkowskiLineConfig(beta=0.6, line_slope=0.5)
    >>> anim = animate_frame_correction(config=cfg, frames=60)
    >>> anim.save("correction.gif", writer="pillow", fps=cfg.fps)
    """
    if config is None:
        config = MinkowskiLineConfig()
    return _get_backend(backend).draw_animation(frames, config)
