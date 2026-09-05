import csv
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from likhlo_ai.database import get_db
from likhlo_ai.models import Transaction

router = APIRouter(prefix="/api/export", tags=["Export & Backup"])


@router.get("/csv")
def export_ledger_csv(db: Session = Depends(get_db)):
    """Export complete ledger as a CSV file for spreadsheets and tax accountants."""
    transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Transaction ID",
        "Timestamp (UTC)",
        "Type",
        "Customer Name",
        "Customer Phone",
        "Amount (INR)",
        "Items Summary",
        "Payment Status",
        "Due Date",
        "Voice Transcript"
    ])

    for tx in transactions:
        cust_name = tx.customer.name if tx.customer else "N/A"
        cust_phone = tx.customer.phone_number if tx.customer and tx.customer.phone_number else ""
        items_str = ", ".join([f"{it.quantity or ''} {it.name}".strip() for it in tx.items])

        writer.writerow([
            tx.id,
            tx.created_at.strftime("%Y-%m-%d %H:%M:%S") if tx.created_at else "",
            tx.transaction_type.value,
            cust_name,
            cust_phone,
            f"{tx.amount:.2f}",
            items_str,
            tx.payment_status.value,
            tx.due_date or "",
            tx.raw_transcript
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=likhlo_khata_export.csv"}
    )
