from collections import defaultdict
from collections.abc import Callable
from collections.abc import Awaitable, Callable
import asyncio

class SubscriptionManager:
    """
    Maintains the relationship between ticker symbols and websocket
    connections.

    symbol -> connection_ids
    connection_id -> symbols
    """

    def __init__(self) -> None:
        self._symbol_connections: dict[str, set[str]] = defaultdict(set)
        self._connection_symbols: dict[str, set[str]] = defaultdict(set)
        self._subscribe_callbacks: list[Callable[[str], Awaitable[None]]] = []
        self._unsubscribe_callbacks: list[Callable[[str], Awaitable[None]]] = []

    def register_subscribe_callback(
    self,
    callback: Callable[[str], Awaitable[None]],
) -> None:
        self._subscribe_callbacks.append(callback)

    def register_unsubscribe_callback(
    self,
    callback: Callable[[str], Awaitable[None]],
) -> None:
        self._unsubscribe_callbacks.append(callback)

    def subscribe(
        self,
        connection_id: str,
        symbol: str,
    ) -> None:
        symbol = symbol.upper()

        first_subscriber = symbol not in self._symbol_connections

        self._symbol_connections[symbol].add(connection_id)
        self._connection_symbols[connection_id].add(symbol)
        if first_subscriber:
            for callback in self._subscribe_callbacks:
                asyncio.create_task(callback(symbol))

    def subscribe_many(
        self,
        connection_id: str,
        symbols: list[str],
    ) -> None:
        for symbol in symbols:
            self.subscribe(connection_id, symbol)

    def unsubscribe(self, connection_id: str, symbol: str) -> bool:
        """
        Returns True if there are no more subscribers for this symbol.
        """

        symbol = symbol.upper()

        self._symbol_connections[symbol].discard(connection_id)
        self._connection_symbols[connection_id].discard(symbol)

        if not self._symbol_connections[symbol]:
            self._symbol_connections.pop(symbol, None)

            for callback in self._unsubscribe_callbacks:
                asyncio.create_task(callback(symbol))

            no_subscribers = True
        else:
            no_subscribers = False

        if not self._connection_symbols[connection_id]:
            self._connection_symbols.pop(connection_id, None)

        return no_subscribers

    def unsubscribe_many(
        self,
        connection_id: str,
        symbols: list[str],
    ) -> list[str]:
        """
        Returns a list of symbols that now have zero subscribers.
        """

        removed = []

        for symbol in symbols:
            if self.unsubscribe(connection_id, symbol):
                removed.append(symbol.upper())

        return removed

    def remove_connection(self, connection_id: str) -> list[str]:
        """
        Removes a disconnected websocket from every subscription.

        Returns all symbols that now have zero subscribers.
        """

        symbols = list(self._connection_symbols.get(connection_id, set()))

        empty_symbols = []

        for symbol in symbols:
            if self.unsubscribe(connection_id, symbol):
                empty_symbols.append(symbol)

        return empty_symbols

    def get_connections(self, symbol: str) -> set[str]:
        return self._symbol_connections.get(symbol.upper(), set()).copy()

    def get_symbols(self, connection_id: str) -> set[str]:
        return self._connection_symbols.get(connection_id, set()).copy()

    def has_symbol(self, symbol: str) -> bool:
        return symbol.upper() in self._symbol_connections

    def subscriber_count(self, symbol: str) -> int:
        return len(self._symbol_connections.get(symbol.upper(), set()))

    def is_subscribed(
        self,
        connection_id: str,
        symbol: str,
    ) -> bool:
        return connection_id in self._symbol_connections.get(symbol.upper(), set())


subscription_manager = SubscriptionManager()
