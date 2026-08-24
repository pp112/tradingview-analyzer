from datetime import datetime
from sqlmodel import SQLModel, Field


class SignalSnapshot(SQLModel, table=True):
    """
    Копия сигнала на момент привязки к позиции/ордеру.
    """
    __tablename__ = "signal_snapshots"

    id: int | None = Field(default=None, primary_key=True)
    symbol: str
    indicator: str
    timeframe: str
    value: float
    direction: str
    captured_at: datetime = Field(default_factory=datetime.now)


class CloseCondition(SQLModel, table=True):
    """
    Условия автозакрытия позиции/ордера.
    """
    __tablename__ = "close_conditions"

    id: int | None = Field(default=None, primary_key=True)
    operator: str       # "<=" | ">="
    target_value: float


class TrackedPosition(SQLModel, table=True):
    """
    Привязка открытой позиции к сигналу + опциональное условие автозакрытия.
    Позиция идентифицируется по symbol
    """
    __tablename__ = "tracked_positions"

    id: int | None = Field(default=None, primary_key=True)
    symbol: str
    signal_snapshot_id: int = Field(foreign_key="signal_snapshots.id")
    close_condition_id: int | None = Field(default=None, foreign_key="close_conditions.id")
    created_at: datetime = Field(default_factory=datetime.now)
    closed_at: datetime | None = None


class TrackedOrder(SQLModel, table=True):
    """
    Привязка открытого ордера к сигналу + опциональное условие автоотмены.
    Ордер идентифицируется по order_id
    """
    __tablename__ = "tracked_orders"

    id: int | None = Field(default=None, primary_key=True)
    symbol: str
    order_id: str   # реальный UUID ордера на бирже
    signal_snapshot_id: int = Field(foreign_key="signal_snapshots.id")
    close_condition_id: int | None = Field(default=None, foreign_key="close_conditions.id")
    created_at: datetime = Field(default_factory=datetime.now)
    cancelled_at: datetime | None = None