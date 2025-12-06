"""
Billing Service - FastAPI application for payment and billing management.
"""
from fastapi import FastAPI, Depends, Query, status, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from ...common.database import get_mysql_session, init_mysql_db
from ...common.exceptions import handle_not_found
from ...schemas.billing_schemas import (
    PaymentRequest, BillingResponse, BillingSearchParams,
    BillingListResponse, RefundRequest, RefundApprovalRequest
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kayak Billing Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting Billing Service...")
    init_mysql_db()


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity checks."""
    from ...common.health import get_comprehensive_health
    return await get_comprehensive_health(
        check_mysql=True,
        service_name="billing-service"
    )


@app.post("/payments", response_model=BillingResponse)
async def process_payment(
    payment: PaymentRequest,
    db: Session = Depends(get_mysql_session)
):
    """Process a payment for a booking."""
    from .service import BillingService
    service = BillingService(db)
    
    try:
        billing = service.process_payment(payment)
        return billing
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/billings/{billing_id}", response_model=BillingResponse)
async def get_billing(billing_id: str, db: Session = Depends(get_mysql_session)):
    """Get billing record by ID."""
    from .service import BillingService
    billing = BillingService(db).get_billing(billing_id)
    if not billing:
        handle_not_found("Billing", billing_id)
    return billing


@app.get("/billings", response_model=BillingListResponse)
async def search_billings(
    user_id: Optional[str] = None,
    booking_id: Optional[str] = None,
    booking_type: Optional[str] = None,
    payment_status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_mysql_session)
):
    """Search billing records."""
    from .service import BillingService
    
    # If booking_id is provided, get billing directly
    if booking_id:
        billing = BillingService(db).get_billing_by_booking_id(booking_id)
        if billing:
            return BillingListResponse(
                billings=[BillingResponse.model_validate(billing)],
                total_count=1,
                total_amount=billing.total_amount,
                page=1,
                page_size=1
            )
        else:
            return BillingListResponse(
                billings=[],
                total_count=0,
                total_amount=0,
                page=1,
                page_size=1
            )
    
    params = BillingSearchParams(
        user_id=user_id, booking_type=booking_type,
        payment_status=payment_status,
        start_date=start_date, end_date=end_date,
        page=page, page_size=page_size
    )
    return BillingService(db).search_billings(params)


@app.post("/billings/{billing_id}/refund")
async def process_refund(
    billing_id: str,
    refund: RefundRequest,
    db: Session = Depends(get_mysql_session)
):
    """Process a refund."""
    from .service import BillingService
    return BillingService(db).process_refund(billing_id, refund)


@app.post("/billings/{billing_id}/refund/approve")
async def approve_refund(
    billing_id: str,
    refund_request: Optional[RefundApprovalRequest] = None,
    db: Session = Depends(get_mysql_session)
):
    """Approve a pending refund (admin only)."""
    from .service import BillingService
    reason = refund_request.reason if refund_request else None
    return BillingService(db).approve_refund(billing_id, reason)


@app.post("/billings/{billing_id}/refund/reject")
async def reject_refund(
    billing_id: str,
    refund_request: Optional[RefundApprovalRequest] = None,
    db: Session = Depends(get_mysql_session)
):
    """Reject a pending refund (admin only)."""
    from .service import BillingService
    reason = refund_request.reason if refund_request else None
    return BillingService(db).reject_refund(billing_id, reason)


@app.get("/billings/{billing_id}/invoice")
async def get_invoice(billing_id: str, db: Session = Depends(get_mysql_session)):
    """Get invoice details."""
    from .service import BillingService
    return BillingService(db).generate_invoice(billing_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)

