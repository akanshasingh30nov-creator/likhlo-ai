import re
import urllib.parse
from typing import Optional
from likhlo_ai.schema import WhatsAppReminder
from likhlo_ai.reminders.upi import generate_upi_link


def format_indian_phone(phone: Optional[str]) -> Optional[str]:
    """Sanitize and format phone number for WhatsApp deep links."""
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        return f"91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return digits
    return digits if len(digits) >= 10 else None


def generate_whatsapp_reminder(
    customer_name: str,
    phone_number: Optional[str],
    amount: float,
    merchant_name: str = "Apka Kirana Store",
    merchant_upi_id: str = "merchant@okhdfcbank",
    tone: str = "polite",
    items_summary: Optional[str] = None
) -> WhatsAppReminder:
    """Generate culturally calibrated, non-confrontational WhatsApp reminders."""
    upi_link = generate_upi_link(merchant_upi_id, merchant_name, amount)
    item_clause = f" ({items_summary})" if items_summary else ""

    clean_customer = customer_name.strip() or "Customer"
    clean_merchant = merchant_name.strip() or "Our Store"

    # Avoid duplicate honorifics (e.g. avoid 'Sharma ji ji')
    name_lower = clean_customer.lower().strip()
    has_honorific = any(
        name_lower.endswith(h)
        for h in [" ji", "ji", " bhai", "bhai", " bhaiya", "bhaiya", " sahab", "sahab", " sir", "sir", " chacha", " uncle"]
    )
    polite_name = clean_customer if has_honorific else f"{clean_customer} ji"

    if tone == "friendly":
        message = (
            f"Hi {clean_customer}! Hope you are doing well.\n\n"
            f"Just reviewing our weekly khata at {clean_merchant}. "
            f"Rs {amount:.0f}{item_clause} is remaining. "
            f"You can settle it anytime via UPI:\n{upi_link}\n\n"
            f"Dhanyawad!"
        )
    elif tone == "formal":
        message = (
            f"Hello {clean_customer},\n\n"
            f"This is an automated ledger statement from {clean_merchant}.\n"
            f"Pending Balance: Rs {amount:.0f}{item_clause}\n\n"
            f"Please settle via UPI:\n{upi_link}\n\n"
            f"Thank you."
        )
    else:  # polite (default)
        message = (
            f"Namaste {polite_name}! 🙏\n\n"
            f"A gentle reminder from {clean_merchant}. Your balance of Rs {amount:.0f}{item_clause} "
            f"is pending in our khata.\n\n"
            f"You can easily clear it using UPI:\n"
            f"{upi_link}\n\n"
            f"Thank you for your trust and business! Have a wonderful day."
        )

    encoded_text = urllib.parse.quote(message)
    formatted_phone = format_indian_phone(phone_number)

    if formatted_phone:
        wa_link = f"https://wa.me/{formatted_phone}?text={encoded_text}"
    else:
        wa_link = f"https://wa.me/?text={encoded_text}"

    return WhatsAppReminder(
        customer_name=clean_customer,
        phone_number=phone_number,
        amount_due=amount,
        message_text=message,
        upi_payment_link=upi_link,
        whatsapp_deep_link=wa_link
    )
