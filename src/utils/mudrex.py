"""
Mudrex API integration client
"""

import json
import logging
from typing import Dict, Optional

import requests

logger = logging.getLogger(__name__)


class MudrexClient:
    """Simple Mudrex API client for order placement and status checks."""

    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        base_url: str = "https://trade.mudrex.com/fapi/v1"
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.enabled = bool(api_secret)  # Only api_secret is required

    def configure(
        self,
        api_key: str,
        api_secret: str,
        base_url: Optional[str] = None
    ):
        """Configure Mudrex credentials."""
        self.api_key = api_key
        self.api_secret = api_secret
        if base_url:
            self.base_url = base_url.rstrip("/")
        self.enabled = bool(api_secret)  # Only api_secret required
        logger.info("Mudrex client configured")

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
        }
        if self.api_secret:
            headers["X-Authentication"] = self.api_secret
        return headers

    def test_connection(self) -> bool:
        """Test Mudrex API connectivity."""
        if not self.enabled:
            return False

        url = f"{self.base_url}/assets"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            if response.status_code == 200:
                logger.info("Mudrex connection successful")
                return True

            logger.error("Mudrex test connection failed: %s", response.text)
            return False
        except Exception as exc:
            logger.error("Mudrex connection error: %s", exc)
            return False

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "market",
        price: Optional[float] = None,
        time_in_force: str = "GTC",
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
    ) -> Optional[Dict]:
        """Place an order through the Mudrex API."""
        if not self.enabled:
            logger.warning("Mudrex API not configured")
            return None

        payload = {
            "symbol": symbol,
            "side": side.lower(),
            "type": order_type.lower(),
            "quantity": quantity,
            "time_in_force": time_in_force,
        }

        if price is not None:
            payload["price"] = price
        if stop_loss is not None:
            payload["stop_loss"] = stop_loss
        if take_profit is not None:
            payload["take_profit"] = take_profit

        url = f"{self.base_url}/orders"
        try:
            response = requests.post(url, headers=self._headers(), json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info("Mudrex order placed: %s", data)
            return data
        except Exception as exc:
            logger.error("Mudrex order placement failed: %s", exc)
            return None

    def get_open_orders(self) -> Optional[Dict]:
        """Fetch open orders from Mudrex - GET /futures/orders."""
        if not self.enabled:
            return None

        url = f"{self.base_url}/futures/orders"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
            logger.info("Mudrex open orders fetched")
            return response.json()
        except Exception as exc:
            logger.error("Mudrex fetch open orders failed: %s", exc)
            return None

    def get_order_history(self, limit: int = 50) -> Optional[Dict]:
        """Fetch order history from Mudrex - GET /futures/orders/history."""
        if not self.enabled:
            return None

        url = f"{self.base_url}/futures/orders/history?limit={limit}"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
            logger.info("Mudrex order history fetched")
            return response.json()
        except Exception as exc:
            logger.error("Mudrex fetch order history failed: %s", exc)
            return None

    def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """Fetch a single order detail from Mudrex - GET /futures/orders/{order_id}."""
        if not self.enabled:
            return None

        url = f"{self.base_url}/futures/orders/{order_id}"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
            logger.info("Mudrex order details fetched for order: %s", order_id)
            return response.json()
        except Exception as exc:
            logger.error("Mudrex fetch order by ID failed: %s", exc)
            return None

    def get_open_positions(self) -> Optional[Dict]:
        """Fetch open positions from Mudrex - GET /futures/positions."""
        if not self.enabled:
            return None

        url = f"{self.base_url}/futures/positions"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info("Mudrex open positions fetched: %s", data)
            return data
        except Exception as exc:
            logger.error("Mudrex fetch open positions failed: %s", exc)
            return None

    def get_position_history(self, limit: int = 50) -> Optional[Dict]:
        """Fetch position history from Mudrex - GET /futures/positions/history."""
        if not self.enabled:
            return None

        url = f"{self.base_url}/futures/positions/history?limit={limit}"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info("Mudrex position history fetched: %s", data)
            return data
        except Exception as exc:
            logger.error("Mudrex fetch position history failed: %s", exc)
            return None

    def get_wallet_balance(self) -> Optional[Dict]:
        """Fetch spot wallet balance from Mudrex - GET /wallet/funds."""
        if not self.enabled:
            return None

        url = f"{self.base_url}/wallet/funds"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
            logger.info("Mudrex wallet balance fetched")
            return response.json()
        except Exception as exc:
            logger.error("Mudrex fetch wallet balance failed: %s", exc)
            return None

    def get_futures_balance(self) -> Optional[Dict]:
        """Fetch futures wallet balance from Mudrex - GET /futures/funds."""
        if not self.enabled:
            return None

        url = f"{self.base_url}/futures/funds"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
            logger.info("Mudrex futures balance fetched")
            return response.json()
        except Exception as exc:
            logger.error("Mudrex fetch futures balance failed: %s", exc)
            return None

    def get_fee_history(self) -> Optional[Dict]:
        """Fetch trading fee history from Mudrex - GET /futures/fee/history."""
        if not self.enabled:
            return None

        url = f"{self.base_url}/futures/fee/history"
        try:
            response = requests.get(url, headers=self._headers(), timeout=10)
            response.raise_for_status()
            logger.info("Mudrex fee history fetched")
            return response.json()
        except Exception as exc:
            logger.error("Mudrex fetch fee history failed: %s", exc)
            return None
