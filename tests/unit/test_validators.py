"""
Unit tests for validators.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.common.validators import (
    validate_state, validate_zip_code, validate_user_id,
    validate_email, validate_phone, normalize_state
)
from backend.common.exceptions import (
    InvalidStateException, InvalidZipCodeException, InvalidUserIdException
)


class TestStateValidator:
    """Tests for state validation."""
    
    def test_valid_state_abbreviation(self):
        assert validate_state("CA") == True
        assert validate_state("ny") == True
        assert validate_state("TX") == True
    
    def test_valid_state_full_name(self):
        assert validate_state("California") == True
        assert validate_state("NEW YORK") == True
    
    def test_invalid_state(self):
        with pytest.raises(InvalidStateException):
            validate_state("XX")
        
        with pytest.raises(InvalidStateException):
            validate_state("Invalid")
    
    def test_normalize_state(self):
        assert normalize_state("california") == "CA"
        assert normalize_state("NY") == "NY"
        assert normalize_state("texas") == "TX"


class TestZipCodeValidator:
    """Tests for ZIP code validation."""
    
    def test_valid_5_digit_zip(self):
        assert validate_zip_code("95123") == True
        assert validate_zip_code("10001") == True
    
    def test_valid_9_digit_zip(self):
        assert validate_zip_code("95123-4567") == True
        assert validate_zip_code("90086-1929") == True
    
    def test_invalid_zip_codes(self):
        with pytest.raises(InvalidZipCodeException):
            validate_zip_code("1234")  # Too short
        
        with pytest.raises(InvalidZipCodeException):
            validate_zip_code("1829A")  # Contains letter
        
        with pytest.raises(InvalidZipCodeException):
            validate_zip_code("37849-392")  # Invalid format


class TestUserIdValidator:
    """Tests for user ID (SSN format) validation."""
    
    def test_valid_user_ids(self):
        assert validate_user_id("123-45-6789") == True
        assert validate_user_id("000-00-0000") == True
        assert validate_user_id("999-99-9999") == True
    
    def test_invalid_user_ids(self):
        with pytest.raises(InvalidUserIdException):
            validate_user_id("12345678")  # No dashes
        
        with pytest.raises(InvalidUserIdException):
            validate_user_id("123-456-789")  # Wrong format
        
        with pytest.raises(InvalidUserIdException):
            validate_user_id("12-345-6789")  # Wrong grouping


class TestEmailValidator:
    """Tests for email validation."""
    
    def test_valid_emails(self):
        assert validate_email("user@example.com") == True
        assert validate_email("test.user@domain.org") == True
    
    def test_invalid_emails(self):
        assert validate_email("invalid", raise_exception=False) == False
        assert validate_email("@domain.com", raise_exception=False) == False


class TestPhoneValidator:
    """Tests for phone validation."""
    
    def test_valid_phones(self):
        assert validate_phone("555-123-4567") == True
        assert validate_phone("(555) 123-4567") == True
        assert validate_phone("5551234567") == True
    
    def test_invalid_phones(self):
        assert validate_phone("12345", raise_exception=False) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

