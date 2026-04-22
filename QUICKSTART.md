# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Install Python
- Download Python 3.8+ from [python.org](https://www.python.org/)
- Make sure to check "Add Python to PATH" during installation

### Step 2: Clone/Download the Project
```bash
cd trading_app
```

### Step 3: Run Startup Script
**Windows:**
```bash
run.bat
```

**Mac/Linux:**
```bash
bash run.sh
```

### Step 4: Open Dashboard
- Automatically opens in your browser at `http://localhost:8501`
- If not, manually visit that URL

## 🎯 First Steps in the Dashboard

### 1. Select Your Asset
- Choose between Crypto or Stock
- Select symbol (BTC/USDT, RELIANCE.NS, etc.)
- Pick timeframe (1h, 1d, etc.)

### 2. Choose Trading Mode
- **Normal**: Standard trading
- **Scalping**: Quick trades (5-15 min)
- **Trend Following**: Swing trades
- **Safe**: Conservative trading

### 3. Select Strategy
- **Combined**: Best for most traders (uses all indicators)
- **EMA Crossover**: Trend-based
- **RSI Filter**: Momentum-based
- **Volume Confirmation**: Breakout-based

### 4. View Analysis
- See real-time candlestick chart
- Check technical indicators (RSI, MACD, Volume)
- Get trading signals with confidence scores

### 5. Check Portfolio
- Monitor open positions
- Track P&L
- View win rate

### 6. Backtest Strategies
- Click "Run Backtest" to test on historical data
- See win rate, ROI, drawdown
- Compare different strategies

## 📊 Understanding the Dashboard

### Market Metrics Section
- **Current Price**: Live market price
- **24h Change**: Price movement
- **High/Low**: Daily range
- **Volume**: Trading volume

### Chart Section
- Blue/Orange lines = EMA (short/long term)
- Red dashed line = EMA 200 (trend)
- Candlesticks = OHLC price action

### Indicators Section
- **RSI**: Overbought (>70) / Oversold (<30)
- **MACD**: Momentum and trend
- **Volume**: Strength of price moves

### Trading Signals
- **BUY (Green)**: Consider going long
- **SELL (Red)**: Consider going short
- **HOLD (Yellow)**: Wait for clearer signal
- **Confidence %**: How reliable the signal is

## 🎓 Example Scenarios

### Scenario 1: Finding a Buy Signal
1. Switch to NORMAL mode
2. Select COMBINED strategy
3. Look for green "BUY" signal
4. Check confidence score (should be >60%)
5. Verify EMA 9 above EMA 26
6. Confirm RSI not overbought

### Scenario 2: Backtesting a Strategy
1. Go to Backtest tab
2. Click "Run Backtest"
3. Wait for results
4. Check:
   - Win Rate (should be >50%)
   - ROI (expected return)
   - Max Drawdown (risk level)

### Scenario 3: Managing Positions
1. Go to Portfolio tab
2. See your open positions
3. Track current P&L
4. Wait for take profit or stop loss
5. Or manually close position

## ⚙️ Configuration

### Important Settings (in `config.py`)
```python
# Capital
INITIAL_CAPITAL = 10000

# Risk Management
DAILY_LOSS_LIMIT = 0.05  # 5% max daily loss
MAX_TRADES_PER_DAY = 10

# Position Size
MAX_POSITION_SIZE = 0.02  # 2% per trade
```

### API Setup (Optional)

**For Real Trading (Not recommended for beginners):**
1. Create Binance account
2. Generate API keys
3. Add to `config.py`:
```python
BINANCE_API_KEY = "your_key"
BINANCE_API_SECRET = "your_secret"
REAL_TRADING = True  # Only after testing!
```

**For Telegram Alerts:**
1. Create Telegram bot (@BotFather)
2. Get Chat ID (@userinfobot)
3. Add to `config.py`:
```python
TELEGRAM_BOT_TOKEN = "your_token"
TELEGRAM_CHAT_ID = "your_chat_id"
TELEGRAM_ENABLED = True
```

## 🧪 Run Examples

Test the system without the UI:

```bash
# Example 1: Fetch data and calculate indicators
python examples/example1_basic_analysis.py

# Example 2: Generate trading signals
python examples/example2_strategies.py

# Example 3: Run backtest
python examples/example3_backtest.py

# Example 4: Manage positions
python examples/example4_portfolio.py
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No data available"
- Check internet connection
- Try different symbol or timeframe
- Binance may have rate limits (wait 1 minute)

### Issue: Dashboard not opening
- Check if running: `streamlit run app.py`
- Open browser to: `http://localhost:8501`
- Check if port 8501 is in use

### Issue: Signals not generating
- Need at least 26+ candles of data
- Check indicator parameters match your timeframe
- Verify data quality

## 📚 Learning Path

### Beginner (Day 1-3)
1. ✅ Install and run dashboard
2. ✅ Learn about candlesticks and OHLC
3. ✅ Understand basic signals (BUY/SELL/HOLD)
4. ✅ Run first backtest

### Intermediate (Week 1-2)
1. ✅ Understand EMA, RSI, MACD indicators
2. ✅ Learn about stop loss and take profit
3. ✅ Paper trade for a week
4. ✅ Analyze backtest results

### Advanced (Month 1-2)
1. ✅ Optimize strategy parameters
2. ✅ Test multiple strategies
3. ✅ Understand risk management
4. ✅ Build custom strategies

## ✅ Pre-Trading Checklist

Before making real trades:
- [ ] Paper traded for at least 1 week
- [ ] Backtested strategy successfully
- [ ] Understand win rate expectations
- [ ] Set stop loss on every trade
- [ ] Never risk more than 2% per trade
- [ ] Have emergency exit plan
- [ ] Monitor trades regularly

## 🚨 Golden Rules

1. **Always use stop loss** - Never trade without it
2. **Risk management** - Never risk more than you can afford to lose
3. **Paper trade first** - Practice before real money
4. **Start small** - Begin with minimum capital
5. **Follow your system** - Don't deviate from strategy
6. **Keep records** - Log all trades
7. **Take breaks** - Trading is mentally taxing

## 📞 Getting Help

1. Check README.md for detailed documentation
2. Review code comments for explanations
3. Run examples to see how it works
4. Check troubleshooting section
5. Review strategy logic in source code

## 🎉 Next Steps

1. Familiarize yourself with the dashboard
2. Test different symbols and timeframes
3. Run backtests to validate strategies
4. Read more about technical analysis
5. Start paper trading
6. Gradually increase capital as you improve
7. Keep learning and refining your approach

---

**Remember: Trading is risky. Start small, learn continuously, and never risk more than you can afford to lose.**

**Happy Trading! 📈**
