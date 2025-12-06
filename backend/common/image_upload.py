"""
Image upload utility for handling profile images.
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Base directory for uploaded images
UPLOAD_BASE_DIR = Path("/app/uploads")
PROFILE_IMAGES_DIR = UPLOAD_BASE_DIR / "profiles"

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure directories exist
PROFILE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )


async def save_profile_image(file: UploadFile, user_type: str = "user") -> str:
    """
    Save uploaded profile image and return the URL path.
    
    Args:
        file: Uploaded file
        user_type: Type of user ('user' or 'admin')
    
    Returns:
        URL path to the saved image (e.g., '/uploads/profiles/user_abc123.jpg')
    """
    validate_image_file(file)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{user_type}_{uuid.uuid4().hex[:12]}{file_ext}"
    file_path = PROFILE_IMAGES_DIR / unique_filename
    
    # Read and save file
    try:
        contents = await file.read()
        
        # Check file size
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Return URL path (relative to static files)
        return f"/uploads/profiles/{unique_filename}"
    
    except Exception as e:
        logger.error(f"Error saving profile image: {str(e)}")
        if file_path.exists():
            file_path.unlink()  # Clean up on error
        raise HTTPException(status_code=500, detail="Failed to save image")


def delete_profile_image(image_url: Optional[str]) -> None:
    """Delete a profile image file."""
    if not image_url:
        return
    
    try:
        # Extract filename from URL
        filename = Path(image_url).name
        file_path = PROFILE_IMAGES_DIR / filename
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted profile image: {filename}")
    except Exception as e:
        logger.error(f"Error deleting profile image: {str(e)}")

