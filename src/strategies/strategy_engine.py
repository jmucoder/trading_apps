"""
Trading Strategy Engine
Implements multiple trading strategies: EMA Crossover, RSI Filter, Volume Confirmation
Supports Scalping Mode, Trend-Following Mode, and Safe Mode
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TradingMode(Enum):
    """Enumeration of trading modes"""
    NORMAL = "normal"
    SCALPING = "scalping"
    TREND_FOLLOWING = "trend_following"
    SAFE = "safe"


class StrategyType(Enum):
    """Enumeration of strategy types"""
    EMA_CROSSOVER = "ema_crossover"
    RSI_FILTER = "rsi_filter"
    VOLUME_CONFIRMATION = "volume_confirmation"
    COMBINED = "combined"


@dataclass
class TradeSignal:
    """Data class for trade signals"""
    timestamp: datetime
    symbol: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float  # 0-100
    strategy: StrategyType
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward_ratio: Optional[float] = None
    mode: TradingMode = TradingMode.NORMAL


@dataclass
class Position:
    """Data class for trading position"""
    symbol: str
    entry_price: float
    quantity: float
    entry_time: datetime
    stop_loss: float
    take_profit: float
    entry_signal: TradeSignal
    trailing_stop: Optional[float] = None
    is_open: bool = True
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = None
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None


class StrategyEngine:
    """
    Main strategy execution engine
    Combines multiple indicators for robust trading signals
    """

    def __init__(self, mode: TradingMode = TradingMode.NORMAL):
        """
        Initialize strategy engine
        
        Args:
            mode: Trading mode (normal, scalping, trend_following, safe)
        """
        self.mode = mode
        self.parameters = self._get_mode_parameters(mode)
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Position] = []

    def _get_mode_parameters(self, mode: TradingMode) -> Dict:
        """
        Get strategy parameters based on mode
        
        Args:
            mode: Trading mode
        
        Returns:
            Dictionary of parameters
        """
        parameters = {
            TradingMode.NORMAL: {
                'ema_fast': 9,
                'ema_slow': 26,
                'rsi_period': 14,
                'min_confidence': 60,
                'risk_reward_ratio': 2.0,
                'position_size_pct': 2.0,
            },
            TradingMode.SCALPING: {
                'ema_fast': 5,
                'ema_slow': 13,
                'rsi_period': 9,
                'min_confidence': 50,
                'risk_reward_ratio': 1.0,
                'position_size_pct': 1.0,
            },
            TradingMode.TREND_FOLLOWING: {
                'ema_fast': 20,
                'ema_slow': 50,
                'rsi_period': 14,
                'min_confidence': 70,
                'risk_reward_ratio': 3.0,
                'position_size_pct': 2.5,
            },
            TradingMode.SAFE: {
                'ema_fast': 9,
                'ema_slow': 26,
                'rsi_period': 14,
                'min_confidence': 75,
                'risk_reward_ratio': 2.5,
                'position_size_pct': 0.5,
            },
        }
        return parameters.get(mode, parameters[TradingMode.NORMAL])

    def analyze_ema_crossover(
        self,
        df: pd.DataFrame
    ) -> TradeSignal:
        """
        Analyze using EMA Crossover strategy
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            TradeSignal object
        """
        from src.data.indicators import TechnicalIndicators, SignalGenerator
        
        if len(df) < self.parameters['ema_slow']:
            return TradeSignal(
                timestamp=datetime.now(),
                symbol=df.get('symbol', 'UNKNOWN').iloc[0] if 'symbol' in df.columns else 'UNKNOWN',
                signal_type='HOLD',
                confidence=0,
                strategy=StrategyType.EMA_CROSSOVER,
                entry_price=df['close'].iloc[-1]
            )

        signal = SignalGenerator.ema_crossover_signal(
            df,
            self.parameters['ema_fast'],
            self.parameters['ema_slow']
        )
        confidence, breakdown = SignalGenerator.calculate_confidence_score(df)

        entry_price = df['close'].iloc[-1]
        atr = TechnicalIndicators.calculate_atr(df['high'], df['low'], df['close'])
        atr_value = atr.iloc[-1] if len(atr) > 0 and pd.notna(atr.iloc[-1]) else entry_price * 0.02

        if signal == 'BUY':
            stop_loss = entry_price - (atr_value * 2)
            take_profit = entry_price + (atr_value * 2 * self.parameters['risk_reward_ratio'])
        elif signal == 'SELL':
            stop_loss = entry_price + (atr_value * 2)
            take_profit = entry_price - (atr_value * 2 * self.parameters['risk_reward_ratio'])
        else:
            stop_loss = entry_price - (atr_value * 2)
            take_profit = entry_price + (atr_value * 2 * self.parameters['risk_reward_ratio'])

        symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'UNKNOWN'

        return TradeSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal,
            confidence=confidence,
            strategy=StrategyType.EMA_CROSSOVER,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=self.parameters['risk_reward_ratio'],
            mode=self.mode
        )

    def analyze_rsi_filter(self, df: pd.DataFrame) -> TradeSignal:
        """
        Analyze using RSI Filter strategy
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            TradeSignal object
        """
        from src.data.indicators import TechnicalIndicators, SignalGenerator
        
        if len(df) < self.parameters['rsi_period']:
            return TradeSignal(
                timestamp=datetime.now(),
                symbol=df['symbol'].iloc[0] if 'symbol' in df.columns else 'UNKNOWN',
                signal_type='HOLD',
                confidence=0,
                strategy=StrategyType.RSI_FILTER,
                entry_price=df['close'].iloc[-1]
            )

        rsi_signal = SignalGenerator.rsi_signal(df, self.parameters['rsi_period'])
        rsi = TechnicalIndicators.calculate_rsi(df['close'], self.parameters['rsi_period'])
        current_rsi = rsi.iloc[-1]

        # RSI: > 50 for buy, < 50 for sell
        if current_rsi > 50:
            signal = 'BUY'
            confidence = min(100, (current_rsi - 50) * 2)
        elif current_rsi < 50:
            signal = 'SELL'
            confidence = min(100, (50 - current_rsi) * 2)
        else:
            signal = 'HOLD'
            confidence = 0

        entry_price = df['close'].iloc[-1]
        
        if signal == 'BUY':
            stop_loss = entry_price * 0.98
            take_profit = entry_price * 1.04
        elif signal == 'SELL':
            stop_loss = entry_price * 1.02
            take_profit = entry_price * 0.96
        else:
            stop_loss = entry_price * 0.98
            take_profit = entry_price * 1.04

        symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'UNKNOWN'

        return TradeSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal,
            confidence=confidence,
            strategy=StrategyType.RSI_FILTER,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            mode=self.mode
        )

    def analyze_volume_confirmation(self, df: pd.DataFrame) -> TradeSignal:
        """
        Analyze using Volume Confirmation strategy
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            TradeSignal object
        """
        from src.data.indicators import SignalGenerator, TechnicalIndicators
        
        if len(df) < 20:
            return TradeSignal(
                timestamp=datetime.now(),
                symbol=df['symbol'].iloc[0] if 'symbol' in df.columns else 'UNKNOWN',
                signal_type='HOLD',
                confidence=0,
                strategy=StrategyType.VOLUME_CONFIRMATION,
                entry_price=df['close'].iloc[-1]
            )

        vol_confirm = SignalGenerator.volume_confirmation(df)
        ema_signal = SignalGenerator.ema_crossover_signal(df)

        if vol_confirm and ema_signal in ['BUY', 'SELL']:
            signal = ema_signal
            confidence = 80.0
        elif ema_signal in ['BUY', 'SELL']:
            signal = ema_signal
            confidence = 50.0
        else:
            signal = 'HOLD'
            confidence = 0

        entry_price = df['close'].iloc[-1]
        atr = TechnicalIndicators.calculate_atr(df['high'], df['low'], df['close'])
        atr_value = atr.iloc[-1] if len(atr) > 0 and pd.notna(atr.iloc[-1]) else entry_price * 0.02

        if signal == 'BUY':
            stop_loss = entry_price - (atr_value * 1.5)
            take_profit = entry_price + (atr_value * 3)
        elif signal == 'SELL':
            stop_loss = entry_price + (atr_value * 1.5)
            take_profit = entry_price - (atr_value * 3)
        else:
            stop_loss = entry_price - (atr_value * 1.5)
            take_profit = entry_price + (atr_value * 3)

        symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'UNKNOWN'

        return TradeSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal,
            confidence=confidence,
            strategy=StrategyType.VOLUME_CONFIRMATION,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            mode=self.mode
        )

    def analyze_combined(self, df: pd.DataFrame) -> TradeSignal:
        """
        Combine multiple signals for robust trading
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            TradeSignal object
        """
        ema_signal = self.analyze_ema_crossover(df)
        rsi_signal = self.analyze_rsi_filter(df)
        vol_signal = self.analyze_volume_confirmation(df)

        # Combine signals
        buy_votes = sum([
            1 for sig in [ema_signal, rsi_signal, vol_signal]
            if sig.signal_type == 'BUY'
        ])
        sell_votes = sum([
            1 for sig in [ema_signal, rsi_signal, vol_signal]
            if sig.signal_type == 'SELL'
        ])

        if buy_votes > sell_votes:
            signal = 'BUY'
            confidence = (ema_signal.confidence + rsi_signal.confidence + vol_signal.confidence) / 3
        elif sell_votes > buy_votes:
            signal = 'SELL'
            confidence = (ema_signal.confidence + rsi_signal.confidence + vol_signal.confidence) / 3
        else:
            signal = 'HOLD'
            confidence = 0

        entry_price = df['close'].iloc[-1]
        stop_loss = min([ema_signal.stop_loss, rsi_signal.stop_loss, vol_signal.stop_loss])
        take_profit = max([ema_signal.take_profit, rsi_signal.take_profit, vol_signal.take_profit])

        symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'UNKNOWN'

        return TradeSignal(
            timestamp=datetime.now(),
            symbol=symbol,
            signal_type=signal,
            confidence=confidence,
            strategy=StrategyType.COMBINED,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward_ratio=self.parameters['risk_reward_ratio'],
            mode=self.mode
        )

    def generate_signal(
        self,
        df: pd.DataFrame,
        strategy: StrategyType = StrategyType.COMBINED
    ) -> TradeSignal:
        """
        Generate trading signal based on selected strategy
        
        Args:
            df: OHLC DataFrame
            strategy: Strategy to use
        
        Returns:
            TradeSignal object
        """
        if strategy == StrategyType.EMA_CROSSOVER:
            return self.analyze_ema_crossover(df)
        elif strategy == StrategyType.RSI_FILTER:
            return self.analyze_rsi_filter(df)
        elif strategy == StrategyType.VOLUME_CONFIRMATION:
            return self.analyze_volume_confirmation(df)
        else:
            return self.analyze_combined(df)

    def create_position(self, signal: TradeSignal, quantity: float) -> Optional[Position]:
        """
        Create a new position from signal
        
        Args:
            signal: TradeSignal object
            quantity: Number of units to trade
        
        Returns:
            Position object or None
        """
        if signal.signal_type == 'HOLD':
            return None

        position = Position(
            symbol=signal.symbol,
            entry_price=signal.entry_price,
            quantity=quantity,
            entry_time=signal.timestamp,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            entry_signal=signal
        )

        self.positions[signal.symbol] = position
        logger.info(f"Position opened: {signal.symbol} @ {signal.entry_price}")
        return position

    def close_position(
        self,
        symbol: str,
        exit_price: float,
        reason: str = 'MANUAL'
    ) -> Optional[Position]:
        """
        Close an open position
        
        Args:
            symbol: Trading symbol
            exit_price: Exit price
            reason: Reason for closing (TP, SL, MANUAL, etc.)
        
        Returns:
            Closed Position object or None
        """
        if symbol not in self.positions:
            return None

        position = self.positions[symbol]
        position.exit_price = exit_price
        position.exit_time = datetime.now()
        position.exit_reason = reason
        position.is_open = False

        # Calculate P&L
        if position.entry_signal.signal_type == 'BUY':
            position.profit_loss = (exit_price - position.entry_price) * position.quantity
            position.profit_loss_pct = ((exit_price / position.entry_price) - 1) * 100
        else:  # SELL
            position.profit_loss = (position.entry_price - exit_price) * position.quantity
            position.profit_loss_pct = ((position.entry_price / exit_price) - 1) * 100

        self.trade_history.append(position)
        del self.positions[symbol]

        logger.info(f"Position closed: {symbol} @ {exit_price}, P&L: {position.profit_loss}")
        return position

    def get_win_rate(self) -> float:
        """Calculate win rate percentage"""
        if not self.trade_history:
            return 0.0

        wins = sum([1 for pos in self.trade_history if (pos.profit_loss or 0) > 0])
        return (wins / len(self.trade_history)) * 100

    def get_total_pnl(self) -> float:
        """Calculate total profit/loss"""
        return sum([pos.profit_loss or 0 for pos in self.trade_history])

    def get_statistics(self) -> Dict:
        """Get trading statistics"""
        return {
            'total_trades': len(self.trade_history),
            'win_rate': self.get_win_rate(),
            'total_pnl': self.get_total_pnl(),
            'open_positions': len(self.positions),
            'mode': self.mode.value,
        }


if __name__ == "__main__":
    print("Strategy Engine initialized successfully")
