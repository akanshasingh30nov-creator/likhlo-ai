import re
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from likhlo_ai.schema import ExtractedTransaction, TransactionType, PaymentStatus, CustomerInfo, TransactionItem

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are LikhLo AI ("Bhaiya, Likh Lo!"), an expert voice-first AI accountant for Indian micro-merchants and small retail shops.
Your task is to parse spoken Indian English, Hindi, or Hinglish voice notes from shopkeepers and extract a 100% accurate, structured financial ledger entry.

Guidelines:
1. Identify TransactionType:
   - CREDIT: Shopkeeper gave goods on credit / udhaar (customer owes money, e.g. 'udhaar diya', 'baki hai', 'likh lo', 'likh lena').
   - CASH_SALE: Immediate cash received for a sale (e.g. 'cash diya', 'turant paisa mila', 'nakad').
   - PAYMENT_RECEIVED: Customer paid back past debt (e.g. 'Sharma ji ne purana 500 jama karaya', 'chukta kiya', 'vasooli').
   - DEBIT: Merchant made an expense or bought wholesale stock (e.g. 'mandi mein 2000 kharcha hua').
2. Extract Customer Name with honorifics if present (e.g. 'Sharma ji', 'Ramesh bhaiya', 'Gupta ji').
3. Extract total monetary Amount in INR.
4. Extract individual line items with quantities (e.g. '5kg Atta', '2 packet Milk').
5. Extract promised Due Date or repayment timeline if mentioned (e.g. 'Monday', 'next week', 'somvaar').
6. Assign confidence score between 0.0 and 1.0.

Return strictly valid JSON matching this schema:
{
  "transaction_type": "CREDIT" | "CASH_SALE" | "PAYMENT_RECEIVED" | "DEBIT",
  "amount": number,
  "customer": {"name": string, "phone_number": string | null, "notes": string | null} | null,
  "items": [{"name": string, "quantity": string | null, "unit_price": number | null, "total_price": number | null}],
  "payment_status": "PENDING" | "COMPLETED",
  "due_date": string | null,
  "notes": string | null,
  "confidence_score": number,
  "language_detected": string
}
"""


def clean_json_response(raw_text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse JSON from raw model output, handling markdown blocks."""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    
    try:
        return json.loads(text)
    except Exception as e:
        # Fallback: search for first { and last }
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            try:
                return json.loads(text[first_brace:last_brace + 1])
            except Exception:
                pass
        logger.warning(f"Failed to parse JSON from response: {e}")
        return None


def dict_to_extracted_transaction(data: Dict[str, Any], raw_transcript: str) -> Optional[ExtractedTransaction]:
    """Convert raw dictionary into validated ExtractedTransaction model."""
    try:
        tx_type_raw = str(data.get("transaction_type", "CASH_SALE")).upper()
        try:
            tx_type = TransactionType(tx_type_raw)
        except ValueError:
            tx_type = TransactionType.CASH_SALE

        status_raw = str(data.get("payment_status", "COMPLETED")).upper()
        try:
            status = PaymentStatus(status_raw)
        except ValueError:
            status = PaymentStatus.PENDING if tx_type == TransactionType.CREDIT else PaymentStatus.COMPLETED

        customer = None
        cust_data = data.get("customer")
        if cust_data and isinstance(cust_data, dict) and cust_data.get("name"):
            customer = CustomerInfo(
                name=str(cust_data["name"]).strip(),
                phone_number=cust_data.get("phone_number"),
                notes=cust_data.get("notes")
            )

        items = []
        items_data = data.get("items", [])
        if isinstance(items_data, list):
            for it in items_data:
                if isinstance(it, dict) and it.get("name"):
                    items.append(TransactionItem(
                        name=str(it["name"]).strip(),
                        quantity=it.get("quantity"),
                        unit_price=it.get("unit_price"),
                        total_price=it.get("total_price")
                    ))

        return ExtractedTransaction(
            transaction_type=tx_type,
            amount=float(data.get("amount", 0.0)),
            customer=customer,
            items=items,
            payment_status=status,
            due_date=data.get("due_date"),
            notes=data.get("notes", "Parsed via Universal AI Provider"),
            raw_transcript=raw_transcript,
            confidence_score=float(data.get("confidence_score", 0.95)),
            language_detected=data.get("language_detected", "Hinglish")
        )
    except Exception as e:
        logger.error(f"Error validating ExtractedTransaction from provider: {e}")
        return None


class BaseLLMProvider(ABC):
    """Abstract interface for all AI models (Claude, Hermes, OpenAI, Ollama)."""

    @abstractmethod
    def parse(self, transcript: str) -> Optional[ExtractedTransaction]:
        """Parse natural language transcript into an ExtractedTransaction."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier."""
        pass
