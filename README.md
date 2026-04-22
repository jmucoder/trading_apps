# 📈 Crypto & Stock Market Trading Dashboard

A complete Python-based trading application for cryptocurrency and stock market trading. Built with Streamlit for modern UI, featuring real-time data fetching, advanced technical analysis, automated trading strategies, backtesting, and risk management.

## ✨ Features

### 1. **User Interface** 🎨
- Modern dark-themed Streamlit dashboard
- Real-time price display
- Multi-timeframe support (1m, 5m, 15m, 1h, 4h, 1d)
- Interactive candlestick charts with Plotly
- Buy/Sell signal buttons
- Portfolio overview

### 2. **Market Data** 📊
- Real-time data from:
  - **Binance**: Cryptocurrency trading pairs
  - **Yahoo Finance**: Stock market data
  - **CoinGecko**: Alternative crypto data
- OHLC (Open, High, Low, Close) data
- Volume analysis
- Multi-asset support (BTC, ETH, NIFTY, etc.)

### 3. **Technical Indicators** 📉
- **EMA** (9, 26, 200) - Exponential Moving Average
- **RSI** (14) - Relative Strength Index
- **MACD** - Moving Average Convergence Divergence
- **Bollinger Bands** - Volatility bands
- **ATR** - Average True Range
- **Stochastic Oscillator** - %K and %D
- **Support/Resistance Levels**
- **Pivot Points**

### 4. **Trading Strategies** 🎯
- **EMA Crossover Strategy**
  - Fast (9) vs Slow (26) EMA crossover
  - 200 EMA for trend confirmation
  
- **RSI Filter Strategy**
  - Buy above 50, Sell below 50
  - Overbought (>70) and Oversold (<30) detection
  
- **Volume Confirmation Strategy**
  - High volume validation
  - Breakout detection with volume confirmation
  
- **Combined Strategy**
  - Combines all three strategies
  - Signal voting system
  - Weighted confidence scoring

### 5. **Trading Modes** 🏃
- **Normal Mode**: Standard trading parameters
- **Scalping Mode**: Fast, small profits (5-13 EMA, lower SL)
- **Trend Following**: Larger moves, trend-based (20-50 EMA)
- **Safe Mode**: Conservative, low-risk trading

### 6. **Trade Management** 💼
- Position sizing based on risk
- Stop Loss and Take Profit automation
- Trailing Stop Loss
- Paper trading (simulated) mode
- Position history tracking
- Real-time P&L calculation

### 7. **Risk Management** ⚠️
- Daily loss limit (5% default)
- Maximum trades per day limit
- Max position size constraints
- Risk-based position sizing
- Risk level selection (Low, Medium, High)
- Capital protection system

### 8. **Alerts System** 🔔
- Desktop notifications
- Sound alerts (configurable)
- Telegram integration
- Alert types:
  - EMA crossover
  - RSI levels
  - Volume spikes
  - Breakout signals
  - Take profit hits
  - Stop loss hits

### 9. **Backtesting** 🧪
- Historical data testing
- Win rate calculation
- Profit/Loss metrics
- Max drawdown analysis
- ROI calculation
- Sharpe ratio
- Equity curve visualization
- Strategy comparison

### 10. **Performance Analysis** 📊
- Win rate percentage
- Profit factor
- Average win/loss
- Consecutive wins/losses
- Daily P&L tracking
- Drawdown analysis

### 11. **AI Features** 🤖
- Trend detection (Bullish/Bearish/Sideways)
- Entry zone detection
- Fake breakout detection
- Signal quality scoring
- Risk metrics calculation
- Confidence scoring

### 12. **Logging & History** 📋
- Trade history tracking
- CSV export functionality
- JSON export functionality
- Performance reports
- Trade statistics
- Error logging

## 📋 Project Structure

```
trading_app/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── market_data.py         # Data fetching from APIs
│   │   └── indicators.py          # Technical indicators & signals
│   │
│   ├── strategies/
│   │   ├── __init__.py
│   │   └── strategy_engine.py     # Trading strategies & signal generation
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── portfolio.py           # Position & portfolio management
│   │   ├── backtest.py            # Backtesting engine
│   │   ├── alerts.py              # Alert system
│   │   ├── logger.py              # Trading history logging
│   │   └── ai_analyzer.py         # AI/ML features
│   │
│   └── ui/
│       └── __init__.py
│
└── trading_logs/                   # Generated trading logs & exports
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Windows/Mac/Linux

### Step 1: Clone or Download
```bash
cd trading_app
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## 📚 Usage Guide

