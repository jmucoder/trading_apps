"""
Market Data Fetcher Module
Fetches real-time and historical market data from multiple sources
Supports: Binance, CoinGecko, Yahoo Finance
"""

import pandas as pd
import numpy as np
import yfinance as yf
import ccxt
from datetime import datetime, timedelta
import requests
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataFetcher:
    """
    Fetches market data from multiple sources
    Supports crypto (Binance, CoinGecko) and stocks (Yahoo Finance)
    """

    def __init__(self):
        """Initialize market data fetcher with different APIs"""
        self.binance = ccxt.binance()
        self.currencies = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA']
        self.stocks = ['NIFTY', 'RELIANCE.NS', 'TCS.NS', 'INFY.NS']

    def fetch_crypto_ohlc(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Fetch OHLC data from Binance
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Time interval ('1m', '5m', '15m', '1h', '1d')
            limit: Number of candles to fetch
        
        Returns:
            DataFrame with OHLC data
        """
        try:
            # Convert timeframe to CCXT format
            timeframe_map = {
                '1m': '1m', '3m': '3m', '5m': '5m',
                '15m': '15m', '1h': '1h', '4h': '4h', '1d': '1d'
            }
            
            tf = timeframe_map.get(timeframe, '1h')
            
            # Fetch OHLCV data from Binance
            ohlcv = self.binance.fetch_ohlcv(symbol, tf, limit=limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = symbol
            df['source'] = 'Binance'
            
            logger.info(f"Fetched {len(df)} candles for {symbol} on {timeframe}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching crypto data: {str(e)}")
            return pd.DataFrame()

    def fetch_stock_ohlc(
        self,
        symbol: str,
        interval: str = '1h',
        period: str = '30d'
    ) -> pd.DataFrame:
        """
        Fetch OHLC data from Yahoo Finance
        
        Args:
            symbol: Stock ticker (e.g., 'RELIANCE.NS')
            interval: Time interval ('1m', '5m', '15m', '1h', '1d')
            period: Historical period ('1d', '5d', '30d', '1y')
        
        Returns:
            DataFrame with OHLC data
        """
        try:
            # Fetch data from Yahoo Finance
            data = yf.download(
                symbol,
                interval=interval,
                period=period,
                progress=False
            )
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return pd.DataFrame()
            
            # Reset index and rename columns
            data = data.reset_index()
            data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'adj_close']
            data['symbol'] = symbol
            data['source'] = 'Yahoo Finance'
            
            # Drop adj_close as we have close price
            data = data.drop('adj_close', axis=1)
            
            logger.info(f"Fetched {len(data)} candles for {symbol} on {interval}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching stock data: {str(e)}")
            return pd.DataFrame()

    def fetch_crypto_current_price(self, symbol: str) -> Dict:
        """
        Fetch current price of cryptocurrency
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
        
        Returns:
            Dictionary with price and market data
        """
        try:
            ticker = self.binance.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'current_price': ticker['last'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'volume': ticker['quoteVolume'],
                'change_24h': ticker['percentage'],
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching price: {str(e)}")
            return {}

    def fetch_stock_current_price(self, symbol: str) -> Dict:
        """
        Fetch current price of stock
        
        Args:
            symbol: Stock ticker (e.g., 'RELIANCE.NS')
        
        Returns:
            Dictionary with price and market data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            
            if data.empty:
                return {}
            
            latest = data.iloc[-1]
            return {
                'symbol': symbol,
                'current_price': latest['Close'],
                'high_24h': latest['High'],
                'low_24h': latest['Low'],
                'volume': latest['Volume'],
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error fetching stock price: {str(e)}")
            return {}

    def fetch_multiple_crypto(
        self,
        symbols: List[str],
        timeframe: str = '1h',
        limit: int = 100
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch OHLC data for multiple cryptocurrencies
        
        Args:
            symbols: List of trading pairs
            timeframe: Time interval
            limit: Number of candles per symbol
        
        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        data = {}
        for symbol in symbols:
            df = self.fetch_crypto_ohlc(symbol, timeframe, limit)
            if not df.empty:
                data[symbol] = df
        return data

    def fetch_multiple_stocks(
        self,
        symbols: List[str],
        interval: str = '1h',
        period: str = '30d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch OHLC data for multiple stocks
        
        Args:
            symbols: List of stock tickers
            interval: Time interval
            period: Historical period
        
        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        data = {}
        for symbol in symbols:
            df = self.fetch_stock_ohlc(symbol, interval, period)
            if not df.empty:
                data[symbol] = df
        return data


class DataProcessor:
    """
    Process and calculate technical indicators on market data
    """

    @staticmethod
    def add_volume_sma(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate SMA of volume"""
        df['volume_sma'] = df['volume'].rolling(window=period).mean()
        return df

    @staticmethod
    def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily returns"""
        df['returns'] = df['close'].pct_change()
        return df

    @staticmethod
    def detect_trend(df: pd.DataFrame, ema_period: int = 200) -> str:
        """
        Detect trend direction
        
        Args:
            df: OHLC DataFrame
            ema_period: EMA period for trend detection
        
        Returns:
            'UPTREND', 'DOWNTREND', or 'SIDEWAYS'
        """
        if df.empty or len(df) < ema_period:
            return 'UNKNOWN'

        df['ema_200'] = df['close'].ewm(span=ema_period, adjust=False).mean()
        
        current_price = df['close'].iloc[-1]
        ema_200 = df['ema_200'].iloc[-1]
        
        # Check if price is above or below EMA 200
        if current_price > ema_200 * 1.01:  # 1% buffer
            return 'UPTREND'
        elif current_price < ema_200 * 0.99:
            return 'DOWNTREND'
        else:
            return 'SIDEWAYS'

    @staticmethod
    def validate_data(df: pd.DataFrame) -> bool:
        """Validate data integrity"""
        if df.empty:
            return False
        
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in df.columns for col in required_columns)


if __name__ == "__main__":
    # Test the market data fetcher
    fetcher = MarketDataFetcher()
    
    # Fetch crypto data
    btc_data = fetcher.fetch_crypto_ohlc('BTC/USDT', '1h', 50)
    print("BTC Data:")
    print(btc_data.head())
    
    # Fetch stock data
    stock_data = fetcher.fetch_stock_ohlc('RELIANCE.NS', '1d', '30d')
    print("\nStock Data:")
    print(stock_data.head())
