"""
Pydantic-схемы API для привязки сигналов к позициям и ордерам.

Используются в backend.api.signal_links для:
- валидации входящих запросов;
- формирования ответов API;
"""

from datetime import datetime
from typing import Annotated, Literal, Union

from pydantic import Field

from backend.schemas.base import ApiModel


class SignalSnapshotInput(ApiModel):
    indicator: str
    timeframe: str
    value: float
    direction: str


class ValueCloseConditionInput(ApiModel):
    type: Literal["value"] = "value"
    operator: str
    target_value: float


class CrossoverCloseConditionInput(ApiModel):
    type: Literal["crossover"] = "crossover"


CloseConditionInput = Annotated[
    Union[ValueCloseConditionInput, CrossoverCloseConditionInput],
    Field(discriminator="type"),
]


class LinkPositionSignalRequest(ApiModel):
    """Запрос на привязку сигнала к открытой позиции."""
    symbol: str
    signal: SignalSnapshotInput
    close_condition: CloseConditionInput | None = None


class LinkOrderSignalRequest(ApiModel):
    """Запрос на привязку сигнала к открытому ордеру."""
    symbol: str
    exchange_order_id: str
    signal: SignalSnapshotInput
    close_condition: CloseConditionInput | None = None


class UpdateSignalLinkRequest(ApiModel):
    signal: SignalSnapshotInput
    close_condition: CloseConditionInput | None = None


class SignalSnapshotResponse(ApiModel):
    id: int
    indicator: str
    timeframe: str
    value: float
    direction: str


class ValueCloseConditionResponse(ApiModel):
    id: int
    type: Literal["value"] = "value"
    operator: str
    target_value: float


class CrossoverCloseConditionResponse(ApiModel):
    id: int
    type: Literal["crossover"] = "crossover"


CloseConditionResponse = Annotated[
    Union[ValueCloseConditionResponse, CrossoverCloseConditionResponse],
    Field(discriminator="type"),
]


class PositionSignalLinkResponse(ApiModel):
    """Ответ с данными привязки сигнала к позиции."""
    id: int
    symbol: str
    signal: SignalSnapshotResponse
    close_condition: CloseConditionResponse | None = None
    created_at: datetime


class OrderSignalLinkResponse(ApiModel):
    """Ответ с данными привязки сигнала к ордеру."""
    id: int
    symbol: str
    exchange_order_id: str
    signal: SignalSnapshotResponse
    close_condition: CloseConditionResponse | None = None
    created_at: datetime