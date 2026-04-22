"""
Trading Portfolio and Position Management
Handles position sizing, stop loss, take profit, trailing stops, and risk management
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for trading"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_capital: float
    current_balance: float
    used_margin: float
    free_margin: float
    equity: float
    return_pct: float
    drawdown_pct: float
    win_rate: float
    total_trades: int
    open_positions: int


class PortfolioManager:
    """
    Manages trading portfolio, positions, and risk
    """

    def __init__(
        self,
        initial_capital: float,
        daily_loss_limit: float = 0.05,  # 5% daily loss
        max_trades_per_day: int = 10,
        max_position_size: float = 0.02,  # 2% per position
        risk_level: RiskLevel = RiskLevel.MEDIUM
    ):
        """
        Initialize portfolio manager
        
        Args:
            initial_capital: Starting capital
            daily_loss_limit: Daily loss limit as percentage
            max_trades_per_day: Maximum trades allowed per day
            max_position_size: Maximum position size as percentage of capital
            risk_level: Risk level (low, medium, high)
        """
        self.initial_capital = initial_capital
        self.current_balance = initial_capital
        self.daily_loss_limit = daily_loss_limit
        self.max_trades_per_day = max_trades_per_day
        self.max_position_size = max_position_size
        self.risk_level = risk_level
        
        self.positions: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.last_reset_date = datetime.now().date()
        
        # Risk limits based on level
        self._set_risk_limits()

    def _set_risk_limits(self):
        """Set risk parameters based on risk level"""
        risk_params = {
            RiskLevel.LOW: {
                'max_position_size': 0.01,  # 1%
                'stop_loss_pct': 0.02,  # 2%
                'take_profit_pct': 0.04,  # 4%
                'max_positions': 3,
            },
            RiskLevel.MEDIUM: {
                'max_position_size': 0.02,  # 2%
                'stop_loss_pct': 0.03,  # 3%
                'take_profit_pct': 0.06,  # 6%
                'max_positions': 5,
            },
            RiskLevel.HIGH: {
                'max_position_size': 0.05,  # 5%
                'stop_loss_pct': 0.05,  # 5%
                'take_profit_pct': 0.10,  # 10%
                'max_positions': 10,
            },
        }
        self.risk_params = risk_params[self.risk_level]

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        risk_amount: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on risk management
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_amount: Amount willing to risk (% of capital)
        
        Returns:
            Position size
        """
        if risk_amount is None:
            risk_amount = self.current_balance * self.max_position_size
        
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit == 0:
            return 0
        
        position_size = risk_amount / risk_per_unit
        return position_size

    def add_position(
        self,
        symbol: str,
        entry_price: float,
        quantity: float,
        stop_loss: float,
        take_profit: float,
        position_type: str = 'LONG'  # LONG or SHORT
    ) -> bool:
        """
        Add a new position
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            quantity: Quantity
            stop_loss: Stop loss price
            take_profit: Take profit price
            position_type: LONG or SHORT
        
        Returns:
            True if position added, False otherwise
        """
        # Check daily loss limit
        if self.daily_pnl < -(self.initial_capital * self.daily_loss_limit):
            logger.warning("Daily loss limit reached")
            return False
        
        # Check daily trade limit
        self._reset_daily_limit()
        if self.daily_trades >= self.max_trades_per_day:
            logger.warning("Daily trade limit reached")
            return False
        
        # Check max positions
        if len(self.positions) >= self.risk_params['max_positions']:
            logger.warning("Maximum open positions reached")
            return False
        
        # Check position size
        position_cost = entry_price * quantity
        if position_cost > self.current_balance:
            logger.warning("Insufficient balance")
            return False
        
        # Create position
        self.positions[symbol] = {
            'entry_price': entry_price,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_type': position_type,
            'entry_time': datetime.now(),
            'trailing_stop': None,
            'initial_sl': stop_loss,
        }
        
        self.current_balance -= position_cost
        self.daily_trades += 1
        
        logger.info(f"Position added: {symbol}, Size: {quantity}")
        return True

    def close_position(
        self,
        symbol: str,
        exit_price: float,
        reason: str = 'MANUAL'
    ) -> Optional[Dict]:
        """
        Close a position
        
        Args:
            symbol: Trading symbol
            exit_price: Exit price
            reason: Reason for closing
        
        Returns:
            Position dict with P&L or None
        """
        if symbol not in self.positions:
            return None
        
        position = self.positions.pop(symbol)
        
        # Calculate P&L
        if position['position_type'] == 'LONG':
            pnl = (exit_price - position['entry_price']) * position['quantity']
            pnl_pct = ((exit_price / position['entry_price']) - 1) * 100
        else:  # SHORT
            pnl = (position['entry_price'] - exit_price) * position['quantity']
            pnl_pct = ((position['entry_price'] / exit_price) - 1) * 100
        
        position['exit_price'] = exit_price
        position['exit_time'] = datetime.now()
        position['pnl'] = pnl
        position['pnl_pct'] = pnl_pct
        position['reason'] = reason
        
        self.current_balance += (position['quantity'] * exit_price)
        self.daily_pnl += pnl
        self.trade_history.append(position)
        
        logger.info(f"Position closed: {symbol}, P&L: {pnl}")
        return position

    def update_trailing_stop(
        self,
        symbol: str,
        current_price: float,
        trail_amount: float
    ) -> bool:
        """
        Update trailing stop for a position
        
        Args:
            symbol: Trading symbol
            current_price: Current price
            trail_amount: Trailing amount
        
        Returns:
            True if stop was updated
        """
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        
        if position['position_type'] == 'LONG':
            new_sl = current_price - trail_amount
            if new_sl > position['stop_loss']:
                position['stop_loss'] = new_sl
                position['trailing_stop'] = new_sl
                return True
        else:  # SHORT
            new_sl = current_price + trail_amount
            if new_sl < position['stop_loss']:
                position['stop_loss'] = new_sl
                position['trailing_stop'] = new_sl
                return True
        
        return False

    def check_stop_loss(
        self,
        symbol: str,
        current_price: float
    ) -> bool:
        """
        Check if position hit stop loss
        
        Args:
            symbol: Trading symbol
            current_price: Current price
        
        Returns:
            True if stop loss hit
        """
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        
        if position['position_type'] == 'LONG':
            if current_price <= position['stop_loss']:
                return True
        else:  # SHORT
            if current_price >= position['stop_loss']:
                return True
        
        return False

    def check_take_profit(
        self,
        symbol: str,
        current_price: float
    ) -> bool:
        """
        Check if position hit take profit
        
        Args:
            symbol: Trading symbol
            current_price: Current price
        
        Returns:
            True if take profit hit
        """
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        
        if position['position_type'] == 'LONG':
            if current_price >= position['take_profit']:
                return True
        else:  # SHORT
            if current_price <= position['take_profit']:
                return True
        
        return False

    def get_open_positions(self) -> List[Dict]:
        """Get list of open positions"""
        positions_list = []
        for symbol, pos in self.positions.items():
            pos['symbol'] = symbol
            positions_list.append(pos)
        return positions_list

    def _reset_daily_limit(self):
        """Reset daily limits if new day"""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.last_reset_date = today

    def get_metrics(self) -> PortfolioMetrics:
        """Get portfolio metrics"""
        self._reset_daily_limit()
        
        # Calculate current equity
        open_position_value = sum([
            pos['quantity'] * pos['entry_price']
            for pos in self.positions.values()
        ])
        
        equity = self.current_balance + open_position_value
        return_pct = ((equity - self.initial_capital) / self.initial_capital) * 100
        
        # Calculate drawdown
        peak_equity = max([self.initial_capital] + [
            pos.get('equity', self.initial_capital)
            for pos in self.trade_history
        ])
        drawdown_pct = ((peak_equity - equity) / peak_equity) * 100 if peak_equity > 0 else 0
        
        # Calculate win rate
        winning_trades = sum([
            1 for pos in self.trade_history
            if pos.get('pnl', 0) > 0
        ])
        win_rate = (winning_trades / len(self.trade_history) * 100) if self.trade_history else 0
        
        return PortfolioMetrics(
            total_capital=self.initial_capital,
            current_balance=self.current_balance,
            used_margin=open_position_value,
            free_margin=self.current_balance,
            equity=equity,
            return_pct=return_pct,
            drawdown_pct=drawdown_pct,
            win_rate=win_rate,
            total_trades=len(self.trade_history),
            open_positions=len(self.positions)
        )

    def get_performance_summary(self) -> Dict:
        """Get performance summary"""
        metrics = self.get_metrics()
        
        return {
            'total_capital': metrics.total_capital,
            'current_equity': metrics.equity,
            'return_pct': metrics.return_pct,
            'drawdown_pct': metrics.drawdown_pct,
            'win_rate': metrics.win_rate,
            'total_trades': metrics.total_trades,
            'open_positions': metrics.open_positions,
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
        }


if __name__ == "__main__":
    print("Portfolio Manager initialized successfully")
