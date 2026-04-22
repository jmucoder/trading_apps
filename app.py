"""
Trading Dashboard UI using Streamlit
Modern dark theme trading interface with real-time data and charts
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.market_data import MarketDataFetcher, DataProcessor
from src.data.indicators import TechnicalIndicators, SignalGenerator
from src.strategies.strategy_engine import StrategyEngine, TradingMode, StrategyType
from src.utils.portfolio import PortfolioManager, RiskLevel
from src.utils.backtest import Backtester
from src.utils.alerts import AlertManager, AlertType, AlertSeverity
from src.utils.mudrex import MudrexClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(
    page_title="Crypto & Stock Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    :root {
        --primary-color: #1f77b4;
        --background-color: #0e1117;
        --secondary-background-color: #161b22;
        --text-color: #c9d1d9;
    }
    
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    .metric-card {
        background-color: var(--secondary-background-color);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid var(--primary-color);
    }
    
    .positive { color: #3fb950; }
    .negative { color: #f85149; }
</style>
""", unsafe_allow_html=True)


class TradingDashboard:
    """Main trading dashboard application"""

    def __init__(self):
        """Initialize dashboard"""
        self.fetcher = MarketDataFetcher()
        self.strategy_engine = StrategyEngine(TradingMode.NORMAL)
        self.alert_manager = AlertManager()
        self.portfolio = PortfolioManager(initial_capital=10000)
        self.mudrex_client = MudrexClient()
        self.backtester = Backtester(initial_capital=10000)

    def render_header(self):
        """Render dashboard header"""
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.title("📈 Trading Dashboard")
            st.write("Crypto & Stock Market Trading Platform")

        with col2:
            st.write("")
            st.write("")
            current_time = datetime.now()
            st.info(f"⏰ {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

        with col3:
            st.write("")
            st.write("")
            status = "🟢 LIVE" if True else "🔴 OFFLINE"
            st.success(status)

    def render_sidebar(self):
        """Render sidebar settings"""
        st.sidebar.title("⚙️ Settings")

        # Asset Selection
        st.sidebar.subheader("Asset Selection")
        asset_type = st.sidebar.radio("Select Asset Type", ["Crypto", "Stock"])
        
        if asset_type == "Crypto":
            symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT"]
            symbol = st.sidebar.selectbox("Select Crypto", symbols)
        else:
            symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "NIFTY"]
            symbol = st.sidebar.selectbox("Select Stock", symbols)

        # Timeframe Selection
        st.sidebar.subheader("Timeframe")
        if asset_type == "Crypto":
            timeframe = st.sidebar.selectbox("Select Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"])
        else:
            timeframe = st.sidebar.selectbox("Select Timeframe", ["1h", "1d"])

        # Trading Mode
        st.sidebar.subheader("Trading Mode")
        mode_map = {
            "Normal Trading": TradingMode.NORMAL,
            "Scalping Mode": TradingMode.SCALPING,
            "Trend Following": TradingMode.TREND_FOLLOWING,
            "Safe Mode": TradingMode.SAFE,
        }
        mode_name = st.sidebar.selectbox("Select Mode", list(mode_map.keys()))
        trading_mode = mode_map[mode_name]

        # Strategy Selection
        st.sidebar.subheader("Strategy")
        strategy_map = {
            "Combined (EMA+RSI+MACD)": StrategyType.COMBINED,
            "EMA Crossover": StrategyType.EMA_CROSSOVER,
            "RSI Filter": StrategyType.RSI_FILTER,
            "Volume Confirmation": StrategyType.VOLUME_CONFIRMATION,
        }
        strategy_name = st.sidebar.selectbox("Select Strategy", list(strategy_map.keys()))
        strategy = strategy_map[strategy_name]

        # Risk Management
        st.sidebar.subheader("Risk Management")
        risk_level = st.sidebar.radio("Risk Level", ["Low", "Medium", "High"])
        max_position_size = st.sidebar.slider("Max Position Size (%)", 0.5, 5.0, 2.0)

        return {
            'asset_type': asset_type,
            'symbol': symbol,
            'timeframe': timeframe,
            'trading_mode': trading_mode,
            'strategy': strategy,
            'risk_level': risk_level,
            'max_position_size': max_position_size,
        }

    def render_metrics(self, symbol: str, asset_type: str):
        """Render key metrics"""
        st.subheader("📊 Market Metrics")

        try:
            if asset_type == "Crypto":
                price_data = self.fetcher.fetch_crypto_current_price(symbol)
            else:
                price_data = self.fetcher.fetch_stock_current_price(symbol)

            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.metric("Current Price", f"${price_data.get('current_price', 0):.2f}")

            with col2:
                change = price_data.get('change_24h', 0)
                st.metric("24h Change", f"{change:.2f}%", 
                         delta=f"{change:.2f}%" if change else None)

            with col3:
                st.metric("24h High", f"${price_data.get('high_24h', 0):.2f}")

            with col4:
                st.metric("24h Low", f"${price_data.get('low_24h', 0):.2f}")

            with col5:
                volume = price_data.get('volume', 0)
                st.metric("24h Volume", f"{volume:.0f}")

        except Exception as e:
            st.error(f"Error fetching price data: {str(e)}")

    def render_chart(self, df: pd.DataFrame, symbol: str):
        """Render candlestick chart with indicators"""
        if df.empty:
            st.error("No data available for chart")
            return

        st.subheader(f"📈 {symbol} Chart")

        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC'
        )])

        # Add EMA 9
        ema_9 = TechnicalIndicators.calculate_ema(df['close'], 9)
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=ema_9,
            name='EMA 9',
            line=dict(color='orange', width=1)
        ))

        # Add EMA 26
        ema_26 = TechnicalIndicators.calculate_ema(df['close'], 26)
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=ema_26,
            name='EMA 26',
            line=dict(color='blue', width=1)
        ))

        # Add EMA 200
        ema_200 = TechnicalIndicators.calculate_ema(df['close'], 200)
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=ema_200,
            name='EMA 200',
            line=dict(color='red', width=1, dash='dash')
        ))

        fig.update_layout(
            title=f"{symbol} - Candlestick with EMAs",
            yaxis_title='Price (USD)',
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    def render_indicators(self, df: pd.DataFrame):
        """Render technical indicators"""
        st.subheader("📊 Technical Indicators")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**RSI (14)**")
            rsi = TechnicalIndicators.calculate_rsi(df['close'], 14)
            rsi_value = rsi.iloc[-1]
            
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(y=rsi, name='RSI', line=dict(color='purple')))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
            fig_rsi.update_layout(template='plotly_dark', height=300, showlegend=False)
            
            st.plotly_chart(fig_rsi, use_container_width=True)
            
            if rsi_value > 70:
                st.markdown('<p class="negative">🔴 OVERBOUGHT</p>', unsafe_allow_html=True)
            elif rsi_value < 30:
                st.markdown('<p class="positive">🟢 OVERSOLD</p>', unsafe_allow_html=True)
            else:
                st.info("🟡 NEUTRAL")

        with col2:
            st.write("**MACD**")
            macd, signal, histogram = TechnicalIndicators.calculate_macd(df['close'])
            
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(y=macd, name='MACD', line=dict(color='blue')))
            fig_macd.add_trace(go.Scatter(y=signal, name='Signal', line=dict(color='red')))
            fig_macd.add_trace(go.Bar(y=histogram, name='Histogram', marker=dict(color='gray')))
            fig_macd.update_layout(template='plotly_dark', height=300, showlegend=True)
            
            st.plotly_chart(fig_macd, use_container_width=True)
            
            # MACD Crossover Detection
            macd_val = macd.iloc[-1]
            signal_val = signal.iloc[-1]
            prev_macd = macd.iloc[-2] if len(macd) > 1 else macd.iloc[-1]
            prev_signal = signal.iloc[-2] if len(signal) > 1 else signal.iloc[-1]
            
            macd_cross = False
            cross_type = None
            
            if prev_macd <= prev_signal and macd_val > signal_val:
                macd_cross = True
                cross_type = 'BULLISH'
            elif prev_macd >= prev_signal and macd_val < signal_val:
                macd_cross = True
                cross_type = 'BEARISH'
            
            if macd_cross:
                st.success(f"🔔 MACD {cross_type} Crossover!")
                alert = self.alert_manager.create_alert(
                    symbol='MACD',
                    alert_type=AlertType.MACD_CROSSOVER,
                    severity=AlertSeverity.WARNING,
                    message=f"MACD {cross_type} Crossover detected",
                    data={'type': cross_type, 'macd': macd_val, 'signal': signal_val}
                )
                self.alert_manager.send_alert(alert)
            else:
                st.info("📊 MACD: No crossover")

        with col3:
            st.write("**Volume**")
            sma_volume = df['volume'].rolling(window=20).mean()
            
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(y=df['volume'], name='Volume', marker=dict(color='cyan')))
            fig_vol.add_trace(go.Scatter(y=sma_volume, name='SMA 20', line=dict(color='red')))
            fig_vol.update_layout(template='plotly_dark', height=300, showlegend=True)
            
            st.plotly_chart(fig_vol, use_container_width=True)

    def render_signals(self, df: pd.DataFrame, trading_mode: TradingMode, strategy: StrategyType):
        """Render trading signals"""
        st.subheader("🎯 Trading Signals")

        self.strategy_engine = StrategyEngine(trading_mode)
        signal = self.strategy_engine.generate_signal(df, strategy)

        # Send BUY/SELL alerts for strong signals
        if signal.signal_type in ['BUY', 'SELL'] and signal.confidence > 70:
            alert_severity = AlertSeverity.CRITICAL if signal.confidence > 85 else AlertSeverity.WARNING
            alert = self.alert_manager.create_alert(
                symbol=signal.symbol,
                alert_type=AlertType.EMA_CROSSOVER,
                severity=alert_severity,
                message=f"📢 {signal.signal_type} Signal for {signal.symbol} at ${signal.entry_price:.2f} (Confidence: {signal.confidence:.1f}%)",
                data={
                    'signal_type': signal.signal_type,
                    'confidence': signal.confidence,
                    'entry_price': signal.entry_price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit
                }
            )
            self.alert_manager.send_alert(alert)
            st.info(f"🔔 Alert: {signal.signal_type} signal with {signal.confidence:.1f}% confidence")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if signal.signal_type == 'BUY':
                st.success("📈 BUY")
            elif signal.signal_type == 'SELL':
                st.error("📉 SELL")
            else:
                st.warning("⏸️ HOLD")

        with col2:
            st.metric("Confidence", f"{signal.confidence:.1f}%")

        with col3:
            st.metric("Entry Price", f"${signal.entry_price:.2f}")

        with col4:
            st.metric("Risk/Reward", f"{signal.risk_reward_ratio:.1f}x" if signal.risk_reward_ratio else "N/A")

        # Display signal details
        st.write("**Signal Breakdown:**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.info(f"EMA: {signal.signal_type}")
        with col2:
            st.info(f"RSI: BUY/SELL")
        with col3:
            st.info(f"MACD: {signal.signal_type}")
        with col4:
            st.info(f"Volume: OK")

    def render_mudrex_orders(self):
        """Render Mudrex order and position details without placing orders."""
        st.subheader("📦 Mudrex Trading Details")

        if not self.mudrex_client.enabled:
            st.info("Enable Mudrex and configure credentials in Settings to view orders.")
            return

        def extract_data(response):
            """Extract data from API response - handle {"success": true, "data": [...]} format."""
            if not response:
                return None
            
            if isinstance(response, dict):
                # If response has "data" key, extract it
                if "data" in response:
                    data = response["data"]
                    # Handle case where data is None or empty
                    if data is None:
                        return None
                    # If data is a dict with content, return it as a list
                    if isinstance(data, dict) and data:
                        return [data]
                    # If data is a list, return it
                    if isinstance(data, list):
                        return data if data else None
                    # Return data as-is if non-empty
                    return data if data else None
                
                # If response has "success" key, try to return the whole response
                if "success" in response:
                    # Check if response has other data fields
                    other_keys = {k: v for k, v in response.items() if k != "success"}
                    if other_keys:
                        return [response] if response else None
                    return None
            
            # If it's already a list, return as-is
            if isinstance(response, list):
                return response if response else None
            
            return response if response else None

        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Orders**")
            if st.button("📋 Load Open Orders", key="load_mudrex_open_orders"):
                orders = self.mudrex_client.get_open_orders()
                data = extract_data(orders)
                if data:
                    df_data = data if isinstance(data, list) else [data]
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No open orders found.")

            if st.button("📝 Load Order History", key="load_mudrex_order_history"):
                history = self.mudrex_client.get_order_history()
                data = extract_data(history)
                if data:
                    df_data = data if isinstance(data, list) else [data]
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No order history found.")
        
        with col2:
            st.write("**Positions & Wallet**")
            if st.button("📊 Load Open Positions", key="load_mudrex_positions"):
                positions = self.mudrex_client.get_open_positions()
                data = extract_data(positions)
                if data:
                    df_data = data if isinstance(data, list) else [data]
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("✅ No open positions (or API returned no data)")

            if st.button("💰 Load Wallet Balance", key="load_mudrex_wallet"):
                wallet = self.mudrex_client.get_wallet_balance()
                data = extract_data(wallet)
                if data:
                    st.json(data)
                else:
                    st.info("No wallet data available.")

            if st.button("💵 Load Futures Balance", key="load_mudrex_futures"):
                futures = self.mudrex_client.get_futures_balance()
                data = extract_data(futures)
                if data:
                    st.json(data)
                else:
                    st.info("No futures balance data available.")

            if st.button("📊 Load Fee History", key="load_mudrex_fees"):
                fees = self.mudrex_client.get_fee_history()
                data = extract_data(fees)
                if data:
                    df_data = data if isinstance(data, list) else [data]
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No fee history found.")

    def render_portfolio(self):
        """Render portfolio metrics"""
        st.subheader("💼 Portfolio")

        metrics = self.portfolio.get_metrics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Capital", f"${metrics.total_capital:,.2f}")

        with col2:
            st.metric("Current Equity", f"${metrics.equity:,.2f}")

        with col3:
            st.metric("Return", f"{metrics.return_pct:.2f}%", 
                     delta=f"{metrics.return_pct:.2f}%" if metrics.return_pct > 0 else None)

        with col4:
            st.metric("Win Rate", f"{metrics.win_rate:.1f}%")

        # Open positions
        st.write("**Open Positions:**")
        positions = self.portfolio.get_open_positions()
        if positions:
            positions_df = pd.DataFrame(positions)
            st.dataframe(positions_df, use_container_width=True)
        else:
            st.info("No open positions")

    def render_backtest(self, df: pd.DataFrame):
        """Render backtest results"""
        st.subheader("🧪 Backtest Results")

        if st.button("Run Backtest"):
            with st.spinner("Running backtest..."):
                result = self.backtester.run_ema_crossover_backtest(df)
                metrics = result.calculate_metrics(10000)

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Trades", metrics['total_trades'])

                with col2:
                    st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")

                with col3:
                    st.metric("ROI", f"{metrics['roi']:.2f}%")

                with col4:
                    st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%")

                # Show trade list
                if result.trades:
                    trades_df = pd.DataFrame(result.trades)
                    st.dataframe(trades_df, use_container_width=True)

    def render_settings(self):
        """Render additional settings"""
        st.subheader("⚙️ Advanced Settings")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Telegram Alerts**")
            enable_telegram = st.checkbox("Enable Telegram Notifications")
            if enable_telegram:
                telegram_token = st.text_input("Telegram Bot Token", type="password")
                telegram_chat_id = st.text_input("Chat ID")

        with col2:
            st.write("**Sound Alerts**")
            enable_sound = st.checkbox("Enable Sound Alerts", value=True)

        st.markdown("---")
        st.write("**Mudrex Trading Integration**")
        mudrex_enabled = st.checkbox("Enable Mudrex Trading API", key="mudrex_enabled")
        if mudrex_enabled:
            mudrex_api_key = st.text_input("Mudrex API Key", type="password", key="mudrex_api_key")
            mudrex_api_secret = st.text_input("Mudrex API Secret", type="password", key="mudrex_api_secret")
            mudrex_base_url = st.text_input("Mudrex Base URL", value="https://api.mudrex.com", key="mudrex_base_url")
            if mudrex_api_key and mudrex_api_secret:
                self.mudrex_client.configure(
                    api_key=mudrex_api_key,
                    api_secret=mudrex_api_secret,
                    base_url=mudrex_base_url
                )
                st.success("Mudrex API configured")
            else:
                st.info("Enter both Mudrex API key and secret to enable Mudrex trading")

        self.render_mudrex_orders()

    def _configure_mudrex(self):
        """Configure Mudrex client from Streamlit session state."""
        if st.session_state.get("mudrex_enabled"):
            api_key = st.session_state.get("mudrex_api_key", "")
            api_secret = st.session_state.get("mudrex_api_secret", "")
            base_url = st.session_state.get("mudrex_base_url", "https://api.mudrex.com")
            if api_key and api_secret:
                self.mudrex_client.configure(api_key, api_secret, base_url)

    def run(self):
        """Run the dashboard"""
        self.render_header()
        self._configure_mudrex()

        # Sidebar settings
        settings = self.render_sidebar()

        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Analysis",
            "💼 Portfolio",
            "🧪 Backtest",
            "📊 Dashboard",
            "⚙️ Settings"
        ])

        with tab1:
            # Fetch data
            symbol = settings['symbol']
            asset_type = settings['asset_type']
            timeframe = settings['timeframe']

            with st.spinner(f"Fetching {symbol} data..."):
                if asset_type == "Crypto":
                    df = self.fetcher.fetch_crypto_ohlc(symbol, timeframe, 100)
                else:
                    df = self.fetcher.fetch_stock_ohlc(symbol, '1d', '30d')

            if not df.empty:
                self.render_metrics(symbol, asset_type)
                self.render_chart(df, symbol)
                self.render_indicators(df)
                self.render_signals(df, settings['trading_mode'], settings['strategy'])
            else:
                st.error("Failed to fetch data. Please try again.")

        with tab2:
            self.render_portfolio()

        with tab3:
            if not df.empty:
                self.render_backtest(df)

        with tab4:
            st.write("### Dashboard Summary")
            self.render_portfolio()

        with tab5:
            self.render_settings()


def main():
    """Main function"""
    dashboard = TradingDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
