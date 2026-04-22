"""
Alerts and Notifications System
Push notifications, sound alerts, Telegram integration
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import requests

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of alerts"""
    EMA_CROSSOVER = "ema_crossover"
    RSI_LEVEL = "rsi_level"
    MACD_CROSSOVER = "macd_crossover"
    BREAKOUT = "breakout"
    TARGET_HIT = "target_hit"
    STOP_LOSS_HIT = "stop_loss_hit"
    VOLUME_SPIKE = "volume_spike"
    TREND_CHANGE = "trend_change"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertManager:
    """
    Manage and send trading alerts
    Supports multiple channels: Desktop, Sound, Telegram, Email
    """

    def __init__(self):
        """Initialize alert manager"""
        self.alerts: List[Dict] = []
        self.alert_history: List[Dict] = []
        self.telegram_enabled = False
        self.telegram_token = None
        self.telegram_chat_id = None
        self.sound_enabled = True

    def configure_telegram(self, token: str, chat_id: str):
        """
        Configure Telegram alerts
        
        Args:
            token: Telegram bot token
            chat_id: Chat ID to send alerts to
        """
        self.telegram_enabled = True
        self.telegram_token = token
        self.telegram_chat_id = chat_id
        logger.info("Telegram alerts configured")

    def create_alert(
        self,
        symbol: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Create an alert
        
        Args:
            symbol: Trading symbol
            alert_type: Type of alert
            severity: Alert severity
            message: Alert message
            data: Additional data
        
        Returns:
            Alert dictionary
        """
        alert = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'type': alert_type.value,
            'severity': severity.value,
            'message': message,
            'data': data or {},
            'sent': False,
        }

        self.alerts.append(alert)
        return alert

    def send_alert(self, alert: Dict) -> bool:
        """
        Send alert through all configured channels
        
        Args:
            alert: Alert dictionary
        
        Returns:
            True if sent successfully
        """
        try:
            # Log alert
            logger.warning(f"ALERT [{alert['severity']}]: {alert['message']}")

            # Send via Telegram if configured
            if self.telegram_enabled:
                self._send_telegram(alert)

            # Play sound for critical alerts
            if alert['severity'] == AlertSeverity.CRITICAL.value and self.sound_enabled:
                self._play_sound()

            alert['sent'] = True
            self.alert_history.append(alert)
            return True

        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")
            return False

    def _send_telegram(self, alert: Dict):
        """Send alert via Telegram"""
        try:
            if not self.telegram_enabled:
                return

            # Format message
            emoji_map = {
                'info': '📢',
                'warning': '⚠️',
                'critical': '🚨',
            }
            emoji = emoji_map.get(alert['severity'], '📢')

            message = f"{emoji} *{alert['symbol']}* - {alert['type'].upper()}\n"
            message += f"*Message:* {alert['message']}\n"
            message += f"*Time:* {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"

            if alert['data']:
                message += "\n*Details:*\n"
                for key, value in alert['data'].items():
                    message += f"• {key}: {value}\n"

            # Send to Telegram
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, data=data, timeout=5)
            if response.status_code == 200:
                logger.info("Alert sent via Telegram")
            else:
                logger.error(f"Telegram error: {response.text}")

        except Exception as e:
            logger.error(f"Error sending Telegram: {str(e)}")

    def _play_sound(self):
        """Play sound alert"""
        try:
            # Try to play sound (cross-platform)
            import sys
            if sys.platform == 'win32':
                import winsound
                winsound.Beep(1000, 500)  # Frequency, Duration
            elif sys.platform == 'darwin':
                import os
                os.system('afplay /System/Library/Sounds/Alarm.aiff')
            else:
                import os
                os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga')

        except Exception as e:
            logger.error(f"Error playing sound: {str(e)}")

    def create_ema_crossover_alert(
        self,
        symbol: str,
        signal_type: str,  # 'BUY' or 'SELL'
        price: float,
        fast_ema: float,
        slow_ema: float
    ):
        """Create EMA crossover alert"""
        severity = AlertSeverity.WARNING
        message = f"EMA Crossover: {signal_type} signal for {symbol} at ${price:.2f}"

        alert = self.create_alert(
            symbol=symbol,
            alert_type=AlertType.EMA_CROSSOVER,
            severity=severity,
            message=message,
            data={
                'signal': signal_type,
                'price': price,
                'fast_ema': fast_ema,
                'slow_ema': slow_ema,
            }
        )

        self.send_alert(alert)

    def create_rsi_alert(
        self,
        symbol: str,
        rsi_value: float,
        signal_type: str  # 'OVERBOUGHT', 'OVERSOLD', 'NEUTRAL'
    ):
        """Create RSI alert"""
        severity = AlertSeverity.WARNING
        message = f"RSI Alert: {signal_type} condition for {symbol} (RSI: {rsi_value:.2f})"

        alert = self.create_alert(
            symbol=symbol,
            alert_type=AlertType.RSI_LEVEL,
            severity=severity,
            message=message,
            data={
                'rsi': rsi_value,
                'condition': signal_type,
            }
        )

        self.send_alert(alert)

    def create_target_alert(
        self,
        symbol: str,
        current_price: float,
        target_price: float,
        pnl_pct: float
    ):
        """Create take profit alert"""
        severity = AlertSeverity.CRITICAL
        message = f"Target Hit! {symbol} reached ${current_price:.2f} (+{pnl_pct:.2f}%)"

        alert = self.create_alert(
            symbol=symbol,
            alert_type=AlertType.TARGET_HIT,
            severity=severity,
            message=message,
            data={
                'current_price': current_price,
                'target_price': target_price,
                'pnl_pct': pnl_pct,
            }
        )

        self.send_alert(alert)

    def create_stop_loss_alert(
        self,
        symbol: str,
        current_price: float,
        stop_loss: float,
        pnl_pct: float
    ):
        """Create stop loss alert"""
        severity = AlertSeverity.CRITICAL
        message = f"Stop Loss Hit! {symbol} fell to ${current_price:.2f} ({pnl_pct:.2f}%)"

        alert = self.create_alert(
            symbol=symbol,
            alert_type=AlertType.STOP_LOSS_HIT,
            severity=severity,
            message=message,
            data={
                'current_price': current_price,
                'stop_loss': stop_loss,
                'pnl_pct': pnl_pct,
            }
        )

        self.send_alert(alert)

    def create_volume_spike_alert(
        self,
        symbol: str,
        current_volume: float,
        avg_volume: float,
        volume_ratio: float
    ):
        """Create volume spike alert"""
        severity = AlertSeverity.WARNING
        message = f"Volume Spike! {symbol} volume increased by {volume_ratio:.1f}x"

        alert = self.create_alert(
            symbol=symbol,
            alert_type=AlertType.VOLUME_SPIKE,
            severity=severity,
            message=message,
            data={
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'ratio': volume_ratio,
            }
        )

        self.send_alert(alert)

    def create_breakout_alert(
        self,
        symbol: str,
        breakout_type: str,  # 'UPSIDE' or 'DOWNSIDE'
        price: float,
        resistance_level: float
    ):
        """Create breakout alert"""
        severity = AlertSeverity.WARNING
        message = f"{breakout_type} Breakout! {symbol} broke through ${resistance_level:.2f}"

        alert = self.create_alert(
            symbol=symbol,
            alert_type=AlertType.BREAKOUT,
            severity=severity,
            message=message,
            data={
                'breakout_type': breakout_type,
                'price': price,
                'level': resistance_level,
            }
        )

        self.send_alert(alert)

    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent alerts"""
        return self.alert_history[-limit:]

    def get_unset_alerts(self) -> List[Dict]:
        """Get unsent alerts"""
        return [a for a in self.alerts if not a['sent']]

    def clear_alerts(self):
        """Clear alerts"""
        self.alerts = []

    def export_alerts(self, filename: str):
        """Export alerts to JSON"""
        try:
            with open(filename, 'w') as f:
                alerts_data = [
                    {
                        **alert,
                        'timestamp': alert['timestamp'].isoformat()
                    }
                    for alert in self.alert_history
                ]
                json.dump(alerts_data, f, indent=2)
            logger.info(f"Alerts exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting alerts: {str(e)}")


if __name__ == "__main__":
    print("Alert Manager initialized successfully")
