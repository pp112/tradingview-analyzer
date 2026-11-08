from sqlmodel import Session

from backend.config.logging import get_logger
from backend.exchanges.base import ExchangeApiError, ExchangeClient
from backend.models.linked_values import CurrentIndicatorValue
from backend.signal_links.models import CloseCondition
from backend.signal_links.repository import (
    CloseConditionRepository,
    OrderSignalLinkRepository,
    PositionSignalLinkRepository,
    SignalSnapshotRepository,
)

logger = get_logger(__name__, "[AUTO-CLOSE]")


def _value_condition_met(value: float, condition: CloseCondition) -> bool:
    if condition.operator == "<=":
        return value <= condition.target_value
    if condition.operator == ">=":
        return value >= condition.target_value
    return False


def _crossover_condition_met(
    crossover_index: int,
    condition: CloseCondition,
    condition_repo: CloseConditionRepository,
) -> bool:
    """
    Условие "закрыть при следующем пересечении".
    На первой проверке опорного индекса ещё нет — он просто запоминается. 
    На всех следующих проверках, если индекс последнего пересечения стал 
    больше опорного, значит произошло новое пересечение — условие срабатывает.
    """
    if condition.reference_crossover_index is None:
        condition_repo.set_reference_crossover_index(condition, crossover_index)
        return False
    
    return crossover_index > condition.reference_crossover_index


def _condition_met(
    current: CurrentIndicatorValue, 
    condition: CloseCondition, 
    condition_repo: CloseConditionRepository,
) -> bool:
    if condition.close_type == "crossover":
        return _crossover_condition_met(current.crossover_index, condition, condition_repo)
    return _value_condition_met(current.value, condition)


def _describe(indicator: str, current: CurrentIndicatorValue, condition: CloseCondition) -> str:
    if condition.close_type == "crossover":
        return f"{indicator}: новое пересечение (index={current.crossover_index})"
    return f"{indicator}={current.value} {condition.operator} {condition.target_value}"


async def check_and_auto_close(
    linked_indicator_values: list[CurrentIndicatorValue],
    session: Session,
    client: ExchangeClient,
) -> None:
    """
    Сравнивает текущие значения индикаторов с условиями автозакрытия
    и закрывает позицию / отменяет ордер при срабатывании.
    """
    position_repo = PositionSignalLinkRepository(session)
    order_repo = OrderSignalLinkRepository(session)
    snapshot_repo = SignalSnapshotRepository(session)
    condition_repo = CloseConditionRepository(session)

    values_by_key = {
        (v.symbol, v.indicator.value): v
        for v in linked_indicator_values
    }

    for link in position_repo.get_all_active():
        if link.close_condition_id is None:
            continue

        snapshot = snapshot_repo.get_by_id(link.signal_snapshot_id)
        condition = condition_repo.get_by_id(link.close_condition_id)
        if snapshot is None or condition is None:
            continue

        current = values_by_key.get((snapshot.symbol, snapshot.indicator))
        if current is None:
            continue

        if not _condition_met(current, condition, condition_repo):
            continue

        logger.info(
            f"Автозакрытие позиции: {link.symbol}"
            f"{_describe(snapshot.indicator, current, condition)}"
        )

        try:
            positions = await client.get_positions()
            position = next((p for p in positions if p.symbol == link.symbol), None)
            if position is None:
                logger.warning(f"Позиция {link.symbol} не найдена на бирже, помечаем закрытой")
                position_repo.mark_closed(link)
                continue

            success = await client.close_position(position)
            if success:
                position_repo.mark_closed(link)
            else:
                logger.error(f"Не удалось закрыть позицию {link.symbol}")
        except ExchangeApiError as e:
            logger.error(f"Ошибка биржи при закрытии позиции {link.symbol}: {e}")

    for link in order_repo.get_all_active():
        if link.close_condition_id is None:
            continue

        snapshot = snapshot_repo.get_by_id(link.signal_snapshot_id)
        condition = condition_repo.get_by_id(link.close_condition_id)
        if snapshot is None or condition is None:
            continue

        current = values_by_key.get((snapshot.symbol, snapshot.indicator))
        if current is None:
            continue

        if not _condition_met(current, condition, condition_repo):
            continue

        logger.info(
            f"Автоотмена ордера: {link.symbol}"
            f"{_describe(snapshot.indicator, current, condition)}"
        )

        try:
            orders = await client.get_orders()
            order = next(
                (o for o in orders if o.exchange_order_id == link.exchange_order_id),
                None
            )
            if order is None:
                logger.warning(f"Ордер {link.symbol} не найден на бирже, помечаем отменённым")
                order_repo.mark_cancelled(link)
                continue

            success = await client.cancel_order(order)
            if success:
                order_repo.mark_cancelled(link)
            else:
                logger.error(f"Не удалось отменить ордер {link.symbol}")
        except ExchangeApiError as e:
            logger.error(f"Ошибка биржи при отмене ордера {link.symbol}: {e}")

        