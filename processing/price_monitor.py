import pandas as pd

from storage.writer import write_json
from config import get_logger

logger = get_logger(__name__, "[PRICE_VOL]")


class PriceVolumeMonitor:
    """
    Отслеживает изменения цен между запусками и сохраняет результат.
    """

    CHANGES_PATH = "data/values/prices/price_changes.json"
    
    def calculate_and_save(self, df: pd.DataFrame):
        """
        Вычисляет изменения цен и объёмов из последних двух свечей и сохраняет результат.
        """
        logger.info("Расчёт изменений цен и объёмов")
        changes = self._calculate_changes(df)
        write_json(self.CHANGES_PATH, changes)
        logger.info(f"Изменения цен и объемов сохранены")
        
    @staticmethod
    def _calculate_changes(df: pd.DataFrame) -> dict:
        """
        Вычисляет процентное изменение цены и объёма для каждого символа.
        """
        changes = {}

        for symbol, group in df.groupby("symbol"):
            group = group.sort_values("timestamp")

            if len(group) < 2:
                continue

            prev_price  = group.iloc[-2]["close"]
            curr_price  = group.iloc[-1]["close"]
            prev_volume = group.iloc[-2]["volume"]
            curr_volume = group.iloc[-1]["volume"]

            price_delta_pct  = (curr_price  - prev_price)  / prev_price  * 100
            volume_delta_pct = (curr_volume - prev_volume) / prev_volume * 100

            changes[symbol] = {
                "price_delta_pct":  round(price_delta_pct,  2),
                "volume_delta_pct": round(volume_delta_pct, 2),
            }

        return changes