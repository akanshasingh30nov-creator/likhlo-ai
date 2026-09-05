import unittest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from likhlo_ai.database import Base
from likhlo_ai.models import Customer, Transaction, TransactionItem, AuditLog
from likhlo_ai.schema import TransactionType, PaymentStatus


class TestDatabase(unittest.TestCase):
    def setUp(self):
        # In-memory SQLite for isolated fast unit testing
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_customer_creation(self):
        cust_id = str(uuid.uuid4())
        cust = Customer(id=cust_id, name="Sharma ji", phone_number="9876543210")
        self.db.add(cust)
        self.db.commit()

        retrieved = self.db.query(Customer).filter(Customer.id == cust_id).first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Sharma ji")
        self.assertEqual(retrieved.phone_number, "9876543210")

    def test_transaction_with_items_and_customer(self):
        cust_id = str(uuid.uuid4())
        cust = Customer(id=cust_id, name="Ramesh bhaiya")
        self.db.add(cust)
        self.db.commit()

        tx_id = str(uuid.uuid4())
        tx = Transaction(
            id=tx_id,
            transaction_type=TransactionType.CREDIT,
            amount=420.0,
            payment_status=PaymentStatus.PENDING,
            due_date="Monday",
            raw_transcript="Ramesh bhaiya ko 420 ka samaan diya",
            customer_id=cust_id
        )
        self.db.add(tx)

        item1 = TransactionItem(transaction_id=tx_id, name="Atta / Wheat Flour", quantity="5kg")
        item2 = TransactionItem(transaction_id=tx_id, name="Milk", quantity="2 pkt")
        self.db.add_all([item1, item2])
        self.db.commit()

        # Query and verify
        saved_tx = self.db.query(Transaction).filter(Transaction.id == tx_id).first()
        self.assertIsNotNone(saved_tx)
        self.assertEqual(saved_tx.amount, 420.0)
        self.assertEqual(saved_tx.customer.name, "Ramesh bhaiya")
        self.assertEqual(len(saved_tx.items), 2)

    def test_settle_transaction(self):
        tx_id = str(uuid.uuid4())
        tx = Transaction(
            id=tx_id,
            transaction_type=TransactionType.CREDIT,
            amount=250.0,
            payment_status=PaymentStatus.PENDING,
            raw_transcript="test"
        )
        self.db.add(tx)
        self.db.commit()

        # Settle
        tx.payment_status = PaymentStatus.COMPLETED
        audit = AuditLog(event_type="SETTLE", entity_id=tx_id, description="Paid in full")
        self.db.add(audit)
        self.db.commit()

        refreshed = self.db.query(Transaction).filter(Transaction.id == tx_id).first()
        self.assertEqual(refreshed.payment_status, PaymentStatus.COMPLETED)
        audit_record = self.db.query(AuditLog).filter(AuditLog.entity_id == tx_id).first()
        self.assertIsNotNone(audit_record)


if __name__ == "__main__":
    unittest.main()
