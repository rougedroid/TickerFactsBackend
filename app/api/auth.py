from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.db.database import get_db
from app.schemas.auth import GoogleAuth
from app.services.auth_service import AuthService
from fastapi import Request

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

@router.get("/me")
async def me(
    user: User = Depends(get_current_user),
):

    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "role": user.role,
    }

@router.post("/logout")
async def logout():

    response = JSONResponse(
        content={
            "message": "Logged out."
        }
    )

    response.delete_cookie(
        key="access_token",
        path="/",
    )

    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
    )

    return response

@router.post("/refresh")
async def refresh(
    request: Request,
    db: AsyncSession = Depends(get_db),
):

    refresh_token = request.cookies.get(
        "refresh_token"
    )

    if refresh_token is None:
        raise HTTPException(
            status_code=401,
            detail="No refresh token.",
        )

    service = AuthService(db)

    try:

        access = await service.refresh_access_token(
            refresh_token
        )

        response = JSONResponse(
            content={
                "message": "Token refreshed."
            }
        )

        response.set_cookie(
            key="access_token",
            value=access,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
            max_age=60 * 15,
        )

        return response

    except ValueError as e:

        raise HTTPException(
            status_code=401,
            detail=str(e),
        )