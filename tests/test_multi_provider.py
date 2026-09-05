import unittest
from unittest.mock import patch, MagicMock
from likhlo_ai.parser.engine import UnifiedParser
from likhlo_ai.parser.providers.base import clean_json_response, dict_to_extracted_transaction
from likhlo_ai.parser.providers.anthropic_provider import AnthropicProvider
from likhlo_ai.parser.providers.generic_openai_provider import GenericOpenAICompatibleProvider
from likhlo_ai.schema import TransactionType, PaymentStatus
from fastapi.testclient import TestClient
from likhlo_ai.server import app


class TestMultiProviderAI(unittest.TestCase):
    def setUp(self):
        self.parser = UnifiedParser()
        self.client = TestClient(app)

    def test_clean_json_response(self):
        # Raw JSON
        raw = '{"transaction_type": "CREDIT", "amount": 420.0}'
        self.assertEqual(clean_json_response(raw), {"transaction_type": "CREDIT", "amount": 420.0})

        # Markdown fenced JSON
        fenced = '```json\n{"transaction_type": "CASH_SALE", "amount": 500.0}\n```'
        self.assertEqual(clean_json_response(fenced), {"transaction_type": "CASH_SALE", "amount": 500.0})

        # Text with JSON embedded
        mixed = 'Here is the ledger entry:\n{"transaction_type": "DEBIT", "amount": 1200.0}\nThank you.'
        self.assertEqual(clean_json_response(mixed), {"transaction_type": "DEBIT", "amount": 1200.0})

        # Invalid JSON
        self.assertIsNone(clean_json_response("This is not json at all"))

    def test_dict_to_extracted_transaction(self):
        data = {
            "transaction_type": "CREDIT",
            "amount": 280.0,
            "customer": {"name": "Sharma ji", "phone_number": "9876543210"},
            "items": [{"name": "Atta / Wheat Flour", "quantity": "5kg"}],
            "payment_status": "PENDING",
            "due_date": "Monday",
            "notes": "Test credit entry",
            "confidence_score": 0.98,
            "language_detected": "Hinglish"
        }
        extracted = dict_to_extracted_transaction(data, raw_transcript="test transcript")
        self.assertIsNotNone(extracted)
        self.assertEqual(extracted.transaction_type, TransactionType.CREDIT)
        self.assertEqual(extracted.amount, 280.0)
        self.assertEqual(extracted.customer.name, "Sharma ji")
        self.assertEqual(extracted.items[0].name, "Atta / Wheat Flour")
        self.assertEqual(extracted.payment_status, PaymentStatus.PENDING)

    def test_offline_mode_direct_execution(self):
        # Force offline provider
        res = self.parser.parse("Sharma ji ko 500 udhaar diya", provider="offline")
        self.assertEqual(res.transaction_type, TransactionType.CREDIT)
        self.assertEqual(res.amount, 500.0)
        self.assertEqual(res.customer.name, "Sharma ji")

    def test_anthropic_provider_mock_response(self):
        anthropic = AnthropicProvider(api_key="mock-key", model="claude-3-5-haiku-20241022")
        self.assertEqual(anthropic.provider_name, "Anthropic Claude (claude-3-5-haiku-20241022)")

        mock_response_data = {
            "content": [
                {
                    "type": "text",
                    "text": '```json\n{"transaction_type": "CASH_SALE", "amount": 350.0, "customer": {"name": "Amit"}, "items": [{"name": "Sugar", "quantity": "2kg"}]}\n```'
                }
            ]
        }

        with patch("httpx.Client.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response_data)
            parsed = anthropic.parse("Amit paid 350 for 2kg sugar")
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.transaction_type, TransactionType.CASH_SALE)
            self.assertEqual(parsed.amount, 350.0)
            self.assertEqual(parsed.customer.name, "Amit")

    def test_generic_openai_hermes_mock_response(self):
        hermes = GenericOpenAICompatibleProvider(
            base_url="http://localhost:11434/v1",
            api_key="mock",
            model="hermes3"
        )
        self.assertIn("hermes3", hermes.provider_name)

        mock_response_data = {
            "choices": [
                {
                    "message": {
                        "content": '{"transaction_type": "PAYMENT_RECEIVED", "amount": 1000.0, "customer": {"name": "Gupta ji"}}'
                    }
                }
            ]
        }

        with patch("httpx.Client.post") as mock_post:
            mock_post.return_value = MagicMock(status_code=200, json=lambda: mock_response_data)
            parsed = hermes.parse("Gupta ji returned 1000 rupees")
            self.assertIsNotNone(parsed)
            self.assertEqual(parsed.transaction_type, TransactionType.PAYMENT_RECEIVED)
            self.assertEqual(parsed.amount, 1000.0)

    def test_cloud_failure_graceful_fallback_to_heuristics(self):
        # Even if a cloud provider raises an error or times out, it must fall back to the heuristic engine
        with patch.object(self.parser, "get_provider") as mock_get_provider:
            mock_provider = MagicMock()
            mock_provider.parse.side_effect = TimeoutError("Connection to Anthropic timed out")
            mock_provider.provider_name = "Mock Anthropic"
            mock_get_provider.return_value = mock_provider

            result = self.parser.parse("Ramesh ne 500 rupaye cash diya 2 packet tel ke liye")
            self.assertIsNotNone(result)
            self.assertEqual(result.transaction_type, TransactionType.CASH_SALE)
            self.assertEqual(result.amount, 500.0)

    def test_api_parse_text_with_provider_selection(self):
        payload = {
            "transcript": "Sharma ji ko 280 udhaar diya",
            "auto_save": False,
            "provider": "offline"
        }
        res = self.client.post("/api/voice/parse-text", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["transaction_type"], "CREDIT")
        self.assertEqual(data["amount"], 280.0)


if __name__ == "__main__":
    unittest.main()
