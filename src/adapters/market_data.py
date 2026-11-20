"""行情数据适配器（Mock 实现）。"""

from __future__ import annotations

from typing import Any


class MarketDataAdapter:
    """行情数据适配器（Mock）。"""

    def __init__(self, provider: str = "mock") -> None:
        self.provider = provider

    def quote(self, symbol: str) -> dict:
        return {
            "symbol": symbol,
            "price": 10.5,
            "change": 0.5,
            "change_pct": 5.0,
            "provider": self.provider,
        }

    def batch_quote(self, symbols: list[str]) -> dict:
        return {s: self.quote(s) for s in symbols}
