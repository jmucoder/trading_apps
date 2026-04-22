"""
Technical Indicators Module
Calculates various technical indicators for trading analysis
Includes: EMA, RSI, MACD, Volume, Support/Resistance
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Calculate technical indicators for market analysis
    """

    @staticmethod
    def calculate_ema(data: pd.Series, period: int = 9) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            data: Price series
            period: EMA period
        
        Returns:
            EMA series
        """
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index
        
        Args:
            data: Price series
            period: RSI period (default 14)
        
        Returns:
            RSI series (0-100)
        """
        # Calculate price changes
        delta = data.diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    @staticmethod
    def calculate_macd(
        data: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data: Price series
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
        
        Returns:
            Tuple of (MACD, Signal, Histogram)
        """
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_histogram = macd - macd_signal
        
        return macd, macd_signal, macd_histogram

    @staticmethod
    def calculate_bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            data: Price series
            period: SMA period
            std_dev: Standard deviation multiplier
        
        Returns:
            Tuple of (Upper Band, Middle Band, Lower Band)
        """
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band

    @staticmethod
    def calculate_atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate Average True Range (for volatility)
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period
        
        Returns:
            ATR series
        """
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr

    @staticmethod
    def calculate_stochastic(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14,
        smooth_k: int = 3,
        smooth_d: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Period
            smooth_k: K smoothing
            smooth_d: D smoothing
        
        Returns:
            Tuple of (%K, %D)
        """
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)
        k_percent = k_percent.rolling(window=smooth_k).mean()
        d_percent = k_percent.rolling(window=smooth_d).mean()
        
        return k_percent, d_percent

    @staticmethod
    def calculate_support_resistance(
        df: pd.DataFrame,
        lookback: int = 20
    ) -> Tuple[float, float]:
        """
        Calculate support and resistance levels
        
        Args:
            df: OHLC DataFrame
            lookback: Number of periods to look back
        
        Returns:
            Tuple of (Support, Resistance)
        """
        recent_data = df.tail(lookback)
        
        support = recent_data['low'].min()
        resistance = recent_data['high'].max()
        
        return support, resistance

    @staticmethod
    def calculate_pivot_points(
        high: float,
        low: float,
        close: float
    ) -> Dict[str, float]:
        """
        Calculate pivot points (support/resistance)
        
        Args:
            high: Previous day high
            low: Previous day low
            close: Previous day close
        
        Returns:
            Dictionary with pivot levels
        """
        pivot = (high + low + close) / 3
        r1 = (2 * pivot) - low
        s1 = (2 * pivot) - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        
        return {
            'pivot': pivot,
            'r1': r1,
            's1': s1,
            'r2': r2,
            's2': s2
        }


class SignalGenerator:
    """
    Generate trading signals based on technical indicators
    """

    @staticmethod
    def ema_crossover_signal(
        df: pd.DataFrame,
        fast_period: int = 9,
        slow_period: int = 26
    ) -> str:
        """
        Generate signal based on EMA crossover
        
        Args:
            df: OHLC DataFrame
            fast_period: Fast EMA period
            slow_period: Slow EMA period
        
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        if len(df) < slow_period:
            return 'HOLD'

        ema_fast = TechnicalIndicators.calculate_ema(df['close'], fast_period)
        ema_slow = TechnicalIndicators.calculate_ema(df['close'], slow_period)
        
        current_fast = ema_fast.iloc[-1]
        current_slow = ema_slow.iloc[-1]
        prev_fast = ema_fast.iloc[-2]
        prev_slow = ema_slow.iloc[-2]
        
        # Bullish crossover: fast crosses above slow
        if prev_fast <= prev_slow and current_fast > current_slow:
            return 'BUY'
        
        # Bearish crossover: fast crosses below slow
        elif prev_fast >= prev_slow and current_fast < current_slow:
            return 'SELL'
        
        return 'HOLD'

    @staticmethod
    def rsi_signal(df: pd.DataFrame, period: int = 14) -> str:
        """
        Generate signal based on RSI
        
        Args:
            df: OHLC DataFrame
            period: RSI period
        
        Returns:
            'STRONG_BUY', 'BUY', 'SELL', 'STRONG_SELL', or 'HOLD'
        """
        if len(df) < period:
            return 'HOLD'

        rsi = TechnicalIndicators.calculate_rsi(df['close'], period)
        current_rsi = rsi.iloc[-1]
        
        if current_rsi < 30:
            return 'STRONG_BUY'
        elif current_rsi < 40:
            return 'BUY'
        elif current_rsi > 70:
            return 'STRONG_SELL'
        elif current_rsi > 60:
            return 'SELL'
        
        return 'HOLD'

    @staticmethod
    def macd_signal(df: pd.DataFrame) -> str:
        """
        Generate signal based on MACD
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            'BUY', 'SELL', or 'HOLD'
        """
        if len(df) < 26:
            return 'HOLD'

        macd, signal, histogram = TechnicalIndicators.calculate_macd(df['close'])
        
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        prev_histogram = histogram.iloc[-2]
        current_histogram = histogram.iloc[-1]
        
        # Bullish crossover
        if prev_histogram < 0 and current_histogram > 0:
            return 'BUY'
        
        # Bearish crossover
        elif prev_histogram > 0 and current_histogram < 0:
            return 'SELL'
        
        return 'HOLD'

    @staticmethod
    def volume_confirmation(df: pd.DataFrame, period: int = 20) -> bool:
        """
        Check if current volume confirms the trend
        
        Args:
            df: OHLC DataFrame
            period: Average volume period
        
        Returns:
            True if volume is above average, False otherwise
        """
        if len(df) < period:
            return False

        avg_volume = df['volume'].rolling(window=period).mean().iloc[-1]
        current_volume = df['volume'].iloc[-1]
        
        return current_volume > avg_volume * 1.1  # 10% above average

    @staticmethod
    def calculate_confidence_score(
        df: pd.DataFrame,
        show_breakdown: bool = False
    ) -> Tuple[float, Dict]:
        """
        Calculate overall confidence score (0-100)
        Combines multiple signals
        
        Args:
            df: OHLC DataFrame
            show_breakdown: If True, returns signal breakdown
        
        Returns:
            Tuple of (confidence_score, signal_breakdown)
        """
        scores = {}
        
        # EMA Crossover signal (weight: 30%)
        ema_sig = SignalGenerator.ema_crossover_signal(df)
        scores['ema'] = {'signal': ema_sig, 'weight': 0.3}
        
        if ema_sig == 'BUY':
            scores['ema']['score'] = 100
        elif ema_sig == 'SELL':
            scores['ema']['score'] = 0
        else:
            scores['ema']['score'] = 50
        
        # RSI signal (weight: 25%)
        rsi_sig = SignalGenerator.rsi_signal(df)
        scores['rsi'] = {'signal': rsi_sig, 'weight': 0.25}
        
        rsi_map = {
            'STRONG_BUY': 100, 'BUY': 75,
            'HOLD': 50,
            'SELL': 25, 'STRONG_SELL': 0
        }
        scores['rsi']['score'] = rsi_map.get(rsi_sig, 50)
        
        # MACD signal (weight: 25%)
        macd_sig = SignalGenerator.macd_signal(df)
        scores['macd'] = {'signal': macd_sig, 'weight': 0.25}
        
        if macd_sig == 'BUY':
            scores['macd']['score'] = 100
        elif macd_sig == 'SELL':
            scores['macd']['score'] = 0
        else:
            scores['macd']['score'] = 50
        
        # Volume confirmation (weight: 20%)
        vol_confirm = SignalGenerator.volume_confirmation(df)
        scores['volume'] = {'signal': 'STRONG' if vol_confirm else 'WEAK', 'weight': 0.2}
        scores['volume']['score'] = 100 if vol_confirm else 0
        
        # Calculate weighted score
        total_score = sum(
            scores[key]['score'] * scores[key]['weight']
            for key in scores
        )
        
        breakdown = {key: scores[key]['signal'] for key in scores}
        
        if show_breakdown:
            return total_score, breakdown, scores
        return total_score, breakdown


if __name__ == "__main__":
    # Example usage
    import sys
    sys.path.append('/src/data')
    from market_data import MarketDataFetcher
    
    fetcher = MarketDataFetcher()
    df = fetcher.fetch_crypto_ohlc('BTC/USDT', '1h', 100)
    
    if not df.empty:
        # Calculate indicators
        rsi = TechnicalIndicators.calculate_rsi(df['close'])
        macd, signal, hist = TechnicalIndicators.calculate_macd(df['close'])
        
        print("RSI:", rsi.iloc[-1])
        print("MACD:", macd.iloc[-1])
        print("Signal:", signal.iloc[-1])
        
        # Generate signals
        print("EMA Signal:", SignalGenerator.ema_crossover_signal(df))
        print("RSI Signal:", SignalGenerator.rsi_signal(df))
        print("MACD Signal:", SignalGenerator.macd_signal(df))
