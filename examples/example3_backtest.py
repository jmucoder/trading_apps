"""
Example 3: Backtesting Strategies
Shows how to backtest strategies on historical data
"""

import sys
sys.path.insert(0, '.')

from src.data.market_data import MarketDataFetcher
from src.utils.backtest import Backtester

def example_backtesting():
    """Example: Run backtest on historical data"""
    
    print("\n" + "="*60)
    print("EXAMPLE 3: Backtesting Trading Strategies")
    print("="*60)
    
    # Fetch historical data
    print("\n[1] Fetching historical data for backtest...")
    fetcher = MarketDataFetcher()
    df = fetcher.fetch_crypto_ohlc('BTC/USDT', '1h', 200)
    
    if df.empty:
        print("ERROR: Could not fetch data")
        return
    
    print(f"✓ Fetched {len(df)} candles from {df['timestamp'].iloc[0]} to {df['timestamp'].iloc[-1]}")
    
    # Initialize backtester
    initial_capital = 10000
    backtester = Backtester(initial_capital=initial_capital)
    
    print(f"\n[2] Running backtests with ${initial_capital:,.0f} initial capital")
    print("-" * 60)
    
    # Test EMA Crossover
    print("\nTesting EMA Crossover Strategy...")
    ema_result = backtester.run_ema_crossover_backtest(df)
    ema_metrics = ema_result.calculate_metrics(initial_capital)
    
    print(f"  Total Trades: {ema_metrics['total_trades']}")
    print(f"  Winning Trades: {ema_metrics['winning_trades']}")
    print(f"  Losing Trades: {ema_metrics['losing_trades']}")
    print(f"  Win Rate: {ema_metrics['win_rate']:.1f}%")
    print(f"  Total P&L: ${ema_metrics['total_pnl']:.2f}")
    print(f"  ROI: {ema_metrics['roi']:.2f}%")
    print(f"  Max Drawdown: {ema_metrics['max_drawdown']:.2f}%")
    print(f"  Profit Factor: {ema_metrics['profit_factor']:.2f}")
    print(f"  Sharpe Ratio: {ema_metrics['sharpe_ratio']:.2f}")
    
    # Test RSI Strategy
    print("\nTesting RSI Strategy...")
    rsi_result = backtester.run_rsi_backtest(df)
    rsi_metrics = rsi_result.calculate_metrics(initial_capital)
    
    print(f"  Total Trades: {rsi_metrics['total_trades']}")
    print(f"  Win Rate: {rsi_metrics['win_rate']:.1f}%")
    print(f"  ROI: {rsi_metrics['roi']:.2f}%")
    print(f"  Max Drawdown: {rsi_metrics['max_drawdown']:.2f}%")
    
    # Test Volume Breakout
    print("\nTesting Volume Breakout Strategy...")
    vol_result = backtester.run_volume_breakout_backtest(df)
    vol_metrics = vol_result.calculate_metrics(initial_capital)
    
    print(f"  Total Trades: {vol_metrics['total_trades']}")
    print(f"  Win Rate: {vol_metrics['win_rate']:.1f}%")
    print(f"  ROI: {vol_metrics['roi']:.2f}%")
    print(f"  Max Drawdown: {vol_metrics['max_drawdown']:.2f}%")
    
    # Compare strategies
    print("\n" + "-" * 60)
    print("STRATEGY COMPARISON")
    print("-" * 60)
    
    print(f"\n{'Strategy':<20} {'Win Rate':>12} {'ROI':>12} {'Sharpe':>12} {'DD':>12}")
    print("-" * 60)
    
    print(f"{'EMA Crossover':<20} {ema_metrics['win_rate']:>11.1f}% {ema_metrics['roi']:>11.2f}% {ema_metrics['sharpe_ratio']:>11.2f} {ema_metrics['max_drawdown']:>11.2f}%")
    print(f"{'RSI':<20} {rsi_metrics['win_rate']:>11.1f}% {rsi_metrics['roi']:>11.2f}% {rsi_metrics['sharpe_ratio']:>11.2f} {rsi_metrics['max_drawdown']:>11.2f}%")
    print(f"{'Volume Breakout':<20} {vol_metrics['win_rate']:>11.1f}% {vol_metrics['roi']:>11.2f}% {vol_metrics['sharpe_ratio']:>11.2f} {vol_metrics['max_drawdown']:>11.2f}%")
    
    # Show best strategy
    print("\n" + "="*60)
    best_strategy = max(
        [('EMA Crossover', ema_metrics), ('RSI', rsi_metrics), ('Volume Breakout', vol_metrics)],
        key=lambda x: x[1]['roi']
    )
    
    print(f"BEST STRATEGY: {best_strategy[0]} with ROI of {best_strategy[1]['roi']:.2f}%")
    print("="*60 + "\n")


if __name__ == "__main__":
    example_backtesting()
