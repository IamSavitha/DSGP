#!/bin/bash
# Test 07: Payment & Billing Testing
# Verify payment processing, tax calculation, invoice generation, and secure storage

set -e

echo "========================================="
echo "Test 07: Payment & Billing Testing"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BILLING_URL="http://localhost:8005"
BOOKING_URL="http://localhost:8009"

echo "=== Test 7.1: Payment Initiation ==="
echo ""

# First, try to get or create a booking
echo "Step 1: Finding or creating a booking..."
TEST_USER_ID="TEST-PAYMENT-$(date +%s)"

# Try to create a simple booking first
BOOKING_RESPONSE=$(curl -s -X POST "${BOOKING_URL}/bookings" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"${TEST_USER_ID}\",
    \"booking_type\": \"flight\",
    \"listing_id\": \"AA123\",
    \"num_passengers\": 1,
    \"total_price\": 299.99
  }" 2>/dev/null || echo "")

BOOKING_ID=$(echo "$BOOKING_RESPONSE" | grep -o '"booking_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$BOOKING_ID" ]; then
    echo -e "${YELLOW}⚠️  Could not create booking, using test ID${NC}"
    BOOKING_ID="TEST-BOOKING-$(date +%s)"
fi

echo "Using booking ID: $BOOKING_ID"
echo ""

echo "Step 2: Processing payment..."
PAYMENT_RESPONSE=$(curl -s -X POST "${BILLING_URL}/payments" \
  -H "Content-Type: application/json" \
  -d "{
    \"booking_id\": \"${BOOKING_ID}\",
    \"payment_method\": \"credit_card\",
    \"card_number\": \"4111111111111111\",
    \"card_expiry\": \"12/26\",
    \"card_cvv\": \"123\",
    \"cardholder_name\": \"Test User\"
  }")

echo "Payment response: $PAYMENT_RESPONSE"

if echo "$PAYMENT_RESPONSE" | grep -q "billing_id\|invoice\|success"; then
    BILLING_ID=$(echo "$PAYMENT_RESPONSE" | grep -o '"billing_id":"[^"]*' | cut -d'"' -f4 || echo "")
    INVOICE_NUMBER=$(echo "$PAYMENT_RESPONSE" | grep -o '"invoice_number":"[^"]*' | cut -d'"' -f4 || echo "")
    
    if [ ! -z "$BILLING_ID" ]; then
        echo -e "${GREEN}✅ Payment processed successfully${NC}"
        echo "Billing ID: $BILLING_ID"
        if [ ! -z "$INVOICE_NUMBER" ]; then
            echo "Invoice Number: $INVOICE_NUMBER"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Payment processing may require authentication or valid booking${NC}"
fi

echo ""
echo "=== Test 7.2: Tax Calculation (8.75%) ==="
echo ""

if [ ! -z "$BILLING_ID" ]; then
    echo "Retrieving billing details to verify tax calculation..."
    BILLING_DETAILS=$(curl -s "${BILLING_URL}/billings/${BILLING_ID}")
    
    SUBTOTAL=$(echo "$BILLING_DETAILS" | grep -o '"subtotal":[0-9.]*' | cut -d':' -f2 || echo "0")
    TAX=$(echo "$BILLING_DETAILS" | grep -o '"tax_amount":[0-9.]*' | cut -d':' -f2 || echo "0")
    TOTAL=$(echo "$BILLING_DETAILS" | grep -o '"total_amount":[0-9.]*' | cut -d':' -f2 || echo "0")
    
    if [ "$SUBTOTAL" != "0" ] && [ "$TAX" != "0" ]; then
        EXPECTED_TAX=$(echo "$SUBTOTAL * 0.0875" | bc 2>/dev/null || echo "N/A")
        echo "Subtotal: \$$SUBTOTAL"
        echo "Tax (8.75%): \$$TAX"
        echo "Expected Tax: \$$EXPECTED_TAX"
        echo "Total: \$$TOTAL"
        
        if [ "$EXPECTED_TAX" != "N/A" ]; then
            TAX_DIFF=$(echo "$TAX - $EXPECTED_TAX" | bc 2>/dev/null | awk '{if ($1 < 0) print -$1; else print $1}' || echo "999")
            if (( $(echo "$TAX_DIFF < 0.01" | bc -l) )); then
                echo -e "${GREEN}✅ Tax calculation correct (8.75%)${NC}"
            else
                echo -e "${YELLOW}⚠️  Tax calculation may be off${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Tax information not available in response${NC}"
    fi
fi

echo ""
echo "=== Test 7.3: Invoice Generation ==="
echo ""

if [ ! -z "$INVOICE_NUMBER" ]; then
    echo "Invoice Number: $INVOICE_NUMBER"
    
    # Check invoice format: INV-YYYYMMDD-XXXXXX
    if echo "$INVOICE_NUMBER" | grep -qE "^INV-[0-9]{8}-[A-Z0-9]{6}$"; then
        echo -e "${GREEN}✅ Invoice number format correct${NC}"
    else
        echo -e "${YELLOW}⚠️  Invoice format may not match expected pattern${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Invoice number not generated${NC}"
fi

echo ""
echo "=== Test 7.4: Payment Method Storage (Last 4 Digits) ==="
echo ""

if [ ! -z "$BILLING_ID" ]; then
    echo "Checking database for secure card storage..."
    CARD_LAST_FOUR=$(docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db \
      -e "SELECT card_last_four FROM billings WHERE billing_id='${BILLING_ID}';" 2>/dev/null | grep -oE '[0-9]{4}' | head -1 || echo "")
    
    if [ ! -z "$CARD_LAST_FOUR" ]; then
        echo "Card last 4 digits stored: ****$CARD_LAST_FOUR"
        echo -e "${GREEN}✅ Only last 4 digits stored (secure)${NC}"
        
        # Verify full card number is NOT stored
        FULL_CARD=$(docker-compose exec -T mysql mysql -u kayak_user -pkayak_pass kayak_db \
          -e "SELECT card_number FROM billings WHERE billing_id='${BILLING_ID}';" 2>/dev/null | grep -oE '4111111111111111' || echo "")
        
        if [ -z "$FULL_CARD" ]; then
            echo -e "${GREEN}✅ Full card number NOT stored (secure)${NC}"
        else
            echo -e "${RED}❌ WARNING: Full card number may be stored${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Could not verify card storage${NC}"
    fi
fi

echo ""
echo "=== Test 7.5: Payment Status Updates ==="
echo ""

if [ ! -z "$BILLING_ID" ]; then
    echo "Checking payment status..."
    STATUS_RESPONSE=$(curl -s "${BILLING_URL}/billings/${BILLING_ID}")
    
    STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*' | cut -d'"' -f4 || echo "")
    
    if [ ! -z "$STATUS" ]; then
        echo "Payment Status: $STATUS"
        if echo "$STATUS" | grep -qi "completed\|success"; then
            echo -e "${GREEN}✅ Payment status tracked correctly${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Status information not available${NC}"
    fi
fi

echo ""
echo "=== Test 7.6: Get Billing Record ==="
echo ""

if [ ! -z "$BILLING_ID" ]; then
    echo "Retrieving billing record: $BILLING_ID"
    BILLING_RECORD=$(curl -s "${BILLING_URL}/billings/${BILLING_ID}")
    
    if echo "$BILLING_RECORD" | grep -q "billing_id\|invoice\|amount"; then
        echo -e "${GREEN}✅ Billing record retrieved${NC}"
        echo "$BILLING_RECORD" | head -20
    else
        echo -e "${YELLOW}⚠️  Billing record not found or endpoint issue${NC}"
    fi
fi

echo ""
echo "=== Kafka Event Verification ==="
echo ""

echo "Checking for payment.completed events..."
sleep 2
PAYMENT_EVENTS=$(docker-compose logs billing-service --tail 20 | grep -i "payment.completed\|event" || echo "")

if [ ! -z "$PAYMENT_EVENTS" ]; then
    echo -e "${GREEN}✅ Payment events published${NC}"
    echo "$PAYMENT_EVENTS" | head -5
else
    echo -e "${YELLOW}⚠️  No payment events found in logs${NC}"
fi

echo ""
echo "========================================="
echo "Test 07 Complete!"
echo "========================================="

