from sqlmodel import Session, select

from backend.positions.models import (
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
        self.session.commit()
        self.session.refresh(snapshot)
        return snapshot

    def get_by_id(self, snapshot_id: int) -> SignalSnapshot | None:
        return self.session.get(SignalSnapshot, snapshot_id)

    def delete(self, snapshot_id: int):
        snapshot = self.session.get(SignalSnapshot, snapshot_id)
        if snapshot:
            self.session.delete(snapshot)
            self.session.commit()


class CloseConditionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, condition: CloseCondition) -> CloseCondition:
        self.session.add(condition)
        self.session.commit()
        self.session.refresh(condition)
        return condition

    def get_by_id(self, condition_id: int) -> CloseCondition | None:
        return self.session.get(CloseCondition, condition_id)

    def delete(self, condition_id: int):
        condition = self.session.get(CloseCondition, condition_id)
        if condition:
            self.session.delete(condition)
            self.session.commit()


class PositionSignalLinkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, link: PositionSignalLink) -> PositionSignalLink:
        self.session.add(link)
        self.session.commit()
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

    def delete(self, link_id: int):
        link = self.session.get(PositionSignalLink, link_id)
        if link:
            self.session.delete(link)
            self.session.commit()


class OrderSignalLinkRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, link: OrderSignalLink) -> OrderSignalLink:
        self.session.add(link)
        self.session.commit()
        self.session.refresh(link)
        return link

    def get_all_active(self) -> list[OrderSignalLink]:
        query = select(OrderSignalLink).where(
            OrderSignalLink.cancelled_at.is_(None)
        )
        return list(self.session.exec(query))

    def get_by_id(self, order_id: str) -> OrderSignalLink | None:
        return self.session.get(OrderSignalLink, order_id)

    def get_by_order_id(self, order_id: str) -> OrderSignalLink | None:
        query = select(OrderSignalLink).where(
            OrderSignalLink.order_id == order_id,
            OrderSignalLink.cancelled_at.is_(None),
        )
        return self.session.exec(query).first()

    def delete(self, link_id: int):
        link = self.session.get(OrderSignalLink, link_id)
        if link:
            self.session.delete(link)
            self.session.commit()