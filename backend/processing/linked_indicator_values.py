from sqlmodel import Session

from backend.models.linked_values import CurrentIndicatorValue
from backend.models.timeframe import Timeframe
from backend.positions.repository import OrderSignalLinkRepository, PositionSignalLinkRepository, SignalSnapshotRepository


def extract_linked_indicator_values(
    indicators: dict[str, dict],
    timeframe: Timeframe,
    session: Session
) -> list[CurrentIndicatorValue]:
    order_repo = OrderSignalLinkRepository(session)
    position_repo = PositionSignalLinkRepository(session)
    snapshot_repo = SignalSnapshotRepository(session)

    all_links = [
        *position_repo.get_all_active(),
        *order_repo.get_all_active()
    ]

    if not all_links:
        return []

    result = []
    for link in all_links:
        snapshot = snapshot_repo.get_by_id(link.signal_snapshot_id)
        if snapshot is None or snapshot.timeframe != timeframe.label:
            continue

        symbol_data = indicators.get(snapshot.symbol)
        if symbol_data is None:
            continue

        value = _extract_value(symbol_data, snapshot.indicator)
        result.append(CurrentIndicatorValue(
            symbol=snapshot.symbol,
            indicator=snapshot.indicator,
            value=value
        ))
    return result


def _extract_value(symbol_data: dict, indicator: str) -> float:
    """
    Извлекает числовое значение индикатора из структуры данных символа.
    """
    if indicator == "rsi":
        return round(symbol_data.get("rsi"), 2)

    if indicator == "macd":
        curr = symbol_data.get("macd").get("curr")
        return round(curr["MACD"] - curr["MACD_signal"], 2)

    if indicator == "ema_sma":
        ema = symbol_data.get("ema")
        sma = symbol_data.get("sma")
        return round(sma - ema, 2)

    if indicator == "vol_ratio":
        return round(symbol_data.get("volume").get("curr"), 2)



        