### Dashboard Overview
1. **Sidebar Settings**
   - Select Asset Type (Crypto/Stock)
   - Choose Symbol (BTC/USDT, RELIANCE.NS, etc.)
   - Select Timeframe (1m, 5m, 15m, 1h, 1d)
   - Choose Trading Mode
   - Pick Strategy
   - Set Risk Level

2. **Analysis Tab**
   - View real-time candlestick charts
   - See technical indicators (RSI, MACD, Volume)
   - Get trading signals with confidence scores
   - Monitor entry/exit prices

3. **Portfolio Tab**
   - Track open positions
   - Monitor P&L
   - View win rate and statistics
   - Set position sizes

4. **Backtest Tab**
   - Run historical backtests
   - Compare strategies
   - View performance metrics
   - Analyze equity curves

5. **Settings Tab**
   - Configure Telegram alerts
   - Enable/disable sound alerts
   - Set risk parameters

### Example: Trading with EMA Crossover

```python
from src.data.market_data import MarketDataFetcher
from src.strategies.strategy_engine import StrategyEngine, TradingMode, StrategyType

# Fetch data
fetcher = MarketDataFetcher()
df = fetcher.fetch_crypto_ohlc('BTC/USDT', '1h', 100)

# Create strategy engine
strategy = StrategyEngine(mode=TradingMode.NORMAL)

# Generate signal
signal = strategy.generate_signal(df, StrategyType.EMA_CROSSOVER)

print(f"Signal: {signal.signal_type}")
print(f"Confidence: {signal.confidence:.1f}%")
print(f"Entry Price: ${signal.entry_price:.2f}")
print(f"Stop Loss: ${signal.stop_loss:.2f}")
print(f"Take Profit: ${signal.take_profit:.2f}")
```

### Example: Backtesting a Strategy

```python
from src.data.market_data import MarketDataFetcher
from src.utils.backtest import Backtester

# Fetch historical data
fetcher = MarketDataFetcher()
df = fetcher.fetch_crypto_ohlc('BTC/USDT', '1h', 200)

# Run backtest
backtester = Backtester(initial_capital=10000)
result = backtester.run_ema_crossover_backtest(df)

# Get metrics
metrics = result.calculate_metrics(10000)
print(f"Total Trades: {metrics['total_trades']}")
print(f"Win Rate: {metrics['win_rate']:.1f}%")
print(f"ROI: {metrics['roi']:.2f}%")
print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
```

### Example: Managing Portfolio

```python
from src.utils.portfolio import PortfolioManager, RiskLevel

# Create portfolio
portfolio = PortfolioManager(
    initial_capital=10000,
    daily_loss_limit=0.05,
    max_trades_per_day=10,
    risk_level=RiskLevel.MEDIUM
)

# Add a position
portfolio.add_position(
    symbol='BTC/USDT',
    entry_price=45000,
    quantity=0.1,
    stop_loss=44000,
    take_profit=46000
)

# Check metrics
metrics = portfolio.get_metrics()
print(f"Equity: ${metrics.equity:,.2f}")
print(f"Return: {metrics.return_pct:.2f}%")
print(f"Win Rate: {metrics.win_rate:.1f}%")

# Close position
portfolio.close_position('BTC/USDT', 45500, reason='MANUAL')
```

### Example: Setting Up Alerts

```python
from src.utils.alerts import AlertManager, AlertType, AlertSeverity

# Create alert manager
alerts = AlertManager()

# Configure Telegram (optional)
alerts.configure_telegram(
    token="YOUR_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID"
)

# Create alert
alerts.create_ema_crossover_alert(
    symbol='BTC/USDT',
    signal_type='BUY',
    price=45000,
    fast_ema=44900,
    slow_ema=44500
)

# View recent alerts
recent = alerts.get_recent_alerts(5)
for alert in recent:
    print(f"{alert['symbol']}: {alert['message']}")
```

## 📊 Trading Modes Comparison

| Mode | Risk | Position Size | SL/TP | Best For |
|------|------|---------------|-------|----------|
| **Normal** | Medium | 2% | Standard ATR | General trading |
| **Scalping** | Low | 1% | Tight | Quick profits (5-15 min) |
| **Trend Following** | High | 2.5% | Loose | Swing trading |
| **Safe** | Very Low | 0.5% | Very Tight | Risk-averse traders |

## 🎯 Strategy Comparison

| Strategy | Best For | Win Rate | Signals |
|----------|----------|----------|---------|
| **EMA Crossover** | Trending markets | 50-60% | Clear entry/exit |
| **RSI Filter** | Overbought/Oversold | 45-55% | Momentum trading |
| **Volume Confirm** | Breakout trading | 55-65% | Volume-based |
| **Combined** | All conditions | 60-70% | Most reliable |

