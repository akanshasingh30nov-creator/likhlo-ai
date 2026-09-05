from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from likhlo_ai.database import Base
from likhlo_ai.schema import TransactionType, PaymentStatus


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    phone_number = Column(String(20), nullable=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, index=True)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    due_date = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    raw_transcript = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.95)
    language_detected = Column(String(30), default="Hinglish")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    customer = relationship("Customer", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")


class TransactionItem(Base):
    __tablename__ = "transaction_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(36), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    quantity = Column(String(50), nullable=True)
    unit_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)

    transaction = relationship("Transaction", back_populates="items")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
