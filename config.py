"""
Configuration file for Trading Application
Customize settings here
"""

# ============================================
# API Configuration
# ============================================

# Binance API (for real trading - optional)
BINANCE_API_KEY = ""
BINANCE_API_SECRET = ""
BINANCE_TESTNET = True  # Use testnet for testing

# Telegram Configuration
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
TELEGRAM_ENABLED = False

# Mudrex API Configuration
MUDREX_ENABLED = False
MUDREX_API_KEY = ""
MUDREX_API_SECRET = ""
MUDREX_BASE_URL = "https://api.mudrex.com"

# ============================================
# Trading Configuration
# ============================================

# Default Capital
INITIAL_CAPITAL = 10000

# Daily Loss Limit (as decimal, e.g., 0.05 = 5%)
DAILY_LOSS_LIMIT = 0.05

# Max Trades Per Day
MAX_TRADES_PER_DAY = 10

# Default Max Position Size (as decimal)
MAX_POSITION_SIZE = 0.02  # 2%

# Risk Levels
RISK_LEVELS = {
    'low': {
        'max_position_size': 0.01,
        'stop_loss_pct': 0.02,
        'take_profit_pct': 0.04,
        'max_positions': 3,
    },
    'medium': {
        'max_position_size': 0.02,
        'stop_loss_pct': 0.03,
        'take_profit_pct': 0.06,
        'max_positions': 5,
    },
    'high': {
        'max_position_size': 0.05,
        'stop_loss_pct': 0.05,
        'take_profit_pct': 0.10,
        'max_positions': 10,
    },
}

# ============================================
# Strategy Configuration
# ============================================

# Strategy Parameters
STRATEGY_PARAMS = {
    'ema_fast': 9,
    'ema_slow': 26,
    'ema_ultra': 200,
    'rsi_period': 14,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'bollinger_period': 20,
    'atr_period': 14,
}

# Minimum Confidence for Signals
MIN_CONFIDENCE = 60

# Risk/Reward Ratio
RISK_REWARD_RATIO = 2.0

# ============================================
# Backtesting Configuration
# ============================================

# Backtest Initial Capital
BACKTEST_CAPITAL = 10000

# Trading Commission (as decimal, e.g., 0.001 = 0.1%)
TRADING_COMMISSION = 0.001

# ============================================
# UI Configuration
# ============================================

# Dark Theme
DARK_THEME_ENABLED = True

# Chart Height (pixels)
CHART_HEIGHT = 500

# Refresh Interval (seconds)
REFRESH_INTERVAL = 5

# ============================================
# Data Configuration
# ============================================

# Default Data Period
DEFAULT_PERIOD = '30d'

# Default Timeframe
DEFAULT_TIMEFRAME = '1h'

# Supported Assets
CRYPTO_ASSETS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']
STOCK_ASSETS = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'NIFTY', 'MARUTI.NS']

# ============================================
# Logging Configuration
# ============================================

# Log Directory
LOG_DIR = 'trading_logs'

# Log Level
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# ============================================
# Alert Configuration
# ============================================

# Enable Alerts
ALERTS_ENABLED = True

# Sound Alert Enabled
SOUND_ALERTS_ENABLED = True

# Alert Types
ALERT_TYPES = [
    'ema_crossover',
    'rsi_level',
    'macd_crossover',
    'breakout',
    'target_hit',
    'stop_loss_hit',
    'volume_spike',
    'trend_change',
]

# ============================================
# Advanced Settings
# ============================================

# AI Features Enabled
AI_FEATURES_ENABLED = True

# Trend Detection Enabled
TREND_DETECTION_ENABLED = True

# Entry Zone Detection Enabled
ENTRY_ZONE_DETECTION_ENABLED = True

# Fake Breakout Detection Enabled
FAKE_BREAKOUT_DETECTION_ENABLED = True

# Paper Trading (Simulated)
PAPER_TRADING = True

# Real Trading (Only if API keys configured)
REAL_TRADING = False

# ============================================
# Performance Optimization
# ============================================

# Cache Enabled
CACHE_ENABLED = True

# Cache TTL (seconds)
CACHE_TTL = 300

# Max Concurrent Data Requests
MAX_CONCURRENT_REQUESTS = 5
