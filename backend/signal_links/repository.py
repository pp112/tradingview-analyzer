from datetime import datetime

from sqlmodel import Session, select

from backend.signal_links.models import (
    CloseCondition, 
    SignalSnapshot, 
    OrderSignalLink, 
    PositionSignalLink,
)


class SignalSnapshotRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, snapshot: SignalSnapshot) -> SignalSnapshot:
        self.session.add(snapshot)
        self.session.flush()
        self.session.refresh(snapshot)
        return snapshot

    def get_by_id(self, snapshot_id: int) -> SignalSnapshot | None:
        return self.session.get(SignalSnapshot, snapshot_id)

    def update(
        self,
        snapshot: SignalSnapshot,
        indicator: str,
        timeframe: str,
        value: float,
        direction: str,
    ) -> SignalSnapshot:
        snapshot.indicator = indicator
        snapshot.timeframe = timeframe
        snapshot.value = value
        snapshot.direction = direction
        self.session.flush()
        return snapshot

    def delete(self, snapshot_id: int):
        snapshot = self.session.get(SignalSnapshot, snapshot_id)
        if snapshot:
            self.session.delete(snapshot)


class CloseConditionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, condition: CloseCondition) -> CloseCondition:
        self.session.add(condition)
        self.session.flush()
        self.session.refresh(condition)
        return condition

    def get_by_id(self, condition_id: int) -> CloseCondition | None:
        return self.session.get(CloseCondition, condition_id)

    def update(
        self,
        condition: CloseCondition,
        operator: str,
        target_value: float,
    ) -> CloseCondition:
        condition.operator = operator
        condition.target_value = target_value
        self.session.flush()
        return condition

    def delete(self, condition_id: int):
        condition = self.session.get(CloseCondition, condition_id)
        if condition:
            self.session.delete(condition)


class PositionSignalLinkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, link: PositionSignalLink) -> PositionSignalLink:
        self.session.add(link)
        self.session.flush()
        self.session.refresh(link)
        return link

    def get_by_id(self, link_id: int) -> PositionSignalLink | None:
        return self.session.get(PositionSignalLink, link_id)

    def get_all_active(self) -> list[PositionSignalLink]:
        query = select(PositionSignalLink).where(
            PositionSignalLink.closed_at.is_(None)
        )
        return list(self.session.exec(query))

    def get_by_symbol(self, symbol: str) -> PositionSignalLink | None:
        query = select(PositionSignalLink).where(
            PositionSignalLink.symbol == symbol,
            PositionSignalLink.closed_at.is_(None),
        )
        return self.session.exec(query).first()

    def mark_closed(self, link: PositionSignalLink) -> PositionSignalLink:
        link.closed_at = datetime.now()
        self.session.flush()
        return link

    def set_close_condition(
        self,
        link: PositionSignalLink,
        condition_id: int | None,
    ) -> PositionSignalLink:
        link.close_condition_id = condition_id
        self.session.flush()
        return link

    def delete(self, link_id: int):
        link = self.session.get(PositionSignalLink, link_id)
        if link:
            self.session.delete(link)


class OrderSignalLinkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, link: OrderSignalLink) -> OrderSignalLink:
        self.session.add(link)
        self.session.flush()
        self.session.refresh(link)
        return link

    def get_all_active(self) -> list[OrderSignalLink]:
        query = select(OrderSignalLink).where(
            OrderSignalLink.cancelled_at.is_(None)
        )
        return list(self.session.exec(query))

    def get_by_id(self, link_id: int) -> OrderSignalLink | None:
        return self.session.get(OrderSignalLink, link_id)

    def get_by_exchange_order_id(
        self,
        exchange_order_id: str,
    ) -> OrderSignalLink | None:
        query = select(OrderSignalLink).where(
            OrderSignalLink.exchange_order_id == exchange_order_id,
            OrderSignalLink.cancelled_at.is_(None),
        )
        return self.session.exec(query).first()

    def set_close_condition(
        self,
        link: OrderSignalLink,
        condition_id: int | None,
    ) -> OrderSignalLink:
        link.close_condition_id = condition_id
        self.session.flush()
        return link

    def delete(self, link_id: int):
        link = self.session.get(OrderSignalLink, link_id)
        if link:
            self.session.delete(link)

    def mark_cancelled(self, link: OrderSignalLink) -> OrderSignalLink:
        link.cancelled_at = datetime.now()
        self.session.flush()
        return link