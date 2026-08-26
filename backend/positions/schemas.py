from pydantic import BaseModel


class SignalSnapshotInput(BaseModel):
    indicator: str
    timeframe: str
    value: float
    direction: str


class CloseConditionInput(BaseModel):
    operator: str
    target_value: float


class LinkPositionSignalRequest(BaseModel):
    symbol: str
    signal: SignalSnapshotInput
    close_condition: CloseConditionInput | None = None


class LinkOrderSignalRequest(BaseModel):
    symbol: str
    order_id: str
    signal: SignalSnapshotInput
    close_condition: CloseConditionInput | None = None


class SignalSnapshotResponse(BaseModel):
    id: int
    indicator: str
    timeframe: str
    value: float
    direction: str


class CloseConditionResponse(BaseModel):
    id: int
    operator: str
    target_value: float


class PositionSignalLinkResponse(BaseModel):
    id: int
    symbol: str
    signal: SignalSnapshotResponse
    close_condition: CloseConditionResponse | None = None


class OrderSignalLinkResponse(BaseModel):
    id: int
    symbol: str
    order_id: str
    signal: SignalSnapshotResponse
    close_condition: CloseConditionResponse | None = None