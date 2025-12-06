#!/bin/bash

# Test 7.4: Payment Method Storage Verification Script
# This script verifies that only last 4 digits of card numbers are stored

echo "=========================================="
echo "Test 7.4: Payment Method Storage Verification"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if MySQL container is running
if ! docker-compose ps | grep -q "mysql.*Up"; then
    echo -e "${RED}❌ MySQL container is not running${NC}"
    echo "Please start services with: docker-compose up -d"
    exit 1
fi

echo "1. Checking most recent billing record..."
echo "-------------------------------------------"
RECENT_BILLING=$(docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db -sN <<EOF
SELECT 
    CONCAT('Billing ID: ', billing_id, ' | Payment Method: ', payment_method, ' | Last 4: ', COALESCE(card_last_four, 'NULL'), ' | Digits: ', COALESCE(LENGTH(card_last_four), 0))
FROM billings
ORDER BY created_at DESC
LIMIT 1;
EOF
)

if [ -z "$RECENT_BILLING" ]; then
    echo -e "${YELLOW}⚠️  No billing records found. Process a payment first.${NC}"
else
    echo "$RECENT_BILLING"
    
    # Extract digit count
    DIGIT_COUNT=$(docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db -sN <<EOF
SELECT LENGTH(card_last_four)
FROM billings
WHERE card_last_four IS NOT NULL
ORDER BY created_at DESC
LIMIT 1;
EOF
)
    
    if [ "$DIGIT_COUNT" = "4" ]; then
        echo -e "${GREEN}✅ Last 4 digits correctly stored (4 digits)${NC}"
    elif [ -z "$DIGIT_COUNT" ]; then
        echo -e "${YELLOW}⚠️  No card_last_four value found${NC}"
    else
        echo -e "${RED}❌ ERROR: card_last_four has $DIGIT_COUNT digits (should be 4)${NC}"
    fi
fi

echo ""
echo "2. Verifying no violations (more than 4 digits)..."
echo "-------------------------------------------"
VIOLATIONS=$(docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db -sN <<EOF
SELECT COUNT(*)
FROM billings
WHERE card_last_four IS NOT NULL
  AND LENGTH(card_last_four) > 4;
EOF
)

if [ "$VIOLATIONS" = "0" ]; then
    echo -e "${GREEN}✅ No violations found - all card_last_four values are 4 digits or less${NC}"
else
    echo -e "${RED}❌ ERROR: Found $VIOLATIONS billing records with more than 4 digits in card_last_four${NC}"
fi

echo ""
echo "3. Checking database schema for card-related columns..."
echo "-------------------------------------------"
CARD_COLUMNS=$(docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db -sN <<EOF
SELECT CONCAT(COLUMN_NAME, ' (', DATA_TYPE, 
    CASE 
        WHEN CHARACTER_MAXIMUM_LENGTH IS NOT NULL THEN CONCAT('(', CHARACTER_MAXIMUM_LENGTH, ')')
        ELSE ''
    END, ')')
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'kayak_db'
  AND TABLE_NAME = 'billings'
  AND (COLUMN_NAME LIKE '%card%' OR COLUMN_NAME LIKE '%credit%')
ORDER BY COLUMN_NAME;
EOF
)

if [ -z "$CARD_COLUMNS" ]; then
    echo -e "${YELLOW}⚠️  No card-related columns found in billings table${NC}"
else
    echo "Card-related columns in billings table:"
    echo "$CARD_COLUMNS" | while read -r line; do
        if echo "$line" | grep -q "card_last_four"; then
            echo -e "${GREEN}✅ $line${NC}"
        else
            echo -e "   $line"
        fi
    done
    
    # Check for forbidden columns
    FORBIDDEN=$(echo "$CARD_COLUMNS" | grep -iE "(card_number|full_card|credit_card_number)" || true)
    if [ -n "$FORBIDDEN" ]; then
        echo -e "${RED}❌ ERROR: Found forbidden columns that could store full card numbers:${NC}"
        echo "$FORBIDDEN"
    else
        echo -e "${GREEN}✅ No forbidden columns found${NC}"
    fi
fi

echo ""
echo "4. Checking users table for card storage..."
echo "-------------------------------------------"
USER_CARD_COLUMNS=$(docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db -sN <<EOF
SELECT CONCAT(COLUMN_NAME, ' (', DATA_TYPE, 
    CASE 
        WHEN CHARACTER_MAXIMUM_LENGTH IS NOT NULL THEN CONCAT('(', CHARACTER_MAXIMUM_LENGTH, ')')
        ELSE ''
    END, ')')
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'kayak_db'
  AND TABLE_NAME = 'users'
  AND (COLUMN_NAME LIKE '%card%' OR COLUMN_NAME LIKE '%credit%')
ORDER BY COLUMN_NAME;
EOF
)

if [ -n "$USER_CARD_COLUMNS" ]; then
    echo "Card-related columns in users table:"
    echo "$USER_CARD_COLUMNS" | while read -r line; do
        if echo "$line" | grep -q "credit_card_last_four"; then
            echo -e "${GREEN}✅ $line${NC}"
        else
            echo "   $line"
        fi
    done
else
    echo -e "${YELLOW}⚠️  No card-related columns in users table${NC}"
fi

echo ""
echo "5. Summary of all billing records with card info..."
echo "-------------------------------------------"
SUMMARY=$(docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db <<EOF
SELECT 
    COUNT(*) as total_billings,
    COUNT(card_last_four) as billings_with_card_info,
    SUM(CASE WHEN LENGTH(card_last_four) = 4 THEN 1 ELSE 0 END) as correct_format,
    SUM(CASE WHEN LENGTH(card_last_four) > 4 THEN 1 ELSE 0 END) as violations
FROM billings;
EOF
)

echo "$SUMMARY"

echo ""
echo "=========================================="
echo "Verification Complete"
echo "=========================================="
echo ""
echo "Expected Results:"
echo "  ✅ card_last_four should be exactly 4 digits"
echo "  ✅ No violations (records with >4 digits)"
echo "  ✅ No forbidden columns (card_number, full_card, etc.)"
echo "  ✅ Only last 4 digits stored, full card number NOT stored"
echo ""

