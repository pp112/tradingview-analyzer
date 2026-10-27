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


def _condition_met(value: float, condition: CloseCondition) -> bool:
    if condition.operator == "<=":
        return value <= condition.target_value
    if condition.operator == ">=":
        return value >= condition.target_value
    return False


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
        (v.symbol, v.indicator.value): v.value 
        for v in linked_indicator_values
    }

    for link in position_repo.get_all_active():
        if link.close_condition_id is None:
            continue

        snapshot = snapshot_repo.get_by_id(link.signal_snapshot_id)
        condition = condition_repo.get_by_id(link.close_condition_id)
        if snapshot is None or condition is None:
            continue

        value = values_by_key.get((snapshot.symbol, snapshot.indicator))
        if value is None:
            continue

        if not _condition_met(value, condition):
            continue

        logger.info(
            f"Автозакрытие позиции: {link.symbol}"
            f"{snapshot.indicator}={value} {condition.operator} {condition.target_value}"
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

        value = values_by_key.get((snapshot.symbol, snapshot.indicator))
        if value is None:
            continue

        if not _condition_met(value, condition):
            continue

        logger.info(
            f"Автоотмена ордера: {link.symbol}"
            f"{snapshot.indicator}={value} {condition.operator} {condition.target_value}"
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

        