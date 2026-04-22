"""
AI/ML Features for Trading
Trend detection, entry zone detection, signal confidence scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from enum import Enum


class TrendDirection(Enum):
    """Trend directions"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"


class SignalQuality(Enum):
    """Signal quality levels"""
    STRONG = "strong"
    NORMAL = "normal"
    WEAK = "weak"


class AIAnalyzer:
    """
    AI/ML features for advanced trading analysis
    Includes: Trend detection, entry zone detection, signal quality
    """

    @staticmethod
    def detect_trend(
        df: pd.DataFrame,
        short_ema: int = 20,
        long_ema: int = 50,
        ultra_long_ema: int = 200
    ) -> Dict:
        """
        Detect trend using multiple EMAs
        
        Args:
            df: OHLC DataFrame
            short_ema: Short EMA period
            long_ema: Long EMA period
            ultra_long_ema: Long EMA period for trend
        
        Returns:
            Dictionary with trend information
        """
        if len(df) < ultra_long_ema:
            return {
                'trend': 'UNKNOWN',
                'strength': 0,
                'confidence': 0
            }

        # Calculate EMAs
        ema_short = df['close'].ewm(span=short_ema, adjust=False).mean()
        ema_long = df['close'].ewm(span=long_ema, adjust=False).mean()
        ema_ultra = df['close'].ewm(span=ultra_long_ema, adjust=False).mean()

        current_price = df['close'].iloc[-1]
        current_short = ema_short.iloc[-1]
        current_long = ema_long.iloc[-1]
        current_ultra = ema_ultra.iloc[-1]

        # Determine trend
        if current_price > current_short > current_long > current_ultra:
            trend = TrendDirection.BULLISH
            strength = 100
        elif current_price > current_long > current_ultra:
            trend = TrendDirection.BULLISH
            strength = 75
        elif current_price > current_ultra:
            trend = TrendDirection.BULLISH
            strength = 50
        elif current_price < current_short < current_long < current_ultra:
            trend = TrendDirection.BEARISH
            strength = 100
        elif current_price < current_long < current_ultra:
            trend = TrendDirection.BEARISH
            strength = 75
        elif current_price < current_ultra:
            trend = TrendDirection.BEARISH
            strength = 50
        else:
            trend = TrendDirection.SIDEWAYS
            strength = 0

        # Calculate confidence
        price_range = df['high'].iloc[-20:].max() - df['low'].iloc[-20:].min()
        atr = price_range / 20
        confidence = min(100, (abs(current_price - current_ultra) / atr) * 10) if atr > 0 else 0

        return {
            'trend': trend.value,
            'strength': strength,
            'confidence': confidence,
            'current_price': current_price,
            'ema_short': current_short,
            'ema_long': current_long,
            'ema_ultra': current_ultra,
        }

    @staticmethod
    def detect_entry_zones(df: pd.DataFrame) -> List[Dict]:
        """
        Detect best entry zones using support/resistance and price patterns
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            List of entry zones
        """
        zones = []

        if len(df) < 20:
            return zones

        recent = df.tail(20)

        # Find support levels (local lows)
        for i in range(1, len(recent) - 1):
            if (recent['low'].iloc[i] < recent['low'].iloc[i-1] and
                recent['low'].iloc[i] < recent['low'].iloc[i+1]):
                zones.append({
                    'type': 'SUPPORT',
                    'price': recent['low'].iloc[i],
                    'strength': 50,
                })

        # Find resistance levels (local highs)
        for i in range(1, len(recent) - 1):
            if (recent['high'].iloc[i] > recent['high'].iloc[i-1] and
                recent['high'].iloc[i] > recent['high'].iloc[i+1]):
                zones.append({
                    'type': 'RESISTANCE',
                    'price': recent['high'].iloc[i],
                    'strength': 50,
                })

        # Find strongest zones
        zones.sort(key=lambda x: x['strength'], reverse=True)
        return zones[:5]  # Return top 5 zones

    @staticmethod
    def detect_fake_breakout(
        df: pd.DataFrame,
        lookback: int = 5
    ) -> bool:
        """
        Detect potential fake breakout signals
        Returns True if breakout is likely fake
        
        Args:
            df: OHLC DataFrame
            lookback: Number of candles to analyze
        
        Returns:
            True if potential fake breakout detected
        """
        if len(df) < lookback + 5:
            return False

        recent = df.tail(lookback + 5)
        latest = recent.tail(lookback)

        # Check if breakout has low volume
        avg_volume = recent['volume'].mean()
        breakout_volume = latest['volume'].mean()

        if breakout_volume < avg_volume * 0.8:
            return True

        # Check if price immediately reverses
        if latest['close'].iloc[-1] < latest['close'].iloc[0]:
            return True

        # Check for rejection from resistance
        if latest['close'].iloc[-1] < latest['high'].mean() * 0.95:
            return True

        return False

    @staticmethod
    def calculate_signal_quality(
        df: pd.DataFrame,
        signal_type: str,  # 'BUY' or 'SELL'
        rsi_value: float,
        volume_confirm: bool,
        trend: str
    ) -> Tuple[SignalQuality, float]:
        """
        Calculate signal quality and confidence score
        
        Args:
            df: OHLC DataFrame
            signal_type: BUY or SELL
            rsi_value: Current RSI value
            volume_confirm: Whether volume confirms signal
            trend: Current trend direction
        
        Returns:
            Tuple of (signal_quality, confidence_score)
        """
        confidence = 0

        # Trend alignment (40% weight)
        if signal_type == 'BUY' and trend == 'bullish':
            confidence += 40
        elif signal_type == 'SELL' and trend == 'bearish':
            confidence += 40
        elif trend == 'sideways':
            confidence += 20

        # RSI alignment (30% weight)
        if signal_type == 'BUY':
            if rsi_value < 50:
                confidence += 30
            elif rsi_value < 70:
                confidence += 15
        else:  # SELL
            if rsi_value > 50:
                confidence += 30
            elif rsi_value > 30:
                confidence += 15

        # Volume confirmation (30% weight)
        if volume_confirm:
            confidence += 30

        # Determine quality
        if confidence >= 80:
            quality = SignalQuality.STRONG
        elif confidence >= 50:
            quality = SignalQuality.NORMAL
        else:
            quality = SignalQuality.WEAK

        return quality, confidence

    @staticmethod
    def calculate_risk_score(
        df: pd.DataFrame,
        current_price: float,
        entry_price: float,
        stop_loss: float
    ) -> Dict:
        """
        Calculate risk metrics for a potential trade
        
        Args:
            df: OHLC DataFrame
            current_price: Current market price
            entry_price: Entry price
            stop_loss: Stop loss price
        
        Returns:
            Dictionary with risk metrics
        """
        # Calculate volatility
        returns = df['close'].pct_change()
        volatility = returns.std() * 100

        # Calculate risk/reward
        if entry_price < current_price:  # BUY
            risk = entry_price - stop_loss
            potential_loss_pct = (risk / entry_price) * 100
        else:  # SELL
            risk = stop_loss - entry_price
            potential_loss_pct = (risk / entry_price) * 100

        # Risk score (0-100, lower is better)
        risk_score = min(100, potential_loss_pct * 2)

        return {
            'volatility': volatility,
            'potential_loss_pct': potential_loss_pct,
            'risk_score': risk_score,
            'safe_to_trade': risk_score < 5,  # Less than 5% risk is safe
        }


if __name__ == "__main__":
    print("AI Analyzer initialized successfully")
