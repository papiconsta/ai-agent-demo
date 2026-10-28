import token

from fastapi import APIRouter, HTTPException, status

from api.auth.schemas import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

# async def authenticate_user(username: str, password: str) -> bool:
#         # Placeholder for actual authentication logic
#         return username == "admin" and password == "password"


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, service: AuthService = Depends(get_auth_service)):

    token = await service.authenticate(body.username, body.password)
    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return TokenResponse(access_token=token)