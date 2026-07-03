import asyncio

import json
from contextlib import suppress
from app.core.logging import logger
import websockets
from websockets.asyncio.client import ClientConnection
from app.realtime.broadcaster import broadcaster
from app.core.config import settings

from app.realtime.subscription_manager import subscription_manager


class FinnhubClient:
    def __init__(self) -> None:
        self._ws: ClientConnection | None = None

        self._listener_task: asyncio.Task | None = None
        self._reconnect_task: asyncio.Task | None = None

        self._subscriptions: set[str] = set()

        subscription_manager.register_subscribe_callback(self.subscribe_symbol)

        subscription_manager.register_unsubscribe_callback(self.unsubscribe_symbol)

    async def start(self) -> None:
        if self._reconnect_task is not None:
            return

        self._reconnect_task = asyncio.create_task(self._connection_loop())

    async def stop(self) -> None:
        if self._reconnect_task:
            self._reconnect_task.cancel()

            with suppress(asyncio.CancelledError):
                await self._reconnect_task

        if self._listener_task:
            self._listener_task.cancel()

            with suppress(asyncio.CancelledError):
                await self._listener_task

        if self._ws:
            await self._ws.close()

    async def _connection_loop(self) -> None:
        while True:
            try:
                await self._connect()

                self._listener_task = asyncio.create_task(self._listen())

                await self._listener_task

            except Exception:
                await asyncio.sleep(5)

    async def _connect(self) -> None:
        self._ws = await websockets.connect(
            f"wss://ws.finnhub.io?token={settings.FINNHUB_API_KEY}"
        )

        for symbol in self._subscriptions:
            await self._send_subscribe(symbol)

    async def _listen(self) -> None:
        """
        Listen for incoming messages from Finnhub and publish price updates
        to Redis.

        Raises on websocket disconnect so the connection loop can reconnect.
        """
        logger.info("Listening for Finnhub messages...")
        if self._ws is None:
            raise RuntimeError("Finnhub websocket is not connected.")

        async for message in self._ws:
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                continue

            message_type = payload.get("type")

            # Trade updates
            if message_type == "trade":
                trades = payload.get("data", [])
                logger.info(f"Received {len(trades)} trades from Finnhub.")

                for trade in trades:
                    symbol = trade.get("s")
                    price = trade.get("p")
                    volume = trade.get("v")
                    timestamp = trade.get("t")

                    if (
                        symbol is None
                        or price is None
                        or volume is None
                        or timestamp is None
                    ):
                        continue
                    
                
                    await broadcaster.publish_price(
                        symbol=symbol,
                        price=price,
                        volume=volume,
                        timestamp=timestamp,
                    )

            # Finnhub ping message
            elif message_type == "ping":
                logger.info("Received ping from Finnhub, sending pong.")
                await self._ws.send(json.dumps({"type": "pong"}))
                continue
            else:
                logger.warning(f"Unknown message type from Finnhub: {message_type}")
                logger.warning(f"Message payload: {payload}")
                continue

            # Unknown messages are ignored for now.

    async def subscribe_symbol(self, symbol: str) -> None:
        """
        Subscribe to a symbol on Finnhub.

        This is called when the first client subscribes to a symbol.
        """
        logger.info(f"Subscribing symbol: {symbol}")
        symbol = symbol.upper()

        if symbol in self._subscriptions:
            return

        self._subscriptions.add(symbol)

        if self._ws is None:
            return

        await self._send_subscribe(symbol)

    async def unsubscribe_symbol(self, symbol: str) -> None:
        """
        Unsubscribe from a symbol on Finnhub.

        This is called when the last client unsubscribes.
        """

        symbol = symbol.upper()

        if symbol not in self._subscriptions:
            return

        self._subscriptions.remove(symbol)

        if self._ws is None:
            return

        await self._send_unsubscribe(symbol)

    async def _send_subscribe(self, symbol: str) -> None:
        """
        Send a subscribe message to Finnhub.
        """
        logger.info(f"Actually Subscribing symbol: {symbol}")

        if self._ws is None:
            return

        await self._ws.send(
            json.dumps(
                {
                    "type": "subscribe",
                    "symbol": symbol,
                }
            )
        )

    async def _send_unsubscribe(self, symbol: str) -> None:
        """
        Send an unsubscribe message to Finnhub.
        """

        if self._ws is None:
            return

        await self._ws.send(
            json.dumps(
                {
                    "type": "unsubscribe",
                    "symbol": symbol,
                }
            )
        )

finnhub_client = FinnhubClient()