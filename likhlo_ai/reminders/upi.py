import re
import urllib.parse
from typing import Optional


def validate_vpa(vpa: str) -> bool:
    """Validate Indian Virtual Payment Address (VPA) format."""
    clean_vpa = vpa.strip()
    pattern = r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$"
    return bool(re.match(pattern, clean_vpa))


def generate_upi_link(
    vpa: str,
    merchant_name: str,
    amount: float,
    transaction_note: Optional[str] = "LikhLo AI Khata Settlement"
) -> str:
    """Generate official NPCI UPI payment deep-link.
    
    Format: upi://pay?pa=<vpa>&pn=<name>&am=<amount>&cu=INR&tn=<note>
    """
    clean_vpa = vpa.strip()
    if not validate_vpa(clean_vpa):
        clean_vpa = "merchant@upi"

    params = {
        "pa": clean_vpa,
        "pn": merchant_name.strip() or "Merchant",
        "am": f"{max(amount, 1.0):.2f}",
        "cu": "INR",
        "tn": transaction_note or "Khata Settlement"
    }

    query_string = urllib.parse.urlencode(params, safe="@")
    return f"upi://pay?{query_string}"
