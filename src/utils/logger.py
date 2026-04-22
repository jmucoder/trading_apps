"""
Trading History and Logging Module
Save and manage trading history, export to CSV
"""

import pandas as pd
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TradingLogger:
    """
    Log and manage trading history
    Supports CSV and JSON exports
    """

    def __init__(self, log_dir: str = "trading_logs"):
        """
        Initialize trading logger
        
        Args:
            log_dir: Directory to store logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.trades: List[Dict] = []
        self.alerts: List[Dict] = []
        self.errors: List[Dict] = []

    def log_trade(
        self,
        symbol: str,
        signal_type: str,
        entry_price: float,
        exit_price: Optional[float] = None,
        quantity: float = 0,
        pnl: Optional[float] = None,
        pnl_pct: Optional[float] = None,
        strategy: str = "",
        mode: str = "normal"
    ):
        """
        Log a trade
        
        Args:
            symbol: Trading symbol
            signal_type: BUY/SELL
            entry_price: Entry price
            exit_price: Exit price
            quantity: Quantity traded
            pnl: Profit/Loss
            pnl_pct: Profit/Loss percentage
            strategy: Trading strategy used
            mode: Trading mode
        """
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'signal_type': signal_type,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'strategy': strategy,
            'mode': mode,
        }
        
        self.trades.append(trade)
        logger.info(f"Trade logged: {symbol} {signal_type} @ {entry_price}")

    def log_alert(
        self,
        symbol: str,
        alert_type: str,
        message: str,
        severity: str = "info"
    ):
        """Log an alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'type': alert_type,
            'message': message,
            'severity': severity,
        }
        
        self.alerts.append(alert)

    def log_error(self, error_message: str, context: str = ""):
        """Log an error"""
        error = {
            'timestamp': datetime.now().isoformat(),
            'message': error_message,
            'context': context,
        }
        
        self.errors.append(error)
        logger.error(f"Error logged: {error_message}")

    def export_trades_csv(self, filename: Optional[str] = None) -> str:
        """
        Export trades to CSV
        
        Args:
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        if not self.trades:
            logger.warning("No trades to export")
            return ""

        if filename is None:
            filename = f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = self.log_dir / filename
        
        df = pd.DataFrame(self.trades)
        df.to_csv(filepath, index=False)
        
        logger.info(f"Trades exported to {filepath}")
        return str(filepath)

    def export_trades_json(self, filename: Optional[str] = None) -> str:
        """
        Export trades to JSON
        
        Args:
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        if not self.trades:
            logger.warning("No trades to export")
            return ""

        if filename is None:
            filename = f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.log_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(self.trades, f, indent=2)
        
        logger.info(f"Trades exported to {filepath}")
        return str(filepath)

    def export_performance_report(self, filename: Optional[str] = None) -> str:
        """
        Export performance report
        
        Args:
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        filepath = self.log_dir / filename

        # Calculate metrics
        df = pd.DataFrame(self.trades)
        
        if df.empty:
            logger.warning("No trades for performance report")
            return ""

        summary = {
            'Total Trades': len(df),
            'Winning Trades': len(df[df['pnl'] > 0]),
            'Losing Trades': len(df[df['pnl'] < 0]),
            'Win Rate %': (len(df[df['pnl'] > 0]) / len(df) * 100) if len(df) > 0 else 0,
            'Total P&L': df['pnl'].sum(),
            'Average P&L': df['pnl'].mean(),
            'Max Win': df['pnl'].max(),
            'Max Loss': df['pnl'].min(),
            'ROI %': (df['pnl'].sum() / (df['entry_price'].sum()) * 100) if df['entry_price'].sum() > 0 else 0,
        }

        summary_df = pd.DataFrame([summary])
        summary_df.to_csv(filepath, index=False)
        
        logger.info(f"Performance report exported to {filepath}")
        return str(filepath)

    def get_trades_dataframe(self) -> pd.DataFrame:
        """Get trades as DataFrame"""
        return pd.DataFrame(self.trades)

    def get_trade_statistics(self) -> Dict:
        """Get trade statistics"""
        if not self.trades:
            return {}

        df = pd.DataFrame(self.trades)
        
        winning = df[df['pnl'] > 0] if 'pnl' in df.columns else pd.DataFrame()
        losing = df[df['pnl'] < 0] if 'pnl' in df.columns else pd.DataFrame()

        stats = {
            'total_trades': len(df),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate_pct': (len(winning) / len(df) * 100) if len(df) > 0 else 0,
            'total_pnl': winning['pnl'].sum() - abs(losing['pnl'].sum()) if 'pnl' in df.columns else 0,
            'avg_win': winning['pnl'].mean() if len(winning) > 0 else 0,
            'avg_loss': losing['pnl'].mean() if len(losing) > 0 else 0,
            'profit_factor': (winning['pnl'].sum() / abs(losing['pnl'].sum())) if len(losing) > 0 and losing['pnl'].sum() != 0 else 0,
        }

        return stats

    def get_recent_trades(self, limit: int = 10) -> List[Dict]:
        """Get recent trades"""
        return self.trades[-limit:]

    def clear_history(self):
        """Clear all history"""
        self.trades = []
        self.alerts = []
        self.errors = []
        logger.info("Trading history cleared")


if __name__ == "__main__":
    logger = TradingLogger()
    print("Trading Logger initialized successfully")
