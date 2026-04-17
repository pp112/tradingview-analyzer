from typing import Literal


class ReportBuilder:
    """
    Формирует человекочитаемые отчёты сигналов.    
    """
    MAPPING = {
        "RSI_OVERBOUGHT": ("RSI", "ВНИЗ"),
        "RSI_OVERSOLD": ("RSI", "ВВЕРХ"),
        "MACD_BULLISH": ("MACD", "ВВЕРХ"),
        "MACD_BEARISH": ("MACD", "ВНИЗ"),
        "EMA_SMA_BULLISH": ("EMA_SMA", "ВВЕРХ"),
        "EMA_SMA_BEARISH": ("EMA_SMA", "ВНИЗ"),
    }

    def build(
        self,
        signals: list[dict],
        timeframe,
        correlations: dict[str, float] | None = None,
        sort_order: Literal["asc", "desc"] = "desc",
        corr_threshold: float | None = None
    ) -> list[str]:
        reports = []
        
        processed = self._prepare_signals(
            signals, correlations, sort_order, corr_threshold
        )

        for s in processed:
            indicator, direction = self.MAPPING.get(s["signal"])
            corr_value = correlations.get(s["symbol"])

            reports.append(
                self._format(s["symbol"], indicator, direction, timeframe, corr_value)
            )

        return reports

    @staticmethod
    def _prepare_signals(
        signals: list[dict],
        correlations: dict[str, float] | None,
        sort_order: Literal["asc", "desc"],
        corr_threshold: float | None
    ) -> list[dict]:

        if not correlations:
            return signals

        # фильтр
        filtered = [
            s for s in signals
            if correlations.get(s["symbol"]) is not None
        ]

        # threshold
        if corr_threshold is not None:
            filtered = [
                s for s in filtered
                if correlations[s["symbol"]] <= corr_threshold
            ]

        # сортировка
        return sorted(
            filtered,
            key=lambda s: correlations[s["symbol"]],
            reverse=(sort_order == "desc")
        )

    @staticmethod
    def _format(symbol, indicator, direction, timeframe, corr_value):
        return (
            f"| {symbol:<17} | {direction:<5} | {indicator:<9} | "
            f"{timeframe.label:<3} | corr: {corr_value}"
        )