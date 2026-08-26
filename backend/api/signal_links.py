from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.positions.models import (
    CloseCondition,
    OrderSignalLink,
    PositionSignalLink, 
    SignalSnapshot,
)
from backend.positions.repository import (
    CloseConditionRepository,
    OrderSignalLinkRepository,
    PositionSignalLinkRepository, 
    SignalSnapshotRepository,
)
from backend.positions.schemas import (
    CloseConditionInput,
    CloseConditionResponse,
    LinkOrderSignalRequest,
    LinkPositionSignalRequest,
    OrderSignalLinkResponse,
    PositionSignalLinkResponse,
    SignalSnapshotInput,
    SignalSnapshotResponse,
)
from backend.storage.database import get_session


router = APIRouter(prefix="/links")


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


def _make_condition_response(condition: CloseCondition | None) -> CloseConditionResponse | None:
    """
    Преобразует SQLModel-объект в Pydantic-схему для API-ответа.
    """
    if condition is None:
        return None
    return CloseConditionResponse(
        id=condition.id,
        operator=condition.operator,
        target_value=condition.target_value
    )


def _create_snapshot_and_condition(
    signal: SignalSnapshotInput,
    close_condition: CloseConditionInput | None,
    symbol: str,
    snapshot_repo: SignalSnapshotRepository,
    condition_repo: CloseConditionRepository
) -> tuple[SignalSnapshot, CloseCondition | None]:
    """
    Создает в БД SignalSnapshot и опционально CloseCondition.
    """
    snapshot = snapshot_repo.create(SignalSnapshot(
        symbol=symbol,
        indicator=signal.indicator,
        timeframe=signal.timeframe,
        value=signal.value,
        direction=signal.direction
    ))
    condition = None
    if close_condition is not None:
        condition = condition_repo.create(CloseCondition(
            operator=close_condition.operator,
            target_value=close_condition.target_value
        ))
    return snapshot, condition


@router.post("/positions", response_model=PositionSignalLinkResponse)
def link_signal_to_position(req: LinkPositionSignalRequest, session: Session = Depends(get_session)):
    """
    Привязывает сигнал к позиции и сохраняет данные в БД.
    """
    snapshot_repo = SignalSnapshotRepository(session)
    condition_repo = CloseConditionRepository(session)
    position_repo = PositionSignalLinkRepository(session)

    existing = position_repo.get_by_symbol(req.symbol)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Позиция {req.symbol} уже привязана к сигналу"
        )

    snapshot, condition = _create_snapshot_and_condition(
        req.signal, req.close_condition, req.symbol, snapshot_repo, condition_repo
    )

    position_link = position_repo.create(PositionSignalLink(
        symbol=req.symbol,
        signal_snapshot_id=snapshot.id,
        close_condition_id=condition.id if condition else None
    ))

    return PositionSignalLinkResponse(
        id=position_link.id,
        symbol=position_link.symbol,
        signal=_make_snapshot_response(snapshot),
        close_condition=_make_condition_response(condition)
    )


@router.get("/positions", response_model=list[PositionSignalLinkResponse])
def get_position_signals(session: Session = Depends(get_session)):
    """
    Возвращает все активные привязки позиций (у которых closed_at = None).
    """
    snapshot_repo = SignalSnapshotRepository(session)
    condition_repo = CloseConditionRepository(session)
    position_repo = PositionSignalLinkRepository(session)

    result = []
    for position_link in position_repo.get_all_active():
        snapshot = snapshot_repo.get_by_id(position_link.signal_snapshot_id)
        if snapshot is None:
            continue

        condition = (
            condition_repo.get_by_id(position_link.close_condition_id)
            if position_link.close_condition_id
            else None
        )

        result.append(PositionSignalLinkResponse(
            id=position_link.id,
            symbol=position_link.symbol,
            signal=_make_snapshot_response(snapshot),
            close_condition=_make_condition_response(condition)
        ))

    return result


@router.delete("/positions/{link_id}")
def unlink_signal_from_position(link_id: int, session: Session = Depends(get_session)):
    """
    Удаляет привязку сигнала от позиции по ID.
    """
    snapshot_repo = SignalSnapshotRepository(session)
    condition_repo = CloseConditionRepository(session)
    position_repo = PositionSignalLinkRepository(session)

    if not session.get(PositionSignalLink, link_id):
        raise HTTPException(status_code=404, detail="Привязка не найдена")

    position_link = position_repo.get_by_id(link_id)

    snapshot_repo.delete(position_link.signal_snapshot_id)

    if position_link.close_condition_id is not None:
        condition_repo.delete(position_link.close_condition_id)

    position_repo.delete(link_id)

    return {"success": True}


@router.post("/orders", response_model=OrderSignalLinkResponse)
def link_signal_to_order(req: LinkOrderSignalRequest, session: Session = Depends(get_session)):
    """
    Привязывает сигнал к открытому ордеру и сохраняет данные в БД.
    """
    snapshot_repo = SignalSnapshotRepository(session)
    condition_repo = CloseConditionRepository(session)
    order_repo = OrderSignalLinkRepository(session)

    existing = order_repo.get_by_order_id(req.order_id)
    if existing:
        raise HTTPException(
            status_code=409, 
            detail=f"Ордер {req.order_id} уже привязан к сигналу"
        )

    snapshot, condition = _create_snapshot_and_condition(
        req.signal, req.close_condition, req.symbol, snapshot_repo, condition_repo
    )

    order_link = order_repo.create(OrderSignalLink(
        symbol=req.symbol,
        order_id=req.order_id,
        signal_snapshot_id=snapshot.id,
        close_condition_id=condition.id if condition else None
    ))

    return OrderSignalLinkResponse(
        id=order_link.id,
        symbol=order_link.symbol,
        order_id=order_link.order_id,
        signal=_make_snapshot_response(snapshot),
        close_condition=_make_condition_response(condition)
    )


@router.get("/orders", response_model=list[OrderSignalLinkResponse])
def get_order_signals(session: Session = Depends(get_session)):
    """
    Возвращает все активные привязки ордеров (у которых cancelled_at = None).
    """
    snapshot_repo = SignalSnapshotRepository(session)
    condition_repo = CloseConditionRepository(session)
    order_repo = OrderSignalLinkRepository(session)

    result = []
    for order_link in order_repo.get_all_active():
        snapshot = snapshot_repo.get_by_id(order_link.signal_snapshot_id)
        if snapshot is None:
            continue

        condition = (
            condition_repo.get_by_id(order_link.close_condition_id)
            if order_link.close_condition_id
            else None
        )

        result.append(OrderSignalLinkResponse(
            id=order_link.id,
            symbol=order_link.symbol,
            order_id=order_link.order_id,
            signal=_make_snapshot_response(snapshot),
            close_condition=_make_condition_response(condition)
        ))

    return result


@router.delete("/orders/{link_id}")
def unlink_signal_from_order(link_id: int, session: Session = Depends(get_session)):
    """
    Удаляет привязку сигнала от ордера по ID.
    """
    snapshot_repo = SignalSnapshotRepository(session)
    condition_repo = CloseConditionRepository(session)
    order_repo = OrderSignalLinkRepository(session)

    order_link = order_repo.get_by_id(link_id)
    if order_link is None:
        raise HTTPException(status_code=404, detail="Привязка не найдена")

    snapshot_repo.delete(order_link.signal_snapshot_id)

    if order_link.close_condition_id is not None:
        condition_repo.delete(order_link.close_condition_id)

    order_repo.delete(link_id)

    return {"success": True}