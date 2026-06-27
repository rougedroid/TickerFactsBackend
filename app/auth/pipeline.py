from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_pipeline_key(
    x_api_key: str = Header(...),
):

    if x_api_key != settings.PIPELINE_API_KEY:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key.",
        )