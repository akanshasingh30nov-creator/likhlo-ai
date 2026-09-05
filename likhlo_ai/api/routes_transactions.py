from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from likhlo_ai.database import get_db
from likhlo_ai.models import Transaction, Customer, AuditLog
from likhlo_ai.schema import (
    TransactionType,
    PaymentStatus,
    ExtractedTransaction,
    CustomerInfo,
    TransactionItem as SchemaItem
)

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("", response_model=List[ExtractedTransaction])
def list_transactions(
    tx_type: Optional[TransactionType] = Query(None, alias="type"),
    status: Optional[PaymentStatus] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List transactions with optional filtering by type and status."""
    query = db.query(Transaction)
    if tx_type:
        query = query.filter(Transaction.transaction_type == tx_type)
    if status:
        query = query.filter(Transaction.payment_status == status)

    records = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()

    results: List[ExtractedTransaction] = []
    for r in records:
        customer_info = None
        if r.customer:
            customer_info = CustomerInfo(
                name=r.customer.name,
                phone_number=r.customer.phone_number,
                notes=r.customer.notes
            )
        items = [
            SchemaItem(
                name=it.name,
                quantity=it.quantity,
                unit_price=it.unit_price,
                total_price=it.total_price
            )
            for it in r.items
        ]
        results.append(
            ExtractedTransaction(
                id=r.id,
                transaction_type=r.transaction_type,
                amount=r.amount,
                customer=customer_info,
                items=items,
                payment_status=r.payment_status,
                due_date=r.due_date,
                notes=r.notes,
                raw_transcript=r.raw_transcript,
                confidence_score=r.confidence_score,
                language_detected=r.language_detected,
                created_at=r.created_at
            )
        )
    return results


@router.patch("/{tx_id}/settle")
def settle_transaction(tx_id: str, db: Session = Depends(get_db)):
    """Mark a pending udhaar credit transaction as settled."""
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    tx.payment_status = PaymentStatus.COMPLETED
    audit = AuditLog(
        event_type="SETTLE_TRANSACTION",
        entity_id=tx.id,
        description=f"Transaction {tx.id} marked as settled"
    )
    db.add(audit)
    db.commit()
    return {"status": "success", "message": "Transaction marked as settled"}


@router.delete("/{tx_id}")
def delete_transaction(tx_id: str, db: Session = Depends(get_db)):
    """Delete a transaction and its line items."""
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(tx)
    audit = AuditLog(
        event_type="DELETE_TRANSACTION",
        entity_id=tx_id,
        description=f"Transaction {tx_id} deleted"
    )
    db.add(audit)
    db.commit()
    return {"status": "success", "message": "Transaction deleted successfully"}
