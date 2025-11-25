"""
Validation utilities for the Kayak Simulation system.
"""
import re
from typing import Optional
from .exceptions import (
    InvalidStateException,
    InvalidZipCodeException,
    InvalidUserIdException
)


# ==================== Constants ====================

VALID_US_STATES = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
}

# Reverse mapping for full state names
STATE_NAME_TO_ABBREV = {v.upper(): k for k, v in VALID_US_STATES.items()}

# Regex patterns
SSN_PATTERN = re.compile(r'^[0-9]{3}-[0-9]{2}-[0-9]{4}$')
ZIP_CODE_PATTERN = re.compile(r'^[0-9]{5}(-[0-9]{4})?$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_PATTERN = re.compile(r'^(\+1)?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$')
FLIGHT_ID_PATTERN = re.compile(r'^[A-Z]{2}[0-9]{1,4}$')


# ==================== Validators ====================

def validate_state(state: str, raise_exception: bool = True) -> bool:
    """
    Validate US state abbreviation or full name.
    
    Args:
        state: State abbreviation (e.g., 'CA') or full name (e.g., 'California')
        raise_exception: If True, raise exception on invalid state
    
    Returns:
        True if valid, False otherwise
    
    Raises:
        InvalidStateException: If state is invalid and raise_exception is True
    """
    state_upper = state.upper().strip()
    
    # Check abbreviation
    if state_upper in VALID_US_STATES:
        return True
    
    # Check full state name
    if state_upper in STATE_NAME_TO_ABBREV:
        return True
    
    if raise_exception:
        raise InvalidStateException(state)
    return False


def normalize_state(state: str) -> str:
    """
    Normalize state to 2-letter abbreviation.
    
    Args:
        state: State abbreviation or full name
    
    Returns:
        2-letter state abbreviation
    
    Raises:
        InvalidStateException: If state is invalid
    """
    state_upper = state.upper().strip()
    
    if state_upper in VALID_US_STATES:
        return state_upper
    
    if state_upper in STATE_NAME_TO_ABBREV:
        return STATE_NAME_TO_ABBREV[state_upper]
    
    raise InvalidStateException(state)


def validate_zip_code(zip_code: str, raise_exception: bool = True) -> bool:
    """
    Validate ZIP code format.
    
    Valid formats:
        - ##### (e.g., 95123)
        - #####-#### (e.g., 90086-1929)
    
    Args:
        zip_code: ZIP code string
        raise_exception: If True, raise exception on invalid ZIP code
    
    Returns:
        True if valid, False otherwise
    
    Raises:
        InvalidZipCodeException: If ZIP code is invalid and raise_exception is True
    """
    if ZIP_CODE_PATTERN.match(zip_code.strip()):
        return True
    
    if raise_exception:
        raise InvalidZipCodeException(zip_code)
    return False


def validate_user_id(user_id: str, raise_exception: bool = True) -> bool:
    """
    Validate user ID (SSN format: XXX-XX-XXXX).
    
    Args:
        user_id: User ID string
        raise_exception: If True, raise exception on invalid ID
    
    Returns:
        True if valid, False otherwise
    
    Raises:
        InvalidUserIdException: If user ID is invalid and raise_exception is True
    """
    if SSN_PATTERN.match(user_id.strip()):
        return True
    
    if raise_exception:
        raise InvalidUserIdException(user_id)
    return False


def validate_email(email: str, raise_exception: bool = True) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string
        raise_exception: If True, raise exception on invalid email
    
    Returns:
        True if valid, False otherwise
    """
    if EMAIL_PATTERN.match(email.strip()):
        return True
    
    if raise_exception:
        from .exceptions import KayakException
        raise KayakException(f"Invalid email format: {email}")
    return False


def validate_phone(phone: str, raise_exception: bool = True) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
        raise_exception: If True, raise exception on invalid phone
    
    Returns:
        True if valid, False otherwise
    """
    # Remove common formatting characters for validation
    cleaned = re.sub(r'[\s.-]', '', phone)
    if len(cleaned) >= 10 and cleaned.replace('+', '').isdigit():
        return True
    
    if raise_exception:
        from .exceptions import KayakException
        raise KayakException(f"Invalid phone number format: {phone}")
    return False


def validate_flight_id(flight_id: str, raise_exception: bool = True) -> bool:
    """
    Validate flight ID format (e.g., AA123).
    
    Args:
        flight_id: Flight ID string
        raise_exception: If True, raise exception on invalid ID
    
    Returns:
        True if valid, False otherwise
    """
    if FLIGHT_ID_PATTERN.match(flight_id.upper().strip()):
        return True
    
    if raise_exception:
        from .exceptions import KayakException
        raise KayakException(f"Invalid flight ID format: {flight_id}")
    return False


def validate_credit_card(card_number: str) -> bool:
    """
    Validate credit card number using Luhn algorithm.
    
    Args:
        card_number: Credit card number (digits only or with spaces/dashes)
    
    Returns:
        True if valid, False otherwise
    """
    # Remove non-digit characters
    digits = re.sub(r'\D', '', card_number)
    
    if len(digits) < 13 or len(digits) > 19:
        return False
    
    # Luhn algorithm
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits_list = digits_of(card_num)
        odd_digits = digits_list[-1::-2]
        even_digits = digits_list[-2::-2]
        
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        
        return checksum % 10
    
    return luhn_checksum(digits) == 0


def sanitize_string(value: str) -> str:
    """
    Sanitize string input by removing dangerous characters.
    
    Args:
        value: Input string
    
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove potential SQL injection characters
    dangerous_chars = ['--', ';', "'", '"', '/*', '*/', 'xp_', 'sp_']
    result = value
    for char in dangerous_chars:
        result = result.replace(char, '')
    
    return result.strip()


def validate_positive_number(value: float, field_name: str = "value") -> bool:
    """
    Validate that a number is positive.
    
    Args:
        value: Number to validate
        field_name: Name of the field for error message
    
    Returns:
        True if valid
    
    Raises:
        KayakException: If value is not positive
    """
    if value <= 0:
        from .exceptions import KayakException
        raise KayakException(f"{field_name} must be positive, got {value}")
    return True


def validate_date_range(start_date, end_date, field_name: str = "Date") -> bool:
    """
    Validate that start date is before end date.
    
    Args:
        start_date: Start date
        end_date: End date
        field_name: Name of the field for error message
    
    Returns:
        True if valid
    
    Raises:
        KayakException: If start date is after end date
    """
    if start_date > end_date:
        from .exceptions import KayakException
        raise KayakException(f"{field_name} range is invalid: start must be before end")
    return True

