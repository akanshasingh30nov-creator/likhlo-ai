import unittest
from likhlo_ai.parser.heuristic import parse_spoken_text_heuristically
from likhlo_ai.schema import TransactionType, PaymentStatus


class TestHeuristicParser(unittest.TestCase):
    def test_credit_atta_milk(self):
        tx = parse_spoken_text_heuristically("Sharma ji ko 5kg atta aur 2 packet doodh udhaar diya 280 baki hai somvaar denge")
        self.assertEqual(tx.transaction_type, TransactionType.CREDIT)
        self.assertEqual(tx.amount, 280.0)
        self.assertIn("Sharma", tx.customer.name)
        self.assertEqual(tx.due_date, "Monday")
        self.assertEqual(tx.payment_status, PaymentStatus.PENDING)

    def test_cash_sale_oil(self):
        tx = parse_spoken_text_heuristically("Ramesh ne 500 rupaye cash diya 2 packet tel ke liye")
        self.assertEqual(tx.transaction_type, TransactionType.CASH_SALE)
        self.assertEqual(tx.amount, 500.0)
        self.assertEqual(tx.payment_status, PaymentStatus.COMPLETED)

    def test_repayment_vasooli(self):
        tx = parse_spoken_text_heuristically("Gupta ji ne purana 1200 rupaye jama karaya hisab clear")
        self.assertEqual(tx.transaction_type, TransactionType.PAYMENT_RECEIVED)
        self.assertEqual(tx.amount, 1200.0)
        self.assertEqual(tx.payment_status, PaymentStatus.COMPLETED)

    def test_debit_wholesale_mandi(self):
        tx = parse_spoken_text_heuristically("Mandi mein 2500 rupaye kharcha hua wholesale dal ke liye")
        self.assertEqual(tx.transaction_type, TransactionType.DEBIT)
        self.assertEqual(tx.amount, 2500.0)
        self.assertEqual(tx.payment_status, PaymentStatus.COMPLETED)

    def test_english_credit_phrase(self):
        tx = parse_spoken_text_heuristically("Credit note for Suresh uncle 350 rs for sugar and biscuits will pay tomorrow")
        self.assertEqual(tx.transaction_type, TransactionType.CREDIT)
        self.assertEqual(tx.amount, 350.0)
        self.assertIn("Suresh", tx.customer.name)
        self.assertEqual(tx.due_date, "Tomorrow")

    def test_word_numbers_hazar(self):
        tx = parse_spoken_text_heuristically("Verma ji ko ek hazar udhaar diya")
        self.assertEqual(tx.amount, 1000.0)
        self.assertEqual(tx.transaction_type, TransactionType.CREDIT)

    def test_item_detection_ghee_tea(self):
        tx = parse_spoken_text_heuristically("Amit bhai 1kg ghee aur chai patti 450 rs cash")
        item_names = [it.name for it in tx.items]
        self.assertTrue(any("Ghee" in n for n in item_names))
        self.assertTrue(any("Tea" in n for n in item_names))
        self.assertEqual(tx.amount, 450.0)
        self.assertEqual(tx.transaction_type, TransactionType.CASH_SALE)


if __name__ == "__main__":
    unittest.main()
