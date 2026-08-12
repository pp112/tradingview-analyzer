from pydantic import BaseModel
from enum import Enum

class Side(Enum):
    LONG = "long"
    SHORT = "short"

class Order(BaseModel):
    symbol: str
    side: Side
    

class Position(BaseModel):
    symbol: str
    side: Side
