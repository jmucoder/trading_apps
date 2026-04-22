"""
Trading Application - Crypto & Stock Market Trading Platform
Main initialization file
"""

__version__ = "1.0.0"
__author__ = "Trading App Developer"
__description__ = "Complete Python-based trading application for crypto and stock market trading"

from src.data.market_data import MarketDataFetcher, DataProcessor
from src.data.indicators import TechnicalIndicators, SignalGenerator
from src.strategies.strategy_engine import StrategyEngine, TradingMode, StrategyType
from src.utils.portfolio import PortfolioManager, RiskLevel
from src.utils.backtest import Backtester
from src.utils.alerts import AlertManager
from src.utils.logger import TradingLogger
from src.utils.ai_analyzer import AIAnalyzer

__all__ = [
    'MarketDataFetcher',
    'DataProcessor',
    'TechnicalIndicators',
    'SignalGenerator',
    'StrategyEngine',
    'TradingMode',
    'StrategyType',
    'PortfolioManager',
    'RiskLevel',
    'Backtester',
    'AlertManager',
    'TradingLogger',
    'AIAnalyzer',
]
