"""
Example 1: Basic Data Fetching and Analysis
Shows how to fetch market data and calculate indicators
"""

import sys
sys.path.insert(0, '.')

from src.data.market_data import MarketDataFetcher, DataProcessor
from src.data.indicators import TechnicalIndicators, SignalGenerator

def example_basic_analysis():
    """Example: Fetch data and analyze with indicators"""
    
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Data Fetching and Analysis")
    print("="*60)
    
    # Initialize fetcher
    fetcher = MarketDataFetcher()
    
    # Fetch crypto data (BTC/USDT, 1-hour candles, 50 periods)
    print("\n[1] Fetching Bitcoin data...")
    btc_data = fetcher.fetch_crypto_ohlc('BTC/USDT', '1h', 50)
    
    if btc_data.empty:
        print("ERROR: Could not fetch data")
        return
    
    print(f"✓ Fetched {len(btc_data)} candles")
    print(f"Latest price: ${btc_data['close'].iloc[-1]:.2f}")
    
    # Calculate technical indicators
    print("\n[2] Calculating indicators...")
    
    # EMA
    ema_9 = TechnicalIndicators.calculate_ema(btc_data['close'], 9)
    ema_26 = TechnicalIndicators.calculate_ema(btc_data['close'], 26)
    ema_200 = TechnicalIndicators.calculate_ema(btc_data['close'], 200)
    
    print(f"EMA 9: ${ema_9.iloc[-1]:.2f}")
    print(f"EMA 26: ${ema_26.iloc[-1]:.2f}")
    print(f"EMA 200: ${ema_200.iloc[-1]:.2f}")
    
    # RSI
    rsi = TechnicalIndicators.calculate_rsi(btc_data['close'], 14)
    print(f"RSI (14): {rsi.iloc[-1]:.2f}")
    
    # MACD
    macd, signal, histogram = TechnicalIndicators.calculate_macd(btc_data['close'])
    print(f"MACD: {macd.iloc[-1]:.6f}")
    print(f"Signal: {signal.iloc[-1]:.6f}")
    print(f"Histogram: {histogram.iloc[-1]:.6f}")
    
    # Generate signals
    print("\n[3] Generating trading signals...")
    
    ema_signal = SignalGenerator.ema_crossover_signal(btc_data)
    rsi_signal = SignalGenerator.rsi_signal(btc_data)
    macd_signal = SignalGenerator.macd_signal(btc_data)
    
    print(f"EMA Crossover Signal: {ema_signal}")
    print(f"RSI Signal: {rsi_signal}")
    print(f"MACD Signal: {macd_signal}")
    
    # Volume confirmation
    vol_confirm = SignalGenerator.volume_confirmation(btc_data)
    print(f"Volume Confirmation: {'YES' if vol_confirm else 'NO'}")
    
    # Confidence score
    confidence, breakdown = SignalGenerator.calculate_confidence_score(btc_data)
    print(f"\nOverall Confidence Score: {confidence:.1f}%")
    print(f"Signal Breakdown: {breakdown}")
    
    print("\n" + "="*60)
    print("Example 1 Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    example_basic_analysis()
