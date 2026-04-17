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

    def build(self, signals, timeframe):
        reports = []

        for s in signals:
            indicator, direction = self.MAPPING.get(s["signal"])

            reports.append(
                self._format(s["symbol"], indicator, direction, timeframe)
            )

        return reports

    @staticmethod
    def _format(symbol, indicator, direction, timeframe):
        return f"| {symbol:<14} | {direction:<5} | {indicator:<9} | {timeframe.label:<3}\n"