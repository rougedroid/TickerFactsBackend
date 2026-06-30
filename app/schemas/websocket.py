from typing import Any, Literal

from pydantic import BaseModel, Field

from app.realtime.constants import MessageType


class WSMessage(BaseModel):
    """
    Base WebSocket message.
    Every websocket payload contains a 'type'.
    """

    type: MessageType


# ===================================================================
# Client -> Server Messages
# ===================================================================

class SubscribeMessage(WSMessage):
    """
    Subscribe to one or more ticker symbols.
    """

    type: Literal[MessageType.SUBSCRIBE] = MessageType.SUBSCRIBE
    symbols: list[str] = Field(default_factory=list)


class UnsubscribeMessage(WSMessage):
    """
    Unsubscribe from one or more ticker symbols.
    """

    type: Literal[MessageType.UNSUBSCRIBE] = MessageType.UNSUBSCRIBE
    symbols: list[str] = Field(default_factory=list)


class HeartbeatMessage(WSMessage):
    """
    Client heartbeat.
    """

    type: Literal[MessageType.HEARTBEAT] = MessageType.HEARTBEAT


# ===================================================================
# Server -> Client Messages
# ===================================================================

class SubscriptionAck(WSMessage):
    """
    Sent after a successful subscription.
    """

    type: Literal[MessageType.SUBSCRIBED] = MessageType.SUBSCRIBED
    symbols: list[str]


class UnsubscriptionAck(WSMessage):
    """
    Sent after a successful unsubscription.
    """

    type: Literal[MessageType.UNSUBSCRIBED] = MessageType.UNSUBSCRIBED
    symbols: list[str]


class PriceUpdateMessage(WSMessage):
    """
    Live price update.
    """

    type: Literal[MessageType.PRICE_UPDATE] = MessageType.PRICE_UPDATE

    symbol: str

    price: float

    volume: float

    timestamp: int


class FilingUpdateMessage(WSMessage):
    """
    SEC filing update.
    """

    type: Literal[MessageType.FILING_UPDATE] = MessageType.FILING_UPDATE

    symbol: str

    filing_type: str

    accession_number: str

    payload: dict[str, Any]


class MetricUpdateMessage(WSMessage):
    """
    Extracted metrics update.
    """

    type: Literal[MessageType.METRIC_UPDATE] = MessageType.METRIC_UPDATE

    symbol: str

    metrics: dict[str, Any]


class ErrorMessage(WSMessage):
    """
    Error message sent to the client.
    """

    type: Literal[MessageType.ERROR] = MessageType.ERROR

    message: str