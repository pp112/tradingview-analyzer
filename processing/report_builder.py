from typing import Literal
from models.timeframe import Timeframe


class ReportBuilder:
    """
    формирует финальный текстовый отчёт по торговым сигналам.
    
    Задачи:
    - фильтрация сигналов по корреляции
    - сортировка по приоритету и "силе" сигнала
    - извлечение значений индикаторов
    - форматирование строк для отчёта
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
        signals: list[dict[str, str]],
        indicators: dict[str, dict],
        timeframe: Timeframe,
        correlations: dict[str, float],
        corr_sort_order: Literal["asc", "desc"] = "desc",
        corr_threshold: float = 1
    ) -> list[str]:
        """
        Собирает финальный отчёт.

        Пайплайн:
        1. Фильтрация сигналов по корреляции
        2. Сортировка по приоритету и силе сигнала
        3. Формирование строк отчёта
        """
        reports = []
        
        filtered_sorted_signals = self._prepare_signals(
            signals, indicators, correlations, corr_sort_order, corr_threshold
        )

        for s in filtered_sorted_signals:
            indicator, direction = self.MAPPING.get(s["signal"])
            symbol = str(s["symbol"])
            corr_value = correlations.get(symbol)
            vol_ratio = indicators[symbol]["volume"]["ratio"]

            reports.append(
                self._format(
                    symbol,
                    indicator,
                    direction,
                    timeframe,
                    corr_value,
                    indicators.get(symbol, {}),
                    vol_ratio
                )
            )

        return reports

    @staticmethod
    def _prepare_signals(
        signals: list[dict[str, str]],
        indicators: dict[str, dict],
        correlations: dict[str, float],
        corr_sort_order: Literal["asc", "desc"],
        corr_threshold: float | None
    ) -> list[dict[str, str]]:
        """
        Фильтрует и сортирует сигналы.
        - удаляет сигналы без корреляции
        - применяет порог корреляции
        - сортирует по приоритету и силе
        """

        filtered = [
            s for s in signals
            if correlations.get(str(s["symbol"])) is not None
        ]

        filtered = [
            s for s in filtered
            if correlations[str(s["symbol"])] <= corr_threshold
        ]

        return sorted(
            filtered,
            key=lambda s: ReportBuilder._sort_key(s, indicators, correlations, corr_sort_order),
        )

    @staticmethod
    def _sort_key(
        signal: dict[str, str],
        indicators: dict[str, dict],
        correlations: dict[str, float],
        corr_sort_order: Literal["asc", "desc"],
    ) -> tuple[int, float, float]:
        """
        Возвращает кортеж для сортировки для сигнала.

        Приоритеты:
        1. Тип индикатора (RSI -> MACD -> EMA/SMA)
        2. Сила сигнала (чем больше, тем выше)
        3. Корреляция (tie-breaker)
        """
        signal_name = str(signal.get("signal", ""))
        indicator_order = {
            "RSI_OVERBOUGHT": 0,
            "RSI_OVERSOLD": 0,
            "MACD_BULLISH": 1,
            "MACD_BEARISH": 1,
            "EMA_SMA_BULLISH": 2,
            "EMA_SMA_BEARISH": 2,
        }.get(signal_name, 99)

        symbol = str(signal.get("symbol", ""))
        indicator_values = indicators.get(symbol, {})
        strength = ReportBuilder._get_strength(signal_name, indicator_values)

        volume_ratio = indicator_values["volume"]["ratio"]

        corr_value = correlations.get(symbol, 0.0)
        corr_score = corr_value if corr_sort_order == "asc" else -corr_value

        return (indicator_order, -strength, -volume_ratio, corr_score)

    @staticmethod
    def _get_strength(signal_name: str, values: dict) -> float:
        """
        Возвращает "силу" сигнала.

        Логика:
        - RSI: расстояние до границ (0 или 100)
        - MACD: расстояние между MACD и signal
        - EMA/SMA: расстояние между линиями
        """
        if signal_name in {"RSI_OVERBOUGHT", "RSI_OVERSOLD"}:
            rsi_val = values.get("rsi")
            if rsi_val is None:
                return 0.0
            rsi_val = float(rsi_val)
            return rsi_val if signal_name == "RSI_OVERBOUGHT" else 100 - rsi_val

        if signal_name in {"MACD_BULLISH", "MACD_BEARISH"}:
            macd_block = values.get("macd")
            if not macd_block:
                return 0.0
            curr = macd_block.get("curr")
            if not curr:
                return 0.0
            macd_val = float(curr.get("MACD", 0.0))
            macd_signal = float(curr.get("MACD_signal", 0.0))
            return abs(macd_val - macd_signal)

        if signal_name in {"EMA_SMA_BULLISH", "EMA_SMA_BEARISH"}:
            ema = values.get("ema")
            sma = values.get("sma")
            if not ema or not sma:
                return 0.0
            return abs(float(ema[1]) - float(sma[1]))

        return 0.0
    
    def _format_indicator_value(indicator: str, values: dict) -> str:
        if indicator == "RSI":
            rsi_val = values.get("rsi")
            if rsi_val is None:
                return "-"
            return f"RSI={rsi_val:.2f}"

        if indicator == "MACD":
            macd_block = values.get("macd")
            if not macd_block:
                return "-"
            curr = macd_block.get("curr")
            if not curr:
                return "-"
            macd_val = float(curr.get("MACD", 0.0))
            macd_signal = float(curr.get("MACD_signal", 0.0))
            spread = abs(macd_val - macd_signal)
            return f"diff={spread:.6f}"

        if indicator == "EMA_SMA":
            ema = values.get("ema")
            sma = values.get("sma")
            if not ema or not sma:
                return "-"
            ema_val = float(ema[1])
            sma_val = float(sma[1])
            spread = abs(ema_val - sma_val)
            return f"diff={spread:.6f}"

        return "-"

    @staticmethod
    def _format(
        symbol: str,
        indicator: str,
        direction: str,
        timeframe: Timeframe,
        corr_value: float,
        indicator_values: dict,
        vol_ratio: float
    ) -> str:
        """
        Формирует одну строку отчёта вида:

        | SYMBOL | DIR | INDICATOR | TF | val: ... | vol_rat=... | corr: ...
        """
        indicator_value = ReportBuilder._format_indicator_value(indicator, indicator_values)

        return (
            f"| {symbol:<17} | {direction:<5} | {indicator} | {indicator_value:<9} | "
            f"vol_rat={vol_ratio:.2f} | corr: {corr_value:<5.2f} | {timeframe.label}"
        )