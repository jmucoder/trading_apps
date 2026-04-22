"""
Backtesting Engine
Test strategies on historical data
Shows win rate, profit, loss, and equity curve
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BacktestResult:
    """Store backtest results"""
    
    def __init__(self):
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []
        self.daily_returns: List[float] = []
        self.timestamps: List[datetime] = []

    def add_trade(self, trade: Dict):
        """Add trade result"""
        self.trades.append(trade)

    def calculate_metrics(self, initial_capital: float) -> Dict:
        """Calculate backtest metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'total_pnl': 0,
                'roi': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'consecutive_wins': 0,
                'consecutive_losses': 0,
            }

        # Extract P&L values
        pnls = [trade.get('pnl', 0) for trade in self.trades]
        winning_trades = [p for p in pnls if p > 0]
        losing_trades = [p for p in pnls if p < 0]

        # Calculate metrics
        total_trades = len(self.trades)
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        win_rate = (winning_count / total_trades * 100) if total_trades > 0 else 0

        gross_profit = sum(winning_trades) if winning_trades else 0
        gross_loss = abs(sum(losing_trades)) if losing_trades else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        total_pnl = sum(pnls)
        roi = (total_pnl / initial_capital * 100) if initial_capital > 0 else 0

        avg_win = (gross_profit / len(winning_trades)) if winning_trades else 0
        avg_loss = (gross_loss / len(losing_trades)) if losing_trades else 0

        # Calculate max drawdown
        equity = initial_capital
        peak = initial_capital
        max_dd = 0
        for pnl in pnls:
            equity += pnl
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)

        max_drawdown = max_dd * 100

        # Calculate consecutive wins/losses
        consecutive_wins = 0
        consecutive_losses = 0
        for pnl in pnls:
            if pnl > 0:
                consecutive_wins += 1
                consecutive_losses = 0
            else:
                consecutive_losses += 1
                consecutive_wins = 0

        # Sharpe ratio (simplified)
        if len(pnls) > 1:
            returns = np.array(pnls)
            sharpe = (np.mean(returns) / (np.std(returns) + 1e-8)) * np.sqrt(252)
        else:
            sharpe = 0

        return {
            'total_trades': total_trades,
            'winning_trades': winning_count,
            'losing_trades': losing_count,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_pnl': total_pnl,
            'roi': roi,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'consecutive_wins': consecutive_wins,
            'consecutive_losses': consecutive_losses,
        }


class Backtester:
    """
    Backtest trading strategies on historical data
    """

    def __init__(self, initial_capital: float = 10000):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital
        """
        self.initial_capital = initial_capital

    def run_strategy(
        self,
        df: pd.DataFrame,
        strategy_func,
        commission: float = 0.001  # 0.1% commission
    ) -> BacktestResult:
        """
        Run backtest with custom strategy function
        
        Args:
            df: OHLC DataFrame with indicators
            strategy_func: Function that generates signals
            commission: Trading commission as decimal
        
        Returns:
            BacktestResult object
        """
        result = BacktestResult()
        balance = self.initial_capital
        position = None

        for i in range(len(df)):
            row = df.iloc[i]
            signal = strategy_func(df.iloc[:i+1])

            if position is None and signal in ['BUY', 'SELL']:
                # Open position
                position = {
                    'entry_idx': i,
                    'entry_price': row['close'],
                    'entry_time': row['timestamp'] if 'timestamp' in row else i,
                    'signal': signal,
                    'quantity': balance / (row['close'] * (1 + commission)),
                }

            elif position is not None:
                # Check exit conditions
                exit_signal = False
                exit_price = row['close']

                if position['signal'] == 'BUY':
                    if signal == 'SELL':
                        exit_signal = True
                elif position['signal'] == 'SELL':
                    if signal == 'BUY':
                        exit_signal = True

                if exit_signal:
                    # Close position
                    if position['signal'] == 'BUY':
                        pnl = (exit_price - position['entry_price']) * position['quantity']
                    else:
                        pnl = (position['entry_price'] - exit_price) * position['quantity']

                    # Apply commission
                    pnl -= pnl * commission

                    balance += pnl

                    trade = {
                        'entry_idx': position['entry_idx'],
                        'exit_idx': i,
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'signal': position['signal'],
                        'quantity': position['quantity'],
                        'pnl': pnl,
                        'pnl_pct': (pnl / (position['entry_price'] * position['quantity'])) * 100,
                        'duration': i - position['entry_idx'],
                    }

                    result.add_trade(trade)
                    position = None
                    result.equity_curve.append(balance)
                    result.timestamps.append(row['timestamp'] if 'timestamp' in row else i)

        # Close remaining position
        if position is not None:
            last_row = df.iloc[-1]
            if position['signal'] == 'BUY':
                pnl = (last_row['close'] - position['entry_price']) * position['quantity']
            else:
                pnl = (position['entry_price'] - last_row['close']) * position['quantity']

            pnl -= pnl * commission
            balance += pnl

            trade = {
                'entry_idx': position['entry_idx'],
                'exit_idx': len(df) - 1,
                'entry_price': position['entry_price'],
                'exit_price': last_row['close'],
                'signal': position['signal'],
                'quantity': position['quantity'],
                'pnl': pnl,
                'pnl_pct': (pnl / (position['entry_price'] * position['quantity'])) * 100,
                'duration': len(df) - 1 - position['entry_idx'],
            }

            result.add_trade(trade)
            result.equity_curve.append(balance)
            result.timestamps.append(last_row['timestamp'] if 'timestamp' in row else len(df) - 1)

        return result

    def run_ema_crossover_backtest(
        self,
        df: pd.DataFrame,
        fast_period: int = 9,
        slow_period: int = 26,
        commission: float = 0.001
    ) -> BacktestResult:
        """
        Backtest EMA crossover strategy
        
        Args:
            df: OHLC DataFrame
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            commission: Trading commission
        
        Returns:
            BacktestResult object
        """
        from src.data.indicators import TechnicalIndicators, SignalGenerator

        def strategy(data):
            return SignalGenerator.ema_crossover_signal(data, fast_period, slow_period)

        return self.run_strategy(df, strategy, commission)

    def run_rsi_backtest(
        self,
        df: pd.DataFrame,
        period: int = 14,
        commission: float = 0.001
    ) -> BacktestResult:
        """
        Backtest RSI strategy
        
        Args:
            df: OHLC DataFrame
            period: RSI period
            commission: Trading commission
        
        Returns:
            BacktestResult object
        """
        from src.data.indicators import TechnicalIndicators

        def strategy(data):
            if len(data) < period:
                return 'HOLD'

            rsi = TechnicalIndicators.calculate_rsi(data['close'], period)
            current_rsi = rsi.iloc[-1]

            if current_rsi < 30:
                return 'BUY'
            elif current_rsi > 70:
                return 'SELL'
            return 'HOLD'

        return self.run_strategy(df, strategy, commission)

    def run_volume_breakout_backtest(
        self,
        df: pd.DataFrame,
        commission: float = 0.001
    ) -> BacktestResult:
        """
        Backtest volume breakout strategy
        
        Args:
            df: OHLC DataFrame
            commission: Trading commission
        
        Returns:
            BacktestResult object
        """
        from src.data.indicators import SignalGenerator

        def strategy(data):
            if len(data) < 20:
                return 'HOLD'

            vol_confirm = SignalGenerator.volume_confirmation(data)
            return 'BUY' if vol_confirm else 'HOLD'

        return self.run_strategy(df, strategy, commission)

    def compare_strategies(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Dict]:
        """
        Compare multiple strategies on same data
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            Dictionary with results for each strategy
        """
        results = {}

        # Test EMA Crossover
        ema_result = self.run_ema_crossover_backtest(df)
        results['EMA Crossover'] = ema_result.calculate_metrics(self.initial_capital)

        # Test RSI
        rsi_result = self.run_rsi_backtest(df)
        results['RSI'] = rsi_result.calculate_metrics(self.initial_capital)

        # Test Volume Breakout
        vol_result = self.run_volume_breakout_backtest(df)
        results['Volume Breakout'] = vol_result.calculate_metrics(self.initial_capital)

        return results

    def print_results(self, result: BacktestResult):
        """Print backtest results"""
        metrics = result.calculate_metrics(self.initial_capital)

        print("\n" + "=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Winning Trades: {metrics['winning_trades']}")
        print(f"Losing Trades: {metrics['losing_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"Total P&L: ${metrics['total_pnl']:.2f}")
        print(f"ROI: {metrics['roi']:.2f}%")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Avg Win: ${metrics['avg_win']:.2f}")
        print(f"Avg Loss: ${metrics['avg_loss']:.2f}")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    print("Backtester initialized successfully")
