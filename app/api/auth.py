from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.auth import GoogleAuth
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/google")
async def google_login(
    payload: GoogleAuth,
    db: AsyncSession = Depends(get_db),
):

    service = AuthService(db)

    try:
        tokens = await service.login_with_google(payload.credential)
        response = JSONResponse(content={"message": "Login successful"})
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            secure=False,  # True in production
            samesite="lax",
            max_age=60 * 15,
            path="/",
        )
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,
            path="/api/v1/auth",
        )
        return response

    except ValueError as e:

        raise HTTPException(
            status_code=401,
            detail=str(e),
        )
