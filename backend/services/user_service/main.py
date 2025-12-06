"""
User Service - FastAPI application for user management.
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import json

from ...common.config import settings
from ...common.database import get_mysql_session, init_mysql_db
from ...common.exceptions import (
    DuplicateUserException, InvalidUserIdException, KayakException,
    handle_duplicate_user, handle_not_found, handle_invalid_user_id
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from ...schemas.user_schemas import (
    UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse
)
from ...common.image_upload import save_profile_image
from .service import UserService
from .auth import create_access_token, get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Kayak User Service",
    description="User management microservice for Kayak simulation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(InvalidUserIdException)
async def invalid_user_id_handler(request, exc: InvalidUserIdException):
    """Handle InvalidUserIdException from Pydantic validators."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": {
                "message": exc.message,
                "error_code": "INVALID_USER_ID",
                "details": exc.details
            }
        }
    )


@app.exception_handler(KayakException)
async def kayak_exception_handler(request, exc: KayakException):
    """Handle general KayakException."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": {
                "message": exc.message,
                "details": exc.details
            }
        }
    )


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting User Service...")
    init_mysql_db()
    # Mount static files for serving uploaded images
    try:
        app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")
    logger.info("User Service started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down User Service...")


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity checks."""
    from ...common.health import get_comprehensive_health
    return await get_comprehensive_health(
        check_mysql=True,
        check_redis=True,
        service_name="user-service"
    )


# ==================== User Endpoints ====================

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_id: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone_number: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_mysql_session)
):
    """Create a new user with optional profile image."""
    try:
        # Handle image upload if provided
        profile_image_url = None
        if profile_image:
            profile_image_url = await save_profile_image(profile_image, user_type="user")
        
        # Create user data object
        user_data = UserCreate(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            phone_number=phone_number,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            profile_image_url=profile_image_url
        )
        
        service = UserService(db)
        user = service.create_user(user_data)
        return user
    except DuplicateUserException:
        handle_duplicate_user(user_id)
    except InvalidUserIdException:
        handle_invalid_user_id(user_id)


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_mysql_session)
):
    """Get user by ID."""
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        handle_not_found("User", user_id)
    return user


@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    zip_code: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_mysql_session)
):
    """Update user information with optional profile image."""
    service = UserService(db)
    
    # Handle image upload if provided
    profile_image_url = None
    if profile_image:
        profile_image_url = await save_profile_image(profile_image, user_type="user")
    
    # Create update data object
    user_data = UserUpdate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        address=address,
        city=city,
        state=state,
        zip_code=zip_code,
        profile_image_url=profile_image_url
    )
    
    user = service.update_user(user_id, user_data)
    if not user:
        handle_not_found("User", user_id)
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_mysql_session)
):
    """Delete a user."""
    service = UserService(db)
    success = service.delete_user(user_id)
    if not success:
        handle_not_found("User", user_id)


@app.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    db: Session = Depends(get_mysql_session)
):
    """List all users with pagination."""
    service = UserService(db)
    return service.list_users(skip=skip, limit=limit, search=search)


# ==================== Authentication Endpoints ====================

@app.post("/auth/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_mysql_session)
):
    """User login."""
    logger.info(f"Login attempt for email: {credentials.email}")
    service = UserService(db)
    user = service.authenticate_user(credentials.email, credentials.password)
    if not user:
        logger.warning(f"Authentication failed for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    logger.info(f"Authentication successful for user: {user.user_id}")
    
    access_token = create_access_token(data={"sub": user.user_id})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current authenticated user."""
    return current_user


# ==================== Booking History Endpoints ====================

@app.get("/users/{user_id}/bookings")
async def get_user_bookings(
    user_id: str,
    booking_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_mysql_session)
):
    """Get user's booking history."""
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        handle_not_found("User", user_id)
    
    return service.get_user_bookings(
        user_id,
        booking_type=booking_type,
        status=status
    )


@app.get("/users/{user_id}/reviews")
async def get_user_reviews(
    user_id: str,
    db: Session = Depends(get_mysql_session)
):
    """Get reviews submitted by user."""
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        handle_not_found("User", user_id)
    
    return service.get_user_reviews(user_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

