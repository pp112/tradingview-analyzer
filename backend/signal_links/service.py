from sqlmodel import Session

from backend.schemas.signal_links import (
    CloseConditionInput,
    LinkOrderSignalRequest,
    LinkPositionSignalRequest, 
    SignalSnapshotInput, 
    UpdateSignalLinkRequest,
)
from backend.signal_links.models import (
    CloseCondition, 
    OrderSignalLink, 
    PositionSignalLink, 
    SignalSnapshot,
)
from backend.signal_links.repository import (
    CloseConditionRepository, 
    OrderSignalLinkRepository, 
    PositionSignalLinkRepository, 
    SignalSnapshotRepository,
)


class SignalLinkNotFoundError(Exception):
    """Привязка с таким id не найдена или уже закрыта/отменена."""


class SignalSnapshotNotFoundError(Exception):
    """Привязанный к link сигнал не найден в БД (данные рассинхронизированы)."""


class PositionAlreadyLinkedError(Exception):
    """У позиции с этим symbol уже есть активная привязка сигнала."""


class OrderAlreadyLinkedError(Exception):
    """У ордера с этим exchange_order_id уже есть привязка сигнала."""


class SignalLinkService:
    """
    Бизнес-логика привязки сигналов к позициям и ордерам.
    """

    def __init__(self, session: Session):
        self.position_repo = PositionSignalLinkRepository(session)
        self.order_repo = OrderSignalLinkRepository(session)
        self.snapshot_repo = SignalSnapshotRepository(session)
        self.condition_repo = CloseConditionRepository(session)

    def create_position_link(
        self, 
        req: LinkPositionSignalRequest
    ) -> tuple[PositionSignalLink, SignalSnapshot, CloseCondition | None]:
        """
        Привязывает сигнал к позиции. 
        Бросает PositionAlreadyLinkedError, если у позиции уже есть активная привязка.
        """
        if self.position_repo.get_by_symbol(req.symbol):
            raise PositionAlreadyLinkedError(f"Позиция {req.symbol} уже привязана к сигналу")

        snapshot, condition = self._create_snapshot_and_condition(
            req.signal, req.close_condition, req.symbol
        )

        link = self.position_repo.create(PositionSignalLink(
            symbol=req.symbol,
            signal_snapshot_id=snapshot.id,
            close_condition_id=condition.id if condition else None
        ))
        return link, snapshot, condition 

    def create_order_link(
        self,
        req: LinkOrderSignalRequest
    ) -> tuple[OrderSignalLink, SignalSnapshot, CloseCondition | None]:
        """
        Привязывает сигнал к ордеру. 
        Бросает OrderAlreadyLinkedError, если у ордера уже есть привязка.
        """
        if self.order_repo.get_by_exchange_order_id(req.exchange_order_id):
            raise OrderAlreadyLinkedError(f"Ордер {req.exchange_order_id} уже привязан к сигналу")

        snapshot, condition = self._create_snapshot_and_condition(
            req.signal, req.close_condition, req.symbol
        )

        link = self.order_repo.create(OrderSignalLink(
            symbol=req.symbol,
            exchange_order_id=req.exchange_order_id,
            signal_snapshot_id=snapshot.id,
            close_condition_id=condition.id if condition else None
        ))
        return link, snapshot, condition

    def update_position_link(
        self, 
        link_id: int, 
        req: UpdateSignalLinkRequest
    ) -> tuple[PositionSignalLink, SignalSnapshot, CloseCondition | None]:
        """
        Изменяет сигнал и условие автозакрытия привязки позиции.
        Бросает SignalLinkNotFoundError / SignalSnapshotNotFoundError.
        """
        link = self.position_repo.get_by_id(link_id)
        if link is None or link.closed_at is not None:
            raise SignalLinkNotFoundError(f"Привязка позиции id={link_id} не найдена")

        snapshot, condition = self._update_snapshot_and_close_condition(link, req)
        return link, snapshot, condition

    def update_order_link(
        self,
        link_id: int,
        req: UpdateSignalLinkRequest
    ) -> tuple[PositionSignalLink, SignalSnapshot, CloseCondition | None]:
        """
        Изменяет сигнал и условие автозакрытия привязки ордера.
        Бросает SignalLinkNotFoundError / SignalSnapshotNotFoundError.
        """
        link = self.order_repo.get_by_id(link_id)
        if link is None or link.cancelled_at is not None:
            raise SignalLinkNotFoundError(f"Привязка ордера id={link_id} не найдена")

        snapshot, condition = self._update_snapshot_and_close_condition(link, req)
        return link, snapshot, condition

    def delete_position_link(self, link_id: int) -> None:
        """
        Удаляет привязку сигнала от позиции вместе с её сигналом и условием.
        Бросает SignalLinkNotFoundError, если привязка не найдена.
        """
        link = self.position_repo.get_by_id(link_id)
        if link is None:
            raise SignalLinkNotFoundError(f"Привязка позиции id={link_id} не найдена")

        self.snapshot_repo.delete(link.signal_snapshot_id)
        if link.close_condition_id is not None:
            self.condition_repo.delete(link.close_condition_id)
        self.position_repo.delete(link_id)

    def delete_order_link(self, link_id: int) -> None:
        """
        Удаляет привязку сигнала от ордера вместе с её сигналом и условием.
        Бросает SignalLinkNotFoundError, если привязка не найдена.
        """
        link = self.order_repo.get_by_id(link_id)
        if link is None:
            raise SignalLinkNotFoundError("Привязка не найдена")
 
        self.snapshot_repo.delete(link.signal_snapshot_id)
        if link.close_condition_id is not None:
            self.condition_repo.delete(link.close_condition_id)
        self.order_repo.delete(link_id)

    def list_position_links_with_signals(
        self,
    ) -> list[tuple[PositionSignalLink, SignalSnapshot, CloseCondition | None]]:
        """
        Собирает все активные привязки позиций (у которых closed_at = None)
        вместе с их сигналом и условием закрытия.
        """
        links = self.position_repo.get_all_active()
        return self._list_links_with_signals(links)

    def list_order_links_with_signals(
        self,
    ) -> list[tuple[OrderSignalLink, SignalSnapshot, CloseCondition | None]]:
        """
        Собирает все активные привязки ордеров (у которых cancelled_at = None)
        вместе с их сигналом и условием закрытия.
        """
        links = self.order_repo.get_all_active()
        return self._list_links_with_signals(links)

    def _create_snapshot_and_condition(
        self,
        signal: SignalSnapshotInput,
        close_condition: CloseConditionInput | None,
        symbol: str,
    ) -> tuple[SignalSnapshot, CloseCondition | None]:
        """
        Создает в БД SignalSnapshot и опционально CloseCondition.
        """
        snapshot = self.snapshot_repo.create(SignalSnapshot(
            symbol=symbol,
            indicator=signal.indicator,
            timeframe=signal.timeframe,
            value=signal.value,
            direction=signal.direction
        ))
        condition = None
        if close_condition is not None:
            condition = self.condition_repo.create(self._build_close_condition(close_condition))
        return snapshot, condition

    def _update_snapshot_and_close_condition(
        self,
        link: PositionSignalLink | OrderSignalLink,
        req: UpdateSignalLinkRequest,
    ) -> tuple[SignalSnapshot, CloseCondition | None]:
        """
        Обновляет привязанный сигнал и условия закрытия существующей привязки
        Бросает SignalSnapshotNotFoundError, если снимок сигнала, 
        указанный в привязке, отсутствует в БД.
        """
        if isinstance(link, PositionSignalLink):
            link_repo = self.position_repo
        elif isinstance(link, OrderSignalLink):
            link_repo = self.order_repo

        curr_snapshot = self.snapshot_repo.get_by_id(link.signal_snapshot_id)
        if curr_snapshot is None:
            raise SignalSnapshotNotFoundError(f"Сигнал привязки {link.id} не найден")

        self.snapshot_repo.update(
            snapshot=curr_snapshot,
            indicator=req.signal.indicator,
            timeframe=req.signal.timeframe,
            value=req.signal.value,
            direction=req.signal.direction,
        )

        curr_condition = (
            self.condition_repo.get_by_id(link.close_condition_id) 
            if link.close_condition_id is not None 
            else None
        )

        new_condition = req.close_condition

        if new_condition is None:
            if curr_condition is not None:
                link_repo.set_close_condition(link, None)
                self.condition_repo.delete(curr_condition.id)
                curr_condition = None
        elif curr_condition is None:
            curr_condition = self.condition_repo.create(self._build_close_condition(new_condition))
            link_repo.set_close_condition(link, curr_condition.id)
        else:
            if new_condition.type == "crossover":
                self.condition_repo.update(
                    curr_condition, close_type="crossover", operator=None, target_value=None
                )
            else:
                self.condition_repo.update(
                    curr_condition,
                    close_type="value",
                    operator=new_condition.operator,
                    target_value=new_condition.target_value,
                )

        return curr_snapshot, curr_condition

    def _list_links_with_signals(
        self,
        links: list[PositionSignalLink] | list[OrderSignalLink],
    ) -> list[tuple[PositionSignalLink | OrderSignalLink, SignalSnapshot, CloseCondition | None]]:
        """
        Общая часть сборки списка привязок вместе с их сигналом и условием,
        используется для позиций и для ордеров.
        """
        result = []
        for link in links:
            signal_data = self._load_signal_and_condition(link)
            if signal_data is None:
                continue
            snapshot, condition = signal_data
            result.append((link, snapshot, condition))
        return result

    def _load_signal_and_condition(
        self,
        link: PositionSignalLink | OrderSignalLink,
    ) -> tuple[SignalSnapshot, CloseCondition | None] | None:
        """
        Находит привязанные к link сигнал и условие закрытия.
        Возвращает None, если сигнал не найден (привязка "осиротела").
        """
        snapshot = self.snapshot_repo.get_by_id(link.signal_snapshot_id)
        if snapshot is None:
            return None
        
        condition = (
            self.condition_repo.get_by_id(link.close_condition_id)
            if link.close_condition_id
            else None
        )
        return snapshot, condition

    @staticmethod
    def _build_close_condition(condition: CloseConditionInput) -> CloseCondition:
        """
        Строит SQLModel-объект CloseCondition из входных данных запроса.
        """
        if condition.type == "crossover":
            return CloseCondition(close_type="crossover")
        return CloseCondition(
            close_type="value",
            operator=condition.operator,
            target_value=condition.target_value,
        )