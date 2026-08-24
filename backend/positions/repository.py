from sqlmodel import Session, select

from backend.positions.models import (
    CloseCondition, 
    SignalSnapshot, 
    TrackedOrder, 
    TrackedPosition,
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


class TrackedPositionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, tracked: TrackedPosition) -> TrackedPosition:
        self.session.add(tracked)
        self.session.commit()
        self.session.refresh(tracked)
        return tracked

    def get_all_active(self) -> list[TrackedPosition]:
        query = select(TrackedPosition).where(
            TrackedPosition.closed_at.is_(None)
        )
        return list(self.session.exec(query))


class TrackedOrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, tracked: TrackedOrder) -> TrackedOrder:
        self.session.add(tracked)
        self.session.commit()
        self.session.refresh(tracked)
        return tracked

    def get_all_active(self) -> list[TrackedOrder]:
        query = select(TrackedOrder).where(
            TrackedOrder.cancelled_at.is_(None)
        )
        return list(self.session.exec(query))