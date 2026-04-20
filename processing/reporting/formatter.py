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
        indicator_name: str,
        timeframe: Timeframe,
        corr_value: float,
        indicator_values: dict,
        vol_ratio: float,
        column_order: SortMode,
        index: int
    ) -> str:
        """
        Формирует одну строку отчёта вида:

        | SYMBOL | DIRECTION | INDICATOR | RSI=... | vol_rat=... | corr: ... | TF
        """
        value = ReportFormatter._indicator_value(indicator_name, indicator_values)
        extrs = ReportFormatter._rsi_ext_value(direction, indicator_values)

        base = {
            "index": f"{index:<2}",
            "symbol": f"{symbol:<17}",
            "direction": f"{direction:<5}",
            "indicator_name": indicator_name,
            "value": f"{value:<9}",
            "volume": f"vol_rat={vol_ratio:<5.2f}",
            "rsi_extrs": f"extrs={extrs:<19}",
            "corr": f"corr={corr_value:<5}",
            "tf": timeframe.label
        }

        if column_order == SortMode.CORR_IND_VOL:
            keys = ["index", "symbol", "direction", "indicator_name", "corr", "value", "rsi_extrs", "volume", "tf"]
        elif column_order == SortMode.VOL_IND_CORR:
            keys = ["index", "symbol", "direction", "indicator_name", "volume", "value", "rsi_extrs", "corr", "tf"]
        elif column_order == SortMode.IND_VOL_CORR:
            keys = ["index", "symbol", "direction", "indicator_name", "value", "volume", "rsi_extrs", "corr", "tf"]

        if indicator_name != "RSI":
            keys.remove("rsi_extrs")

        return "| " + " | ".join(base[k] for k in keys) + " |"

    @staticmethod
    def _indicator_value(indicator_name: str, values: dict) -> str:
        if indicator_name == "RSI":
            rsi_val = values.get("rsi")
            if rsi_val is None:
                return "-"
            return f"RSI={rsi_val:.2f}"

        if indicator_name == "MACD":
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

        if indicator_name == "EMA_SMA":
            ema = values.get("ema")
            sma = values.get("sma")
            if not ema or not sma:
                return "-"
            ema_val, sma_val = ema[1], sma[1]
            spread = abs(ema_val - sma_val)
            return f"diff={spread:.6f}"

        return "-"
    
    @staticmethod
    def _rsi_ext_value(direction: str, values: dict) -> str:
        if direction == "ВВЕРХ":
            extremes = values.get("rsi_extremes", {}).get("bottom")
        else:
            extremes = values.get("rsi_extremes", {}).get("top")

        if not extremes:
            return "-"
        
        return ", ".join(map(str, extremes))