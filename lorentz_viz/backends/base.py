"""バックエンドの抽象基底クラス。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from lorentz_viz.config import LorentzConfig


class PlotBackend(ABC):
    """ミンコフスキー図描画バックエンドの抽象基底クラス。"""

    @abstractmethod
    def draw_static(self, beta: float, config: LorentzConfig) -> Any:
        """静的ミンコフスキー図を描画する。

        Returns
        -------
        バックエンド固有のフィギュアオブジェクト。
        """

    @abstractmethod
    def draw_animation(
        self,
        beta_max: float,
        frames: int,
        config: LorentzConfig,
    ) -> Any:
        """β=0 から beta_max まで掃引するアニメーションを描画する。

        Returns
        -------
        バックエンド固有のアニメーション/フィギュアオブジェクト。
        """