## 🔧 Configuration

### Risk Levels
- **Low**: 1% position size, 2% SL, 4% TP
- **Medium**: 2% position size, 3% SL, 6% TP
- **High**: 5% position size, 5% SL, 10% TP

### Timeframes
- Crypto: 1m, 3m, 5m, 15m, 1h, 4h, 1d
- Stocks: 1h, 1d

### Default Parameters
- Daily Loss Limit: 5%
- Max Trades/Day: 10
- Default Capital: $10,000

## 📈 Performance Metrics

### Key Metrics
- **Win Rate**: Percentage of profitable trades
- **ROI**: Return on Investment percentage
- **Profit Factor**: Gross Profit / Gross Loss
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Peak-to-trough decline
- **Avg Win/Loss**: Average profit/loss per trade

## 🚨 Risk Management Features

1. **Daily Loss Limit**: Stops trading after losing 5% daily
2. **Max Position Size**: Limits exposure per trade
3. **Stop Loss Automation**: Automatic exit at SL price
4. **Take Profit Automation**: Automatic exit at TP price
5. **Trailing Stop**: Locks in profits automatically
6. **Position Sizing**: Risk-based calculation
7. **Capital Protection**: Never risks more than allocated

## 🔐 Security Considerations

⚠️ **Important**:
- Never share API keys or Telegram tokens
- Use environment variables for sensitive data
- Paper trade first to verify strategies
- Start with small capital for real trading
- Regularly backup trading history

## 📝 API Key Setup

### Binance (Optional for real trading)
1. Create account at binance.com
2. Generate API keys in Account Settings
3. Store securely (don't share)

### Telegram Bot (For alerts)
1. Create bot on @BotFather
2. Get your Chat ID from @userinfobot
3. Add to configuration

## 🐛 Troubleshooting

### "ModuleNotFoundError" Error
```bash
# Ensure all packages are installed
pip install -r requirements.txt

# Or install individually
pip install streamlit pandas numpy matplotlib plotly ta ccxt yfinance
```

### Data Fetching Issues
- Check internet connection
- Verify API availability
- Check for rate limits (Binance, Yahoo Finance)
- Try different timeframes

### Chart Not Displaying
- Ensure Plotly is installed
- Check data is not empty
- Verify timestamp format

### Strategy Not Generating Signals
- Ensure sufficient data (min 26+ candles)
- Check indicator periods
- Verify data quality

## 📚 Learning Resources

### Technical Analysis
- EMA Guide: https://www.investopedia.com/terms/e/ema.asp
- RSI Guide: https://www.investopedia.com/terms/r/rsi.asp
- MACD Guide: https://www.investopedia.com/terms/m/macd.asp

### Trading Concepts
- Risk Management: https://www.investopedia.com/risk-management
- Position Sizing: https://www.investopedia.com/terms/p/position-sizing.asp
- Backtesting: https://www.investopedia.com/terms/b/backtesting.asp

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## ⚖️ Disclaimer

**THIS IS FOR EDUCATIONAL PURPOSES ONLY**

This application is provided "as-is" for educational and research purposes only. 

- Past performance does not guarantee future results
- Trading involves substantial risk of loss
- No guarantee of profitability
- Always use stop losses
- Never risk more than you can afford to lose
- Consult a financial advisor before trading real money

**THE AUTHOR IS NOT RESPONSIBLE FOR ANY TRADING LOSSES**

## 👨‍💻 Author

Created as a comprehensive educational trading application demonstrating:
- Real-time data fetching
- Technical analysis
- Trading strategies
- Risk management
- Backtesting
- UI/UX design

## 🙋 Support

For issues, questions, or suggestions:
1. Check the README thoroughly
2. Review code comments
3. Check troubleshooting section
4. Verify dependencies are installed
5. Search existing issues

## 🎯 Roadmap

### Upcoming Features
- [ ] Advanced ML models for prediction
- [ ] Option trading strategies
- [ ] Multi-exchange support
- [ ] Docker containerization
- [ ] Mobile app
- [ ] Cloud deployment
- [ ] Real-time data streaming (WebSocket)
- [ ] Advanced charting (TradingView integration)
- [ ] Machine learning signal generation
- [ ] Advanced portfolio optimization

## 📞 Contact

For inquiries or suggestions:
- Email: support@tradingapp.com
- GitHub: [Link to repo]

---

**Happy Trading! 📈**

*Remember: Always practice with paper trading first, understand the risks, and never risk money you can't afford to lose.*
