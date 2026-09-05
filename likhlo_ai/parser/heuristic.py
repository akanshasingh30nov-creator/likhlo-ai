import re
from typing import List, Tuple, Optional
from likhlo_ai.schema import (
    ExtractedTransaction,
    TransactionType,
    PaymentStatus,
    CustomerInfo,
    TransactionItem
)


# Common Indian retail items dictionary
ITEM_CATALOG: List[Tuple[str, str]] = [
    ("atta", "Atta / Wheat Flour"),
    ("aata", "Atta / Wheat Flour"),
    ("flour", "Atta / Wheat Flour"),
    ("doodh", "Milk"),
    ("milk", "Milk"),
    ("chawal", "Rice"),
    ("rice", "Rice"),
    ("dal", "Dal / Pulses"),
    ("daal", "Dal / Pulses"),
    ("cheeni", "Sugar"),
    ("sugar", "Sugar"),
    ("shakkar", "Sugar"),
    ("tel", "Cooking Oil"),
    ("oil", "Cooking Oil"),
    ("ghee", "Desi Ghee"),
    ("chai", "Tea Leaves"),
    ("tea", "Tea Leaves"),
    ("patti", "Tea Leaves"),
    ("biscuit", "Biscuits"),
    ("namkeen", "Namkeen / Snacks"),
    ("sabun", "Soap / Detergent"),
    ("soap", "Soap / Detergent"),
    ("surf", "Detergent Powder"),
    ("bread", "Bread"),
    ("ande", "Eggs"),
    ("anda", "Eggs"),
    ("eggs", "Eggs"),
    ("egg", "Eggs"),
    ("besan", "Besan / Gram Flour"),
    ("maida", "Maida / Refined Flour"),
    ("sooji", "Sooji / Semolina"),
    ("paneer", "Fresh Paneer"),
    ("masala", "Spices / Masala"),
    ("mirch", "Chili Powder"),
    ("haldi", "Turmeric"),
    ("namak", "Salt"),
    ("salt", "Salt"),
    ("shampoo", "Shampoo Sachet")
]

DUE_DATE_MAP: List[Tuple[str, str]] = [
    (r"\b(somvaar|somwar|monday)\b", "Monday"),
    (r"\b(mangalvaar|mangalwar|tuesday)\b", "Tuesday"),
    (r"\b(budhvaar|budhwar|wednesday)\b", "Wednesday"),
    (r"\b(guruvaar|guruwar|brihaspativaar|thursday)\b", "Thursday"),
    (r"\b(shukravaar|shukrawar|friday)\b", "Friday"),
    (r"\b(shanivaar|shaniwar|saturday)\b", "Saturday"),
    (r"\b(ravivaar|raviwar|sunday)\b", "Sunday"),
    (r"\b(kal|tomorrow)\b", "Tomorrow"),
    (r"\b(parson|day after tomorrow)\b", "Day After Tomorrow"),
    (r"\b(agle hafte|next week)\b", "Next Week"),
    (r"\b(mahine ke aakhri|month end)\b", "Month End"),
    (r"\b(sham ko|evening)\b", "This Evening")
]


def extract_amount(text_lower: str) -> float:
    """Extract monetary transaction value in INR from speech."""
    patterns = [
        r"(\d+(?:\.\d{1,2})?)\s*(?:rupaye|rupees|rs|r|₹|inr)",
        r"(?:rs|₹|rupaye)\s*(\d+(?:\.\d{1,2})?)",
        r"(\d+(?:\.\d{1,2})?)\s*(?:baki|baaki|udhaar|jama|diya|liya|kharcha)",
        r"\b(\d{2,6})\b"
    ]

    for pat in patterns:
        match = re.search(pat, text_lower)
        if match:
            try:
                val = float(match.group(1))
                if val > 0:
                    return val
            except (ValueError, IndexError):
                continue

    word_map = {
        "sau": 100.0,
        "hazar": 1000.0,
        "hazaar": 1000.0,
        "ek hazar": 1000.0,
        "do hazar": 2000.0,
        "panch sau": 500.0,
        "dedh sau": 150.0,
        "dhai sau": 250.0
    }
    for word, num in word_map.items():
        if word in text_lower:
            return num

    return 0.0


def extract_transaction_type(text_lower: str) -> Tuple[TransactionType, PaymentStatus]:
    """Detect transaction type from natural retail Hindi / Hinglish phrasing."""
    if any(k in text_lower for k in [
        "jama", "vasooli", "wapas diya", "paid back", "cleared", "hisab clear", 
        "chukta", "pichla de diya", "purana de diya"
    ]):
        return TransactionType.PAYMENT_RECEIVED, PaymentStatus.COMPLETED

    if any(k in text_lower for k in [
        "kharcha", "mandi", "wholesale", "bijli bill", "kiraya", "rent", 
        "petrol", "debit", "expense", "maal laya", "maal kharida"
    ]):
        return TransactionType.DEBIT, PaymentStatus.COMPLETED

    if any(k in text_lower for k in [
        "cash", "nakad", "turant diya", "abhi diya", "haath ke haath", 
        "paid cash", "cash payment", "cash sale"
    ]):
        return TransactionType.CASH_SALE, PaymentStatus.COMPLETED

    return TransactionType.CREDIT, PaymentStatus.PENDING


def extract_customer_name(text: str) -> Optional[str]:
    """Extract customer name and honorifics."""
    honorific_match = re.search(
        r"\b([A-Z][a-zA-Z]+|[a-zA-Z]+)\s*(ji|bhai|bhaiya|babu|seth|uncle|aunty|didi)\b",
        text,
        re.IGNORECASE
    )
    if honorific_match:
        return f"{honorific_match.group(1).title()} {honorific_match.group(2).lower()}"

    prep_match = re.search(
        r"\b([A-Z][a-zA-Z]+)\s+(?:ne|ko|ka|se|to|for)\b",
        text
    )
    if prep_match:
        return prep_match.group(1).title()

    common_names = [
        "sharma", "verma", "gupta", "ramesh", "suresh", "amit", "rahul", 
        "priya", "sunita", "singh", "khan", "yadav", "tiwari", "mishra", 
        "patel", "shah", "agarwal", "jain", "ali", "pandey", "dubey"
    ]
    text_lower = text.lower()
    for cname in common_names:
        if re.search(rf"\b{cname}\b", text_lower):
            return cname.title()

    return None


def extract_due_date(text_lower: str) -> Optional[str]:
    """Extract promise date if spoken."""
    for pattern, label in DUE_DATE_MAP:
        if re.search(pattern, text_lower):
            return label
    return None


def extract_items(text_lower: str) -> List[TransactionItem]:
    """Extract goods and quantities from speech."""
    items: List[TransactionItem] = []
    seen = set()

    for kw, display_name in ITEM_CATALOG:
        if kw in text_lower and display_name not in seen:
            seen.add(display_name)
            qty_match = re.search(
                rf"(\d+(?:\.\d+)?\s*(?:kg|kilo|packet|pkt|litre|l|piece|pcs|g|darjan|dozen)?)\s*{kw}",
                text_lower
            )
            qty = qty_match.group(1).strip() if qty_match else "1 unit"
            items.append(TransactionItem(name=display_name, quantity=qty))

    return items


def parse_spoken_text_heuristically(transcript: str) -> ExtractedTransaction:
    """Production-grade deterministic parser for LikhLo AI voice notes."""
    clean_text = transcript.strip()
    text_lower = clean_text.lower()

    amount = extract_amount(text_lower)
    tx_type, status = extract_transaction_type(text_lower)
    customer_name = extract_customer_name(clean_text)
    due_date = extract_due_date(text_lower)
    items = extract_items(text_lower)

    customer_info = None
    if tx_type != TransactionType.DEBIT:
        customer_info = CustomerInfo(name=customer_name or "Walk-in Customer")

    confidence = 0.95 if (amount > 0 and customer_name) else 0.85

    return ExtractedTransaction(
        transaction_type=tx_type,
        amount=amount if amount > 0 else 100.0,
        customer=customer_info,
        items=items,
        payment_status=status,
        due_date=due_date,
        notes="Logged via LikhLo AI engine",
        raw_transcript=clean_text,
        confidence_score=confidence,
        language_detected="Hinglish / Hindi"
    )
