from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    CREDIT = "CREDIT"  # Udhaar diya (Customer owes merchant)
    DEBIT = "DEBIT"    # Expense / Stock bought (Merchant paid)
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"  # Udhaar vasooli (Customer paid back)
    CASH_SALE = "CASH_SALE"  # Direct cash sale


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"


class TransactionItem(BaseModel):
    name: str = Field(description="Name of item or service (e.g. Atta, Milk, Cooking Oil)")
    quantity: Optional[str] = Field(default=None, description="Quantity with unit (e.g. 5kg, 2 packets, 1 litre)")
    unit_price: Optional[float] = Field(default=None, description="Price per unit in INR")
    total_price: Optional[float] = Field(default=None, description="Total price for this line item in INR")


class CustomerInfo(BaseModel):
    name: str = Field(description="Customer name or honorific identity (e.g. Sharma ji, Ramesh bhaiya)")
    phone_number: Optional[str] = Field(default=None, description="Phone number if mentioned or found")
    notes: Optional[str] = Field(default=None, description="Contextual note (e.g. 'temple lane', 'driver')")


class ExtractedTransaction(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique transaction ID")
    transaction_type: TransactionType = Field(
        description="Whether this is credit (udhaar), cash sale, repayment, or debit"
    )
    amount: float = Field(description="Primary monetary value in INR (rupees)")
    customer: Optional[CustomerInfo] = Field(default=None, description="Customer details if relevant")
    items: List[TransactionItem] = Field(default_factory=list, description="Itemized goods or services")
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Status of payment")
    due_date: Optional[str] = Field(default=None, description="Promised due date or timeline (e.g. 'Monday', 'Kal')")
    notes: Optional[str] = Field(default=None, description="Additional context or notes")
    raw_transcript: str = Field(description="Spoken voice input transcribed from audio")
    confidence_score: float = Field(default=0.95, description="Confidence score between 0.0 and 1.0")
    language_detected: str = Field(default="Hinglish / Hindi", description="Language detected from audio")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WhatsAppReminder(BaseModel):
    customer_name: str
    phone_number: Optional[str]
    amount_due: float
    message_text: str
    upi_payment_link: str
    whatsapp_deep_link: str
