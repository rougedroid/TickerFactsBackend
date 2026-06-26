from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# @router.post("/register")
# async def register():
#     return {"message": "Coming soon"}


# @router.post("/login")
# async def login():
#     return {"message": "Coming soon"}


@router.post("/refresh")
async def refresh():
    return {"message": "Coming soon"}


@router.get("/me")
async def me():
    return {"message": "Coming soon"}