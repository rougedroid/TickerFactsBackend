import asyncio
import json
from contextlib import suppress

import websockets
from websockets.asyncio.client import ClientConnection

from app.core.config import settings
from app.core.logging import logger
from app.realtime.broadcaster import broadcaster
from app.realtime.subscription_manager import subscription_manager


class FinnhubClient:
    def __init__(self) -> None:
        self._ws: ClientConnection | None = None

        self._listener_task: asyncio.Task | None = None
        self._reconnect_task: asyncio.Task | None = None

        self._subscriptions: set[str] = set()

        subscription_manager.register_subscribe_callback(
            self.subscribe_symbol
        )

        subscription_manager.register_unsubscribe_callback(
            self.unsubscribe_symbol
        )

    async def start(self) -> None:
        if self._reconnect_task is not None:
            return

        self._reconnect_task = asyncio.create_task(
            self._connection_loop()
        )

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
        reconnect_delay = 1

        while True:
            try:
                logger.info("Connecting to Finnhub websocket...")

                await self._connect()

                logger.info("Connected successfully.")

                reconnect_delay = 1

                self._listener_task = asyncio.create_task(
                    self._listen()
                )

                await self._listener_task

            except asyncio.CancelledError:
                raise

            except Exception:
                logger.exception(
                    "Websocket connection lost. Reconnecting..."
                )

            finally:
                self._listener_task = None

                if self._ws:
                    with suppress(Exception):
                        await self._ws.close()

                self._ws = None

            await asyncio.sleep(reconnect_delay)

            reconnect_delay = min(reconnect_delay * 2, 30)

    async def _connect(self) -> None:
        self._ws = await websockets.connect(
            "wss://socket.massive.com/stocks"
        )

        if self._ws is None:
            raise RuntimeError("Failed to connect.")

        await self._ws.send(
            json.dumps(
                {
                    "action": "auth",
                    "params": settings.FINNHUB_API_KEY,
                }
            )
        )

        authenticated = False

        while True:
            raw_message = await self._ws.recv()

            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                continue

            if not isinstance(payload, list):
                continue

            for event in payload:
                if event.get("ev") != "status":
                    continue

                status = event.get("status")

                if status == "auth_success":
                    authenticated = True
                    logger.info("Authenticated with Polygon.")
                    break

                if status == "auth_failed":
                    raise RuntimeError("Polygon authentication failed.")

            if authenticated:
                break

        for symbol in self._subscriptions:
            await self._send_subscribe(symbol)

    async def _listen(self) -> None:
        """
        Listen for incoming Polygon trade messages and
        publish them to Redis.
        """

        logger.info("Listening for Polygon messages...")

        if self._ws is None:
            raise RuntimeError("Websocket not connected.")

        async for message in self._ws:

            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                continue

            if not isinstance(payload, list):
                continue

            for event in payload:

                event_type = event.get("ev")

                if event_type == "status":
                    logger.debug(
                        f"Polygon status: {event}"
                    )
                    continue

                if event_type != "T":
                    continue

                symbol = event.get("sym")
                price = event.get("p")
                volume = event.get("s")
                timestamp = event.get("t")

                if None in (
                    symbol,
                    price,
                    volume,
                    timestamp,
                ):
                    continue

                try:
                    await broadcaster.publish_price(
                        symbol=symbol,
                        price=price,
                        volume=volume,
                        timestamp=timestamp,
                    )

                except Exception:
                    logger.exception(
                        "Failed to publish trade update."
                    )
                    
    async def subscribe_symbol(self, symbol: str) -> None:
        """
        Subscribe to a symbol.

        Called when the first frontend client subscribes.
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
        Unsubscribe from a symbol.

        Called when the last frontend client unsubscribes.
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
        Send a subscribe request to Polygon.
        """

        if self._ws is None:
            return

        logger.info(f"Actually subscribing to symbol: {symbol}")

        try:
            await self._ws.send(
                json.dumps(
                    {
                        "action": "subscribe",
                        "params": f"T.{symbol}",
                    }
                )
            )

        except Exception:
            logger.exception(
                f"Failed to subscribe to {symbol}"
            )

    async def _send_unsubscribe(self, symbol: str) -> None:
        """
        Send an unsubscribe request to Polygon.
        """

        if self._ws is None:
            return

        logger.info(f"Actually unsubscribing from symbol: {symbol}")

        try:
            await self._ws.send(
                json.dumps(
                    {
                        "action": "unsubscribe",
                        "params": f"T.{symbol}",
                    }
                )
            )

        except Exception:
            logger.exception(
                f"Failed to unsubscribe from {symbol}"
            )


finnhub_client = FinnhubClient()