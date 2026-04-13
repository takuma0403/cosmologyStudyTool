"""ローレンツ変換の純粋な数学。

依存ライブラリは numpy のみ。描画系のインポートは一切しない。
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
from numpy.typing import NDArray


def lorentz_gamma(beta: float) -> float:
    """ローレンツ因子 γ = 1/√(1-β²) を返す。

    Parameters
    ----------
    beta : float
        速度 v/c。|β| < 1 を要求する。

    Raises
    ------
    ValueError
        |β| >= 1 の場合。
    """
    if abs(beta) >= 1.0:
        raise ValueError(f"beta は |beta| < 1 を満たす必要があります。got {beta}")
    return float(1.0 / np.sqrt(1.0 - beta**2))


def lorentz_boost(
    x: NDArray[np.float64],
    ct: NDArray[np.float64],
    beta: float,
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """ローレンツブーストを適用する。

    S 系の座標 (x, ct) を、S に対して速度 v = βc で運動する S' 系へ変換する。

        x'  = γ (x  - β·ct)
        ct' = γ (ct - β·x)

    Parameters
    ----------
    x, ct : array-like
        S 系の座標。
    beta : float
        ブーストパラメータ v/c。

    Returns
    -------
    (x_prime, ct_prime) : tuple of ndarray
    """
    gamma = lorentz_gamma(beta)
    x = np.asarray(x, dtype=float)
    ct = np.asarray(ct, dtype=float)
    x_prime = gamma * (x - beta * ct)
    ct_prime = gamma * (ct - beta * x)
    return x_prime, ct_prime


def inverse_boost(
    x_prime: NDArray[np.float64],
    ct_prime: NDArray[np.float64],
    beta: float,
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """逆ローレンツブースト（-beta のブースト）。"""
    return lorentz_boost(x_prime, ct_prime, -beta)


def primed_x_axis_in_S(
    beta: float,
    x_range: Tuple[float, float],
    n_points: int = 400,
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """S 系から見た x' 軸の (x, ct) 座標列を返す。

    x' 軸は ct' = 0 の直線。ブースト変換から

        ct = β·x

    となる。β=0 のとき ct=0 (通常の x 軸)。
    """
    x = np.linspace(x_range[0], x_range[1], n_points)
    ct = beta * x
    return x, ct


def primed_ct_axis_in_S(
    beta: float,
    ct_range: Tuple[float, float],
    n_points: int = 400,
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """S 系から見た ct' 軸の (x, ct) 座標列を返す。

    ct' 軸は x' = 0 の直線。ブースト変換から

        x = β·ct

    となる。β=0 のとき x=0 (通常の ct 軸)。
    """
    ct = np.linspace(ct_range[0], ct_range[1], n_points)
    x = beta * ct  # β=0 のとき x=0 が自然に得られる
    return x, ct


def tick_marks_on_primed_x_axis(
    beta: float,
    x_range: Tuple[float, float],
) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """x' 軸上の等間隔目盛り線端点を返す。

    x' = ±1, ±2, ... の位置に垂直な短線分を配置する。
    各要素は ((x0, x1), (ct0, ct1)) の形式。
    """
    gamma = lorentz_gamma(beta)
    # x' 軸の方向ベクトル (S 系): (1, β) を正規化
    axis_len = np.sqrt(1.0 + beta**2)
    # x' 軸に垂直な方向: (-β, 1) を正規化
    perp_x = -beta / axis_len
    perp_ct = 1.0 / axis_len
    tick_half = 0.08

    ticks = []
    x_max = max(abs(x_range[0]), abs(x_range[1]))
    n_max = int(x_max * gamma) + 2

    for n in range(-n_max, n_max + 1):
        if n == 0:
            continue
        # x' = n, ct' = 0  →  逆ブーストで S 系座標を求める
        # x = γ(x' + β·ct') = γn,  ct = γ(ct' + β·x') = γβn
        x_center = gamma * n
        ct_center = gamma * beta * n
        if not (x_range[0] <= x_center <= x_range[1]):
            continue
        ticks.append((
            (x_center - tick_half * perp_x, x_center + tick_half * perp_x),
            (ct_center - tick_half * perp_ct, ct_center + tick_half * perp_ct),
        ))
    return ticks


def tick_marks_on_primed_ct_axis(
    beta: float,
    ct_range: Tuple[float, float],
) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
    """ct' 軸上の等間隔目盛り線端点を返す。

    ct' = ±1, ±2, ... の位置に垂直な短線分を配置する。
    各要素は ((x0, x1), (ct0, ct1)) の形式。
    """
    gamma = lorentz_gamma(beta)
    # ct' 軸の方向ベクトル (S 系): (β, 1) を正規化
    axis_len = np.sqrt(beta**2 + 1.0)
    # ct' 軸に垂直な方向: (-1, β) を正規化
    perp_x = -1.0 / axis_len
    perp_ct = beta / axis_len
    tick_half = 0.08

    ticks = []
    ct_max = max(abs(ct_range[0]), abs(ct_range[1]))
    n_max = int(ct_max * gamma) + 2

    for n in range(-n_max, n_max + 1):
        if n == 0:
            continue
        # x' = 0, ct' = n  →  逆ブーストで S 系座標を求める
        # x = γ(x' + β·ct') = γβn,  ct = γ(ct' + β·x') = γn
        x_center = gamma * beta * n
        ct_center = gamma * n
        if not (ct_range[0] <= ct_center <= ct_range[1]):
            continue
        ticks.append((
            (x_center - tick_half * perp_x, x_center + tick_half * perp_x),
            (ct_center - tick_half * perp_ct, ct_center + tick_half * perp_ct),
        ))
    return ticks
