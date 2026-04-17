import pandas as pd

from processing import IndicatorCalculator, SignalGenerator, ReportBuilder
from processing.indicators import correlation
from models.timeframe import Timeframe
from utils import sort_correlations, filter_low_correlations


class IndicatorEngine:
    """
    Оркестратор аналитического пайплайна.

    Отвечает за координацию процессов:
    1. Расчёт индикаторов (IndicatorCalculator)
    2. Генерация торговых сигналов (SignalGenerator)
    3. Расчёт корреляций между активами
    """
    def __init__(
        self, 
        upper_rsi = 70,
        lower_rsi = 30,
        corr_threshold = 0.5
    ):
        self.indicator_calculator = IndicatorCalculator()
        self.signal_generator = SignalGenerator(upper_rsi, lower_rsi)
        self.report_builder = ReportBuilder()
        self.corr_threshold = corr_threshold

    def process(
        self, 
        df: pd.DataFrame, 
        timeframe: Timeframe
    ) -> tuple[
        dict[str, dict], 
        list[dict], 
        list[str]
    ]:
        indicators = self.indicator_calculator.calculate(df, timeframe)
        signals = self.signal_generator.generate(indicators, timeframe)
        reports = self.report_builder.build(signals, timeframe)

        return indicators, signals, reports

    def calculate_correlations(self, df: pd.DataFrame) -> dict[str, float]:
        """
        Рассчитывает корреляции всех символов относительно BTC.
        """
        ticker_corrs = {}

        symbols = df['symbol'].unique()

        for symbol in symbols:
            ticker_corrs[symbol] = correlation(df, symbol)
        
        ticker_corrs = filter_low_correlations(ticker_corrs, self.corr_threshold)
        ticker_corrs = sort_correlations(ticker_corrs, "desc")

        return ticker_corrs