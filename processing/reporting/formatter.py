from models.timeframe import Timeframe
from models.sort_mode import SortMode


class ReportFormatter:
    """
    Класс для формирования строки отчета.
    """
    @staticmethod
    def format_line(
        symbol: str,
        direction: str,
        indicator: str,
        timeframe: Timeframe,
        corr_value: float,
        indicator_values: dict,
        vol_ratio: float,
        column_order: SortMode
    ):
        """
        Формирует одну строку отчёта вида:

        | SYMBOL | DIRECTION | INDICATOR | RSI=... | vol_rat=... | corr: ... | TF
        """
        value = ReportFormatter._indicator_value(indicator, indicator_values)

        base = {
            "symbol": f"{symbol:<17}",
            "direction": f"{direction:<5}",
            "indicator": indicator,
            "value": f"{value:<9}",
            "volume": f"vol_rat={vol_ratio:.2f}",
            "corr": f"corr={corr_value:<5.2f}",
            "tf": timeframe.label
        }

        if column_order == SortMode.CORR_IND_VOL:
            keys = ["symbol", "direction", "indicator", "corr", "value", "volume", "tf"]
        elif column_order == SortMode.VOL_IND_CORR:
            keys = ["symbol", "direction", "indicator", "volume", "value", "corr", "tf"]
        elif column_order == SortMode.IND_VOL_CORR:
            keys = ["symbol", "direction", "indicator", "value", "volume", "corr", "tf"]

        return "| " + " | ".join(base[k] for k in keys) + " |"

    @staticmethod
    def _indicator_value(indicator: str, values: dict) -> str:
        if indicator == "RSI":
            rsi_val = values.get("rsi")
            if rsi_val is None:
                return "-"
            return f"RSI={rsi_val:.2f}"

        if indicator == "MACD":
            macd = values.get("macd")
            if not macd:
                return "-"
            curr = macd.get("curr")
            if not curr:
                return "-"
            spread = abs(curr['MACD'] - curr['MACD_signal'])
            base = abs(curr['MACD_signal']) if curr['MACD_signal'] != 0 else 1e-9

            relative = spread / base

            return f"diff={relative:.3f}"

        if indicator == "EMA_SMA":
            ema = values.get("ema")
            sma = values.get("sma")
            if not ema or not sma:
                return "-"
            ema_val, sma_val = ema[1], sma[1]
            spread = abs(ema_val - sma_val)
            return f"diff={spread:.6f}"

        return "-"