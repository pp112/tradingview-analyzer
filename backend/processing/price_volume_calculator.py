import pandas as pd

from backend.models import PriceVolume


def calculate_price_volume_changes(df: pd.DataFrame) -> list[PriceVolume]:
    """
    Вычисляет процентное изменение цены и объёма для каждого символа.
    """
    changes = []
    for symbol, group in df.groupby("symbol"):
        group = group.sort_values("timestamp")
        if len(group) < 2:
            continue

        prev_price  = group.iloc[-2]["close"]
        curr_price  = group.iloc[-1]["close"]
        prev_volume = group.iloc[-2]["volume"]
        curr_volume = group.iloc[-1]["volume"]

        price_delta_pct  = (curr_price  - prev_price)  / prev_price  * 100
        volume_delta_pct = max(0, (curr_volume - prev_volume) / prev_volume * 100)

        changes.append(PriceVolume(
            symbol=symbol,
            price_delta_pct=round(price_delta_pct, 2),
            volume_delta_pct=round(volume_delta_pct, 0),
        ))

    return changes