from fastapi import APIRouter, Depends, HTTPException
from pydantic import TypeAdapter
from sqlmodel import Session

from backend.schemas.linked_values import CurrentIndicatorValueResponse
from backend.signal_links.service import (
    SignalLinkService, 
    SignalLinkNotFoundError,
    SignalSnapshotNotFoundError, 
    PositionAlreadyLinkedError,
    OrderAlreadyLinkedError,
)
from backend.storage.database import get_session
from backend.signal_links.models import CloseCondition, SignalSnapshot
from backend.schemas.signal_links import (
    CloseConditionResponse,
    CrossoverCloseConditionResponse,
    LinkOrderSignalRequest,
    LinkPositionSignalRequest,
    OrderSignalLinkResponse,
    PositionSignalLinkResponse,
    SignalLinksResponse,
    SignalSnapshotResponse,
    UpdateSignalLinkRequest,
    ValueCloseConditionResponse,
)
from backend.schemas.common import ActionResponse
from backend.storage.paths import LINKED_VALUES_FILE
from backend.storage.writer import read_json


router = APIRouter(prefix="/links", tags=["signal links"])

LINKED_VALUES_ADAPTER = TypeAdapter(list[CurrentIndicatorValueResponse])


def _make_snapshot_response(snapshot: SignalSnapshot) -> SignalSnapshotResponse:
    """
    Преобразует SQLModel-объект в Pydantic-схему для API-ответа.
    """
    return SignalSnapshotResponse(
        id=snapshot.id,
        indicator=snapshot.indicator,
        timeframe=snapshot.timeframe,
        value=snapshot.value,
        direction=snapshot.direction
    )


def _make_condition_response(
    condition: CloseCondition | None,
) -> CloseConditionResponse | None:
    """
    Преобразует SQLModel-объект в Pydantic-схему для API-ответа.
    """
    if condition is None:
        return None
    if condition.close_type == "crossover":
        return CrossoverCloseConditionResponse(id=condition.id)
    return ValueCloseConditionResponse(
        id=condition.id,
        operator=condition.operator,
        target_value=condition.target_value
    )


def _make_position_link_response(link, snapshot, condition) -> PositionSignalLinkResponse:
    """
    Формирует API-ответ с данными привязки сигнала к позиции.
    """
    return PositionSignalLinkResponse(
        id=link.id,
        symbol=link.symbol,
        signal=_make_snapshot_response(snapshot),
        close_condition=_make_condition_response(condition),
        created_at=link.created_at,
    )
 
 
def _make_order_link_response(link, snapshot, condition) -> OrderSignalLinkResponse:
    """
    Формирует API-ответ с данными привязки сигнала к ордеру.
    """
    return OrderSignalLinkResponse(
        id=link.id,
        symbol=link.symbol,
        exchange_order_id=link.exchange_order_id,
        signal=_make_snapshot_response(snapshot),
        close_condition=_make_condition_response(condition),
        created_at=link.created_at,
    )


@router.get("", response_model=SignalLinksResponse)
def get_signal_links(session: Session = Depends(get_session)):
    """
    Возвращает все активные привязки позиций и ордеров.
    """
    service = SignalLinkService(session)

    position_links_data = service.list_position_links_with_signals()
    order_links_data = service.list_order_links_with_signals()

    return SignalLinksResponse(
        positions=[
            _make_position_link_response(link, snapshot, condition)
            for link, snapshot, condition in position_links_data
        ],
        orders=[
            _make_order_link_response(link, snapshot, condition)
            for link, snapshot, condition in order_links_data
        ],
    )


@router.get("/values", response_model=list[CurrentIndicatorValueResponse])
def get_linked_signal_values(tf: str):
    """
    Возвращает текущие значения индикаторов для привязанных сигналов
    указанного таймфрейма.
    """
    data = read_json(LINKED_VALUES_FILE, default={})
    return LINKED_VALUES_ADAPTER.validate_python(data.get(tf, []))


@router.post("/positions", response_model=PositionSignalLinkResponse)
def link_signal_to_position(
    req: LinkPositionSignalRequest, 
    session: Session = Depends(get_session),
):
    """
    Привязывает сигнал к позиции и сохраняет данные в БД.
    """
    service = SignalLinkService(session)
    try:
        link, snapshot, condition = service.create_position_link(req)
    except PositionAlreadyLinkedError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return _make_position_link_response(link, snapshot, condition)


@router.put("/positions/{link_id}", response_model=PositionSignalLinkResponse)
def update_position_signal_link(
    link_id: int, 
    req: UpdateSignalLinkRequest,
    session: Session = Depends(get_session),
):
    """
    Изменяет сигнал и условие автозакрытия существующей привязки позиции.
    """
    service = SignalLinkService(session)
    try:
        link, snapshot, condition = service.update_position_link(link_id, req)
    except (SignalLinkNotFoundError, SignalSnapshotNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))

    return _make_position_link_response(link, snapshot, condition)


@router.delete("/positions/{link_id}", response_model=ActionResponse)
def unlink_signal_from_position(link_id: int, session: Session = Depends(get_session)):
    """
    Удаляет привязку сигнала от позиции по ID.
    """
    service = SignalLinkService(session)
    try:
        service.delete_position_link(link_id)
    except SignalLinkNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ActionResponse(success=True)


@router.post("/orders", response_model=OrderSignalLinkResponse)
def link_signal_to_order(
    req: LinkOrderSignalRequest, 
    session: Session = Depends(get_session)
):
    """
    Привязывает сигнал к открытому ордеру и сохраняет данные в БД.
    """
    service = SignalLinkService(session)
    try:
        link, snapshot, condition = service.create_order_link(req)
    except OrderAlreadyLinkedError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return _make_order_link_response(link, snapshot, condition)


@router.put("/orders/{link_id}", response_model=OrderSignalLinkResponse)
def update_order_signal_link(
    link_id: int, 
    req: UpdateSignalLinkRequest,
    session: Session = Depends(get_session),
):
    """
    Изменяет сигнал и условие автозакрытия существующей привязки ордера.
    """
    service = SignalLinkService(session)
    try:
        link, snapshot, condition = service.update_order_link(link_id, req)
    except (SignalLinkNotFoundError, SignalSnapshotNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))

    return _make_order_link_response(link, snapshot, condition)


@router.delete("/orders/{link_id}", response_model=ActionResponse)
def unlink_signal_from_order(link_id: int, session: Session = Depends(get_session)):
    """
    Удаляет привязку сигнала от ордера по ID.
    """
    service = SignalLinkService(session)
    try:
        service.delete_order_link(link_id)
    except SignalLinkNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return ActionResponse(success=True)