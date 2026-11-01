from fastapi import APIRouter, Depends
from app.models import User
from app.schemas import UserResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Retrieve authenticated user profile"
)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Protected endpoint returning the profile of the bearer token owner."""
    return current_user
