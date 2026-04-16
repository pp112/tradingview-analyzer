from typing import TypedDict

class TOHLC(TypedDict):
    Timestamp: int
    Open: float
    High: float
    Low: float
    Close: float