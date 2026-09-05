import os
import uuid
import shutil
import tempfile
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from likhlo_ai.database import get_db
from likhlo_ai.models import Transaction, TransactionItem, Customer, AuditLog
from likhlo_ai.schema import ExtractedTransaction
from likhlo_ai.parser.engine import UnifiedParser
from likhlo_ai.voice.transcriber import WhisperTranscriber

router = APIRouter(prefix="/api/voice", tags=["Voice Engine"])
parser = UnifiedParser()
transcriber = WhisperTranscriber()


class ParseTextPayload(BaseModel):
    transcript: str
    auto_save: bool = True
    provider: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: Optional[str] = None


def save_extracted_to_db(extracted: ExtractedTransaction, db: Session) -> str:
    """Persist extracted transaction into SQLite database."""
    customer_id = None
    if extracted.customer and extracted.customer.name:
        existing_cust = db.query(Customer).filter(Customer.name == extracted.customer.name).first()
        if existing_cust:
            customer_id = existing_cust.id
        else:
            customer_id = str(uuid.uuid4())
            new_cust = Customer(
                id=customer_id,
                name=extracted.customer.name,
                phone_number=extracted.customer.phone_number,
                notes=extracted.customer.notes
            )
            db.add(new_cust)
            db.flush()

    tx_id = str(uuid.uuid4())
    new_tx = Transaction(
        id=tx_id,
        transaction_type=extracted.transaction_type,
        amount=extracted.amount,
        payment_status=extracted.payment_status,
        due_date=extracted.due_date,
        notes=extracted.notes,
        raw_transcript=extracted.raw_transcript,
        confidence_score=extracted.confidence_score,
        language_detected=extracted.language_detected,
        customer_id=customer_id,
        created_at=extracted.created_at
    )
    db.add(new_tx)

    for item in extracted.items:
        new_item = TransactionItem(
            transaction_id=tx_id,
            name=item.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price
        )
        db.add(new_item)

    audit = AuditLog(
        event_type="VOICE_INGEST",
        entity_id=tx_id,
        description=f"Logged via voice: {extracted.transaction_type.value} of Rs {extracted.amount}"
    )
    db.add(audit)
    db.commit()

    extracted.id = tx_id
    return tx_id


@router.post("/parse-text", response_model=ExtractedTransaction)
def parse_spoken_text(payload: ParseTextPayload, db: Session = Depends(get_db)):
    """Parse text and record in LikhLo AI khata."""
    text = payload.transcript.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty")

    extracted = parser.parse(
        text,
        provider=payload.provider,
        api_key=payload.api_key,
        api_base=payload.api_base,
        model=payload.model
    )
    if payload.auto_save:
        save_extracted_to_db(extracted, db)

    return extracted


@router.post("/parse-audio", response_model=ExtractedTransaction)
async def parse_spoken_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Transcribe audio with Whisper and record transaction in LikhLo AI."""
    suffix = os.path.splitext(file.filename or "audio.wav")[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        transcript = transcriber.transcribe(tmp_path)
        extracted = parser.parse(transcript)
        save_extracted_to_db(extracted, db)
        return extracted
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
