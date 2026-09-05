import unittest
import tempfile
import os
from fastapi.testclient import TestClient
from likhlo_ai.server import app
from likhlo_ai.parser.engine import UnifiedParser
from likhlo_ai.voice.audio_utils import validate_audio_file


class TestEdgeCases(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.parser = UnifiedParser()

    def test_empty_transcript_handling(self):
        with self.assertRaises(ValueError):
            self.parser.parse("")

        res = self.client.post("/api/voice/parse-text", json={"transcript": "   ", "auto_save": False})
        self.assertEqual(res.status_code, 400)

    def test_sql_injection_attempt_in_customer_name(self):
        malicious_input = "Sharma'; DROP TABLE transactions; -- ko 500 udhaar diya"
        res = self.client.post("/api/voice/parse-text", json={"transcript": malicious_input, "auto_save": True})
        self.assertEqual(res.status_code, 200)
        
        # Verify table still exists and query succeeds
        res_list = self.client.get("/api/transactions")
        self.assertEqual(res_list.status_code, 200)

    def test_zero_byte_audio_file(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as empty_file:
            empty_path = empty_file.name

        try:
            with self.assertRaises(ValueError):
                validate_audio_file(empty_path)
        finally:
            if os.path.exists(empty_path):
                os.remove(empty_path)

    def test_unsupported_audio_format(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as txt_file:
            txt_file.write(b"dummy audio text")
            txt_path = txt_file.name

        try:
            with self.assertRaises(ValueError):
                validate_audio_file(txt_path)
        finally:
            if os.path.exists(txt_path):
                os.remove(txt_path)

    def test_nonexistent_transaction_settlement(self):
        res = self.client.patch("/api/transactions/nonexistent-uuid-123/settle")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
