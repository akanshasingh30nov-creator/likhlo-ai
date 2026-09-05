import unittest
from fastapi.testclient import TestClient
from likhlo_ai.server import app


class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["service"], "LikhLo AI")
        self.assertEqual(data["status"], "healthy")

    def test_parse_text_and_transaction_flow(self):
        payload = {
            "transcript": "Sharma ji ko 5kg atta udhaar diya 280 baki hai somvaar denge",
            "auto_save": True
        }
        res = self.client.post("/api/voice/parse-text", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["transaction_type"], "CREDIT")
        self.assertEqual(data["amount"], 280.0)
        self.assertIsNotNone(data["id"])
        tx_id = data["id"]

        # Verify transaction listed
        res_list = self.client.get("/api/transactions?type=CREDIT")
        self.assertEqual(res_list.status_code, 200)
        items = res_list.json()
        self.assertTrue(len(items) > 0)

        # Settle transaction
        res_settle = self.client.patch(f"/api/transactions/{tx_id}/settle")
        self.assertEqual(res_settle.status_code, 200)

    def test_analytics_summary(self):
        res = self.client.get("/api/analytics/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("cash_in_total", data)
        self.assertIn("net_liquidity", data)

    def test_reminder_generation(self):
        payload = {
            "customer_name": "Ramesh",
            "phone_number": "9876543210",
            "amount": 450.0,
            "tone": "polite"
        }
        res = self.client.post("/api/reminders/generate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("Namaste Ramesh", data["message_text"])
        self.assertIn("upi://pay", data["upi_payment_link"])

    def test_export_csv(self):
        res = self.client.get("/api/export/csv")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.headers.get("content-type", ""))
        self.assertIn("Transaction ID", res.text)


if __name__ == "__main__":
    unittest.main()
