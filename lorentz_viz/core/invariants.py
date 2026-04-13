"""ローレンツ不変量の双曲線・光円錐の点列生成。

依存ライブラリは numpy のみ。描画系のインポートは一切しない。
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
from numpy.typing import NDArray


def timelike_hyperbola(
    s_squared: float,
    x_range: Tuple[float, float],
    n_points: int = 500,
) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """時間的不変量の双曲線を生成する。

    (ct)² - x² = s²  (s² > 0)
    →  ct = ±√(s² + x²)

    光円錐の内側（時間的領域）に位置する。
    x_range 内の x に対して常に実数の ct が存在する。

    Returns
    -------
    (x, ct_positive, ct_negative)
    """
    if s_squared <= 0:
        raise ValueError(f"s_squared は正数が必要です (時間的双曲線)。got {s_squared}")
    x = np.linspace(x_range[0], x_range[1], n_points)
    ct_positive = np.sqrt(s_squared + x**2)
    ct_negative = -ct_positive
    return x, ct_positive, ct_negative


def spacelike_hyperbola(
    s_squared: float,
    ct_range: Tuple[float, float],
    n_points: int = 500,
) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """空間的不変量の双曲線を生成する。

    x² - (ct)² = |s²|  (s² < 0)
    →  x = ±√(|s²| + (ct)²)

    光円錐の外側（空間的領域）に位置する。
    ct_range 内の ct に対して常に実数の x が存在する。

    Parameters
    ----------
    s_squared : float
        符号付き不変量。空間的双曲線は s² < 0。

    Returns
    -------
    (ct, x_positive, x_negative)
    """
    if s_squared >= 0:
        raise ValueError(f"s_squared は負数が必要です (空間的双曲線)。got {s_squared}")
    abs_s2 = abs(s_squared)
    ct = np.linspace(ct_range[0], ct_range[1], n_points)
    x_positive = np.sqrt(abs_s2 + ct**2)
    x_negative = -x_positive
    return ct, x_positive, x_negative


def lightcone_lines(
    x_range: Tuple[float, float],
    ct_range: Tuple[float, float],
) -> List[Tuple[NDArray[np.float64], NDArray[np.float64]]]:
    """光円錐の境界線 ct = ±x を返す。

    s² = 0 の場合に対応する。表示範囲に収まる部分のみ返す。

    Returns
    -------
    list of (x, ct) — 2要素のリスト
        [0]: ct = +x の線  (未来右 / 過去左)
        [1]: ct = -x の線  (未来左 / 過去右)
    """
    limit = min(
        abs(x_range[0]), abs(x_range[1]),
        abs(ct_range[0]), abs(ct_range[1]),
    )
    x = np.array([-limit, limit])
    return [
        (x, x),    # ct = +x
        (x, -x),   # ct = -x
    ]
