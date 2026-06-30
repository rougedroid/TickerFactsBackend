from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.realtime.connection_manager import connection_manager
from app.realtime.subscription_manager import subscription_manager
from app.schemas.websocket import (
    ErrorMessage,
    SubscriptionAck,
    UnsubscriptionAck,
)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    Main websocket endpoint.

    Supported messages:

    {
        "type": "subscribe",
        "symbols": ["AAPL", "MSFT"]
    }

    {
        "type": "unsubscribe",
        "symbols": ["AAPL"]
    }
    """

    # ------------------------------------------------------------------
    # TODO: Authenticate websocket connection.
    #
    # Example:
    #
    # token = websocket.query_params.get("token")
    #
    # user = await verify_token(token)
    #
    # if user is None:
    #     await websocket.close(code=1008)
    #     return
    #
    # Store the user -> connection mapping inside ConnectionManager.
    # ------------------------------------------------------------------

    connection_id = await connection_manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_json()

            message_type = message.get("type")

            if message_type == "subscribe":
                symbols = [
                    symbol.upper()
                    for symbol in message.get("symbols", [])
                ]

                subscription_manager.subscribe_many(
                    connection_id,
                    symbols,
                )

                await connection_manager.send(
                    connection_id,
                    SubscriptionAck(
                        symbols=symbols,
                    ),
                )

            elif message_type == "unsubscribe":
                symbols = [
                    symbol.upper()
                    for symbol in message.get("symbols", [])
                ]

                subscription_manager.unsubscribe_many(
                    connection_id,
                    symbols,
                )

                await connection_manager.send(
                    connection_id,
                    UnsubscriptionAck(
                        symbols=symbols,
                    ),
                )

            else:
                await connection_manager.send(
                    connection_id,
                    ErrorMessage(
                        message="Unknown websocket message type."
                    ),
                )

    except WebSocketDisconnect:
        pass

    finally:
        subscription_manager.remove_connection(connection_id)
        await connection_manager.disconnect(connection_id)