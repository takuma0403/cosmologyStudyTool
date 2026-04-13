from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class LorentzConfig:
    """ミンコフスキー図の描画設定。

    Attributes
    ----------
    x_range : (float, float)
        x 軸の表示範囲。
    ct_range : (float, float)
        ct 軸の表示範囲。
    invariant_values : list[float]
        描画するローレンツ不変量 s² のリスト。
        正 → 時間的双曲線 (ct)²-x²=s²
        負 → 空間的双曲線 x²-(ct)²=|s²|
    show_light_cone : bool
        光円錐 (ct=±x) を描画するか。
    show_primed_axes : bool
        慣性系 S' の座標軸 (x', ct') を描画するか。
    show_tick_marks : bool
        S' 軸上の目盛りを描画するか。
    c : float
        光速 (自然単位系では 1)。
    """

    x_range: Tuple[float, float] = (-3.0, 3.0)
    ct_range: Tuple[float, float] = (-3.0, 3.0)
    invariant_values: List[float] = field(
        default_factory=lambda: [1.0, 2.0, -1.0, -2.0]
    )
    show_light_cone: bool = True
    show_primed_axes: bool = True
    show_tick_marks: bool = True
    c: float = 1.0
