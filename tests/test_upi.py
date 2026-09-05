import unittest
from likhlo_ai.reminders.upi import generate_upi_link, validate_vpa
from likhlo_ai.reminders.whatsapp import generate_whatsapp_reminder, format_indian_phone


class TestUpiAndReminders(unittest.TestCase):
    def test_vpa_validation(self):
        self.assertTrue(validate_vpa("gupta@okhdfcbank"))
        self.assertTrue(validate_vpa("merchant.shop@paytm"))
        self.assertFalse(validate_vpa("invalidvpa"))
        self.assertFalse(validate_vpa("abc@@bank"))

    def test_upi_link_generation_safe_at(self):
        link = generate_upi_link(
            vpa="sharma@icici",
            merchant_name="Sharma Kirana",
            amount=320.0
        )
        self.assertTrue(link.startswith("upi://pay?"))
        self.assertIn("pa=sharma@icici", link)
        self.assertIn("am=320.00", link)
        self.assertIn("cu=INR", link)

    def test_whatsapp_reminder_tones(self):
        # Polite
        polite_rem = generate_whatsapp_reminder(
            customer_name="Sharma ji",
            phone_number="9876543210",
            amount=280.0,
            merchant_name="Gupta Store",
            tone="polite"
        )
        self.assertIn("Namaste Sharma ji", polite_rem.message_text)
        self.assertIn("https://wa.me/919876543210", polite_rem.whatsapp_deep_link)

        # Formal
        formal_rem = generate_whatsapp_reminder(
            customer_name="Ramesh",
            phone_number="919876543210",
            amount=500.0,
            merchant_name="Gupta Store",
            tone="formal"
        )
        self.assertIn("Hello Ramesh", formal_rem.message_text)

        # Friendly
        friendly_rem = generate_whatsapp_reminder(
            customer_name="Amit",
            phone_number="9876543210",
            amount=150.0,
            merchant_name="Gupta Store",
            tone="friendly"
        )
        self.assertIn("Hi Amit", friendly_rem.message_text)

    def test_phone_sanitization(self):
        self.assertEqual(format_indian_phone("9876543210"), "919876543210")
        self.assertEqual(format_indian_phone("+91 98765-43210"), "919876543210")
        self.assertIsNone(format_indian_phone("12345"))


if __name__ == "__main__":
    unittest.main()
