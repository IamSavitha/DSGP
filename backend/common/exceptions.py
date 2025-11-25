"""
Custom exceptions for the Kayak Simulation system.
"""
from fastapi import HTTPException, status
from typing import Optional, Any


class KayakException(Exception):
    """Base exception for Kayak system."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


class DuplicateUserException(KayakException):
    """Exception raised when attempting to create a duplicate user."""
    
    def __init__(self, user_id: str):
        super().__init__(
            message=f"User with ID {user_id} already exists",
            details={"user_id": user_id}
        )


class InvalidStateException(KayakException):
    """Exception raised for invalid US state abbreviations."""
    
    VALID_STATES = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
    }
    
    def __init__(self, state: str):
        super().__init__(
            message=f"Invalid state abbreviation: {state}",
            details={"provided_state": state, "valid_states": list(self.VALID_STATES)}
        )


class InvalidZipCodeException(KayakException):
    """Exception raised for invalid ZIP code format."""
    
    def __init__(self, zip_code: str):
        super().__init__(
            message=f"Invalid ZIP code format: {zip_code}. Valid formats: ##### or #####-####",
            details={"provided_zip": zip_code}
        )


class InvalidUserIdException(KayakException):
    """Exception raised for invalid user ID (SSN format)."""
    
    def __init__(self, user_id: str):
        super().__init__(
            message=f"Invalid user ID format: {user_id}. Required format: XXX-XX-XXXX",
            details={"provided_id": user_id}
        )


class ResourceNotFoundException(KayakException):
    """Exception raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID {resource_id} not found",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class BookingFailedException(KayakException):
    """Exception raised when a booking operation fails."""
    
    def __init__(self, reason: str, booking_type: str):
        super().__init__(
            message=f"Booking failed for {booking_type}: {reason}",
            details={"booking_type": booking_type, "reason": reason}
        )


class PaymentFailedException(KayakException):
    """Exception raised when a payment operation fails."""
    
    def __init__(self, reason: str, amount: float = None):
        super().__init__(
            message=f"Payment failed: {reason}",
            details={"reason": reason, "amount": amount}
        )


class UnauthorizedException(KayakException):
    """Exception raised for unauthorized access."""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message=message)


class ConcurrencyException(KayakException):
    """Exception raised for concurrency conflicts."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"Concurrency conflict for {resource_type} {resource_id}",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


# ==================== HTTP Exception Handlers ====================

def raise_http_exception(exception: KayakException, status_code: int = status.HTTP_400_BAD_REQUEST):
    """Convert KayakException to HTTPException."""
    raise HTTPException(
        status_code=status_code,
        detail={
            "message": exception.message,
            "details": exception.details
        }
    )


def handle_duplicate_user(user_id: str):
    """Raise HTTP exception for duplicate user."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "message": f"User with ID {user_id} already exists",
            "error_code": "DUPLICATE_USER"
        }
    )


def handle_invalid_state(state: str):
    """Raise HTTP exception for invalid state."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": f"Invalid state abbreviation: {state}",
            "error_code": "INVALID_STATE"
        }
    )


def handle_invalid_zip_code(zip_code: str):
    """Raise HTTP exception for invalid ZIP code."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": f"Invalid ZIP code: {zip_code}",
            "error_code": "INVALID_ZIP_CODE"
        }
    )


def handle_invalid_user_id(user_id: str):
    """Raise HTTP exception for invalid user ID."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": f"Invalid user ID format: {user_id}. Expected format: XXX-XX-XXXX",
            "error_code": "INVALID_USER_ID"
        }
    )


def handle_not_found(resource_type: str, resource_id: str):
    """Raise HTTP exception for resource not found."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "message": f"{resource_type} not found",
            "resource_id": resource_id,
            "error_code": "NOT_FOUND"
        }
    )

