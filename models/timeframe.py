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
            Timeframe.M15: "15m",
            Timeframe.M30: "30m",
            Timeframe.H1: "1h",
            Timeframe.H4: "4h",
            Timeframe.D1: "1d",
        }[self]