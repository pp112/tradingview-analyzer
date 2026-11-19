from sqlmodel import Session

from backend.exchanges.models import Order, Position
from backend.signal_links.repository import CloseConditionRepository, OrderSignalLinkRepository, PositionSignalLinkRepository, SignalSnapshotRepository


def sync_order_links_to_positions(
    session: Session,
    exchange_orders: list[Order],
    exchange_positions: list[Position],
) -> None:
    """
    Переносит привязку сигнала от исполненного ордера к появившейся позиции.

    Принимает уже полученные с биржи списки ордеров/позиций (никаких
    дополнительных запросов к бирже сама не делает) и сверяет их с активными
    привязками ордеров:
      - если привязанный ордер всё ещё среди открытых — ничего не делаем;
      - если ордера больше нет среди открытых и по тому же символу есть
        открытая позиция без собственной привязки — переносим сигнал
        и условие автозакрытия на новую PositionSignalLink, а привязку
        ордера закрываем (не удаляя сигнал/условие — их теперь использует
        позиция);
      - если ордера нет и позиции тоже нет — закрываем привязку ордера и
        подчищаем её сигнал/условие, как при ручной отвязке.
    """
    order_repo = OrderSignalLinkRepository(session)
    position_repo = PositionSignalLinkRepository(session)
    snapshot_repo = SignalSnapshotRepository(session)
    condition_repo = CloseConditionRepository(session)

    active_order_links = order_repo.get_all_active()
    if not active_order_links:
        return

    active_exchange_order_ids = {o.exchange_order_id for o in exchange_orders}
    positions_by_symbol = {p.symbol: p for p in exchange_positions}

    for link in active_order_links:
        if link.exchange_order_id in active_exchange_order_ids:
            continue # ордер все еще открыт на бирже - переносить рано

        position = positions_by_symbol.get(link.symbol)

        if position is not None and position_repo.get_by_symbol(link.symbol) is None:
            position_repo.create_from_order_link(link)
            order_repo.mark_cancelled(link)
            continue

        # Ордер пропал с биржи, но позиция либо не появилась (отменён/отклонён),
        # либо по символу уже есть своя привязка — просто закрываем эту привязку.
        order_repo.mark_cancelled(link)
        snapshot_repo.delete(link.signal_snapshot_id)
        if link.close_condition_id is not None:
            condition_repo.delete(link.close_condition_id)
