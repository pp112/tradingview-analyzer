import os
import json
from dataclasses import dataclass
from typing import Literal

from market import TradingViewHttpClient
from storage.writer import ensure_dir


@dataclass
class SpikeSignal:
    symbol: str
    signal_type: Literal["price", "volume"]
    direction: Literal["up", "down"]
    prev: float
    curr: float


class PriveVolumeMonitor:

    SNAPSHOT_PATH = "data/state/spike_snapshot.json"

    def __init__(
        self, 
        price_threshold: float = 5.0, 
        volume_multiplier: float = 4.0
    ):
        self.price_threshold = price_threshold
        self.volume_multiplier = volume_multiplier
        self.http_client = TradingViewHttpClient()
    
    async def check(self):
        current = await self.http_client.fetch_data()
        previous = self._load_snapshot()
        signals = []

        if previous:
            signals = self._detect_spikes(previous, current)
        else:
            self._save_snapshot(current)
        
        return signals
        
    def _detect_spikes(self, prev: dict[str, dict], curr: dict[str, dict]):
        signals = []

        for symbol, curr_data in curr.items():
            prev_data = prev.get(symbol)
            if prev_data is None:
                continue

            prev_price = prev_data.get("change_price", 0.0)
            curr_price = curr_data.get("change_price", 0.0)
            prev_vol = prev_data.get("change_volume", 0.0)
            curr_vol = curr_data.get("change_volume", 0.0)

            price_delta = curr_price - prev_price
            volume_ratio = curr_vol / prev_vol if prev_vol != 0 else 0.0

            price_direction = (
               "up" if price_delta > 0 else "down" if price_delta < 0 else "flat"
            )
            volume_direction = (
                "up" if curr_vol > prev_vol else "down" if curr_vol < prev_vol else "flat"
            )

            if price_delta >= self.price_threshold:
                signals.append(SpikeSignal(
                    symbol=symbol,
                    signal_type="price",
                    direction=price_direction,
                    prev=prev_price,
                    curr=curr_price
                ))
            if volume_ratio >= self.volume_multiplier:
                signals.append(SpikeSignal(
                    symbol=symbol,
                    signal_type="volume",
                    direction=volume_direction,
                    prev=prev_vol,
                    curr=curr_vol
                ))

        return signals

    def _load_snapshot(self):
        if not os.path.exists(self.SNAPSHOT_PATH):
            return None
        with open(self.SNAPSHOT_PATH, encoding="utf-8") as f:
            return json.load(f)
        
    def _save_snapshot(self, snapshot: dict):
        ensure_dir(self.SNAPSHOT_PATH)
        with open(self.SNAPSHOT_PATH, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=4, ensure_ascii=False)
    