"""
Authentication utilities for Admin Service.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import bcrypt

from ...common.config import settings
from ...common.database import get_mysql_session
from ...models.mysql_models import Admin, AdminRole

security = HTTPBearer()


def create_admin_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token for admin."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "admin"})  # Mark as admin token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_admin_token(token: str) -> Optional[dict]:
    """Verify JWT token and return admin info."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        # Check if it's an admin token
        if payload.get("type") != "admin":
            return None
        admin_id: str = payload.get("sub")
        if admin_id is None:
            return None
        return {"admin_id": admin_id, "role": payload.get("role")}
    except JWTError:
        return None


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_mysql_session)
) -> Admin:
    """Get current authenticated admin from JWT token."""
    import logging
    logger = logging.getLogger(__name__)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        admin_info = verify_admin_token(token)
        
        if admin_info is None:
            logger.warning("Token verification failed: admin_info is None")
            raise credentials_exception
        
        admin = db.query(Admin).filter(Admin.admin_id == admin_info["admin_id"]).first()
        
        if admin is None:
            logger.warning(f"Admin not found for admin_id: {admin_info['admin_id']}")
            raise credentials_exception
        
        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is deactivated"
            )
        
        return admin
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_current_admin: {e}", exc_info=True)
        raise credentials_exception


async def require_admin_role(
    required_role: AdminRole = AdminRole.ADMIN,
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """Require specific admin role."""
    role_hierarchy = {
        "moderator": 1,
        "admin": 2,
        "super_admin": 3
    }
    
    # Handle both string and enum roles
    admin_role = current_admin.role if isinstance(current_admin.role, str) else current_admin.role.value
    required_role_str = required_role.value if isinstance(required_role, AdminRole) else required_role
    
    if role_hierarchy.get(admin_role.lower(), 0) < role_hierarchy.get(required_role_str.lower(), 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Requires {required_role_str} role or higher"
        )
    
    return current_admin


async def require_super_admin(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """Require super admin role."""
    return await require_admin_role(AdminRole.SUPER_ADMIN, current_admin)

