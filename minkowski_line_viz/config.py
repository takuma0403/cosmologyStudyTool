from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class MinkowskiLineConfig:
    """ミンコフスキー直線変換図の描画設定。

    Attributes
    ----------
    x_range : (float, float)
        x 軸の表示範囲。
    omega_range : (float, float)
        ω 軸の表示範囲。
    beta : float
        ブーストパラメータ v/c。|β| < 1 が必要。
    line_slope : float
        直線① の傾き（ω = slope * x + intercept）。
    line_intercept : float
        直線① の切片。
    show_light_cone : bool
        光円錐 (ω = ±x) を描画するか。
    show_primed_axes : bool
        S' 系の座標軸 (x', ω') を描画するか。
    n_points : int
        各線の描画点数。
    fps : int
        アニメーションのフレームレート（GIF 保存時に参照）。
    """

    x_range: Tuple[float, float] = (-3.0, 3.0)
    omega_range: Tuple[float, float] = (-3.0, 3.0)
    beta: float = 0.6
    line_slope: float = 0.5
    line_intercept: float = 0.0
    show_light_cone: bool = True
    show_primed_axes: bool = True
    n_points: int = 400
    fps: int = 20

    def __post_init__(self) -> None:
        if abs(self.beta) >= 1.0:
            raise ValueError(
                f"beta は |beta| < 1 を満たす必要があります。got {self.beta}"
            )
