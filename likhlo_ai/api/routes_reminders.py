from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from likhlo_ai.schema import WhatsAppReminder
from likhlo_ai.reminders.whatsapp import generate_whatsapp_reminder
from likhlo_ai.config import settings

router = APIRouter(prefix="/api/reminders", tags=["Reminders & UPI"])


class ReminderRequest(BaseModel):
    customer_name: str
    phone_number: Optional[str] = None
    amount: float
    merchant_name: Optional[str] = None
    merchant_upi_id: Optional[str] = None
    tone: Optional[str] = "polite"
    items_summary: Optional[str] = None


@router.post("/generate", response_model=WhatsAppReminder)
def generate_reminder_endpoint(req: ReminderRequest):
    """Generate culturally calibrated WhatsApp reminder with dynamic UPI link."""
    return generate_whatsapp_reminder(
        customer_name=req.customer_name,
        phone_number=req.phone_number,
        amount=req.amount,
        merchant_name=req.merchant_name or settings.default_merchant_name,
        merchant_upi_id=req.merchant_upi_id or settings.default_merchant_upi,
        tone=req.tone or "polite",
        items_summary=req.items_summary
    )
