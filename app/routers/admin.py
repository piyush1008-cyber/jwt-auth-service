from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserResponse
from app.dependencies import require_role

router = APIRouter(prefix="/api/v1/admin", tags=["Admin (RBAC)"])


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List all registered accounts (Admin/Moderator only)"
)
def list_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(["admin", "moderator"]))
):
    """RBAC protected endpoint restricted to administrative staff."""
    return db.query(User).all()


@router.get(
    "/stats",
    summary="Aggregate user and role metrics (Admin only)"
)
def get_system_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(["admin"]))
):
    """Privileged endpoint returning security and user statistics."""
    total_users = db.query(User).count()
    admins = db.query(User).filter(User.role == "admin").count()
    moderators = db.query(User).filter(User.role == "moderator").count()
    standard_users = db.query(User).filter(User.role == "user").count()

    return {
        "total_registered_users": total_users,
        "role_breakdown": {
            "admin": admins,
            "moderator": moderators,
            "user": standard_users
        },
        "requested_by": admin_user.username
    }
