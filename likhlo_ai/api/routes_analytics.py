from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from likhlo_ai.database import get_db
from likhlo_ai.models import Transaction, Customer
from likhlo_ai.schema import TransactionType, PaymentStatus

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


class FinancialSummary(BaseModel):
    cash_in_total: float
    cash_in_count: int
    pending_udhaar_total: float
    pending_debtors_count: int
    cash_out_total: float
    cash_out_count: int
    net_liquidity: float
    total_transactions_count: int


class DebtorSummary(BaseModel):
    customer_name: str
    phone_number: Optional[str] = None
    total_pending_amount: float
    unpaid_transactions_count: int


@router.get("/summary", response_model=FinancialSummary)
def get_financial_summary(db: Session = Depends(get_db)):
    """Calculate daily and cumulative financial health metrics."""
    transactions = db.query(Transaction).all()

    cash_in = 0.0
    cash_in_count = 0
    pending_udhaar = 0.0
    cash_out = 0.0
    cash_out_count = 0

    pending_debtors = set()

    for tx in transactions:
        if tx.transaction_type == TransactionType.CASH_SALE:
            cash_in += tx.amount
            cash_in_count += 1
        elif tx.transaction_type == TransactionType.PAYMENT_RECEIVED:
            cash_in += tx.amount
            cash_in_count += 1
        elif tx.transaction_type == TransactionType.CREDIT:
            if tx.payment_status == PaymentStatus.PENDING:
                pending_udhaar += tx.amount
                if tx.customer_id:
                    pending_debtors.add(tx.customer_id)
                elif tx.customer and tx.customer.name:
                    pending_debtors.add(tx.customer.name)
        elif tx.transaction_type == TransactionType.DEBIT:
            cash_out += tx.amount
            cash_out_count += 1

    return FinancialSummary(
        cash_in_total=cash_in,
        cash_in_count=cash_in_count,
        pending_udhaar_total=pending_udhaar,
        pending_debtors_count=len(pending_debtors),
        cash_out_total=cash_out,
        cash_out_count=cash_out_count,
        net_liquidity=cash_in - cash_out,
        total_transactions_count=len(transactions)
    )


@router.get("/top-debtors", response_model=List[DebtorSummary])
def get_top_debtors(limit: int = 10, db: Session = Depends(get_db)):
    """Retrieve top customers with highest outstanding udhaar."""
    results = (
        db.query(
            Customer.name,
            Customer.phone_number,
            func.sum(Transaction.amount).label("total_debt"),
            func.count(Transaction.id).label("tx_count")
        )
        .join(Transaction, Transaction.customer_id == Customer.id)
        .filter(Transaction.transaction_type == TransactionType.CREDIT)
        .filter(Transaction.payment_status == PaymentStatus.PENDING)
        .group_by(Customer.id)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(limit)
        .all()
    )

    return [
        DebtorSummary(
            customer_name=r[0],
            phone_number=r[1],
            total_pending_amount=float(r[2]),
            unpaid_transactions_count=int(r[3])
        )
        for r in results
    ]
