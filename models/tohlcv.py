from typing import TypedDict

class TOHLCV(TypedDict):
    Timestamp: int
    Open: float
    High: float
    Low: float
    Close: float
    Volume: float