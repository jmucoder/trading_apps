"""
Example 2: Strategy Generation and Trading Signals
Shows how to use the strategy engine to generate trading signals
"""

import sys
sys.path.insert(0, '.')

from src.data.market_data import MarketDataFetcher
from src.strategies.strategy_engine import StrategyEngine, TradingMode, StrategyType

def example_strategy_signals():
    """Example: Generate trading signals using different strategies and modes"""
    
    print("\n" + "="*60)
    print("EXAMPLE 2: Strategy Generation and Trading Signals")
    print("="*60)
    
    # Fetch data
    print("\n[1] Fetching market data...")
    fetcher = MarketDataFetcher()
    df = fetcher.fetch_crypto_ohlc('ETH/USDT', '1h', 100)
    
    if df.empty:
        print("ERROR: Could not fetch data")
        return
    
    print(f"✓ Fetched {len(df)} candles for ETH/USDT")
    
    # Test different modes
    modes = [
        TradingMode.NORMAL,
        TradingMode.SCALPING,
        TradingMode.TREND_FOLLOWING,
        TradingMode.SAFE,
    ]
    
    strategies = [
        StrategyType.EMA_CROSSOVER,
        StrategyType.RSI_FILTER,
        StrategyType.VOLUME_CONFIRMATION,
        StrategyType.COMBINED,
    ]
    
    print("\n[2] Testing Trading Strategies and Modes")
    print("-" * 60)
    
    for mode in modes:
        print(f"\n>>> {mode.value.upper()} MODE")
        
        engine = StrategyEngine(mode=mode)
        
        for strategy in strategies:
            signal = engine.generate_signal(df, strategy)
            
            print(f"\n  Strategy: {strategy.value}")
            print(f"  Signal: {signal.signal_type}")
            print(f"  Confidence: {signal.confidence:.1f}%")
            print(f"  Entry Price: ${signal.entry_price:.2f}")
            if signal.stop_loss:
                print(f"  Stop Loss: ${signal.stop_loss:.2f}")
            if signal.take_profit:
                print(f"  Take Profit: ${signal.take_profit:.2f}")
            if signal.risk_reward_ratio:
                print(f"  R/R Ratio: {signal.risk_reward_ratio:.1f}x")
    
    print("\n" + "="*60)
    print("Strategy Comparison Summary")
    print("="*60)
    
    # Detailed comparison for COMBINED strategy
    print("\nTesting COMBINED strategy in all modes:")
    
    for mode in modes:
        engine = StrategyEngine(mode=mode)
        signal = engine.generate_signal(df, StrategyType.COMBINED)
        
        status = "🟢 BUY" if signal.signal_type == "BUY" else \
                 "🔴 SELL" if signal.signal_type == "SELL" else \
                 "🟡 HOLD"
        
        confidence_bar = "█" * int(signal.confidence / 10) + "░" * (10 - int(signal.confidence / 10))
        
        print(f"\n{mode.value.upper():20} {status:10} Confidence: [{confidence_bar}] {signal.confidence:.1f}%")
    
    print("\n" + "="*60)
    print("Example 2 Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    example_strategy_signals()
