from enum import StrEnum


class MessageType(StrEnum):
    # Client -> Server
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"

    # Server -> Client
    SUBSCRIBED = "subscribed"
    UNSUBSCRIBED = "unsubscribed"

    PRICE_UPDATE = "price_update"
    METRIC_UPDATE = "metric_update"
    FILING_UPDATE = "filing_update"

    HEARTBEAT = "heartbeat"

    ERROR = "error"


class RedisChannel(StrEnum):
    PRICE = "price"
    METRIC = "metric"
    FILING = "filing"