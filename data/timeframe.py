from enum import Enum

class Timeframe(Enum):
    M15 = "15"
    M30 = "30"
    H1 = "60"
    H4 = "240"
    D1 = "1D"

    @property
    def label(self):
        return {
            "15": "15m",
            "30": "30m",
            "60": "1h",
            "240": "4h",
            "1D": "1d",
        }[self.value]