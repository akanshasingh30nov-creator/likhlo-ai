import logging
from typing import Optional
from likhlo_ai.schema import ExtractedTransaction
from likhlo_ai.config import settings

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are LikhLo AI ("Bhaiya, Likh Lo!"), an expert voice-first AI accountant for Indian micro-merchants and small retail shops.
Your task is to parse spoken Indian English, Hindi, or Hinglish voice notes from shopkeepers and extract a 100% accurate, structured financial ledger entry.

Guidelines:
1. Identify TransactionType:
   - CREDIT: Shopkeeper gave goods on credit / udhaar (customer owes money, e.g. 'udhaar diya', 'baki hai', 'likh lo', 'likh lena').
   - CASH_SALE: Immediate cash received for a sale (e.g. 'cash diya', 'turant paisa mila', 'nakad').
   - PAYMENT_RECEIVED: Customer paid back past debt (e.g. 'Sharma ji ne purana 500 jama karaya', 'chukta kiya').
   - DEBIT: Merchant made an expense or bought wholesale stock (e.g. 'mandi mein 2000 kharcha hua').
2. Extract Customer Name with honorifics if present (e.g. 'Sharma ji', 'Ramesh bhaiya').
3. Extract total monetary Amount in INR.
4. Extract individual line items with quantities (e.g. '5kg Atta', '2 packet Milk').
5. Extract promised Due Date or repayment timeline if mentioned (e.g. 'Monday', 'next week', 'kal').
6. Assign confidence score between 0.0 and 1.0.
"""


class LLMParser:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def parse(self, transcript: str) -> Optional[ExtractedTransaction]:
        """Parse transcript using OpenAI Structured Outputs with GPT-4o-mini."""
        if not self.client:
            return None

        try:
            response = self.client.beta.chat.completions.parse(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": f"Parse this voice note: \"{transcript}\""}
                ],
                response_format=ExtractedTransaction,
                timeout=12.0
            )
            parsed = response.choices[0].message.parsed
            if parsed:
                parsed.raw_transcript = transcript
                return parsed
        except Exception as e:
            logger.error(f"OpenAI LLM parsing error: {e}")
            return None

        return None
