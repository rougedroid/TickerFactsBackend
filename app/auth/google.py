from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings


def verify_google_token(token: str):

    try:
        info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        return {
            "provider_id": info["sub"],
            "email": info["email"],
            "name": info.get("name", ""),
            "picture": info.get("picture"),
        }

    except Exception:
        return None
