from sqlmodel import Session

from backend.exchanges.models import Order, Position
from backend.signal_links.repository import OrderSignalLinkRepository


def sync_order_links_to_position(
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


    active_order_links = order_repo.get_all_active()
    if not active_order_links:
        return
    
    