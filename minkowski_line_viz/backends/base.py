"""バックエンドの抽象基底クラス。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from minkowski_line_viz.config import MinkowskiLineConfig


class MinkowskiLineBackend(ABC):
    """ミンコフスキー直線変換図描画バックエンドの抽象基底クラス。"""

    @abstractmethod
    def draw_static(self, config: MinkowskiLineConfig) -> Any:
        """左右 2 パネルの静的図を描画する。

        左パネル: S 系ビュー（x, w 直交、x', w' 斜め）
        右パネル: S' 系ビュー（x', w' 直交、直線① 変換後）

        Returns
        -------
        バックエンド固有のフィギュアオブジェクト。
        """

    @abstractmethod
    def draw_animation(self, frames: int, config: MinkowskiLineConfig) -> Any:
        """S 系ビュー → S' 系ビューへの視点補正アニメーションを描画する。

        β_view を 0 から -β_target まで ease-in-out で変化させる。

        Returns
        -------
        バックエンド固有のアニメーション/フィギュアオブジェクト。
        """
