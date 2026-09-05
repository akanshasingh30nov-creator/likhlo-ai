# Contributing to LikhLo AI 🎙️

Thank you for your interest in contributing to **LikhLo AI ("Bhaiya, Likh Lo!")**!

LikhLo AI is an open-source, voice-first ledger copilot built to solve real-world billing and credit tracking challenges for **63M+ micro-merchants and kirana store owners**.

We welcome contributions from developers, designers, translators, and fintech enthusiasts worldwide.

---

## 🌟 Areas Where We Need Your Help

1. **Regional Language & Dialect Expansion:**
   - Add new phonetic and keyword dictionaries in `likhlo_ai/parser/heuristic.py` for languages like **Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, and Malayalam**.
   - International translations for emerging markets: **Spanish (Tienditas), Bahasa Indonesia (Warung), and Tagalog (Sari-Sari stores)**.
2. **AI Provider Integrations:**
   - Add new providers in `likhlo_ai/parser/providers/` (e.g. Mistral, DeepSeek, Google Gemini).
3. **Accounting & Hardware Integrations:**
   - TallyPrime / Tally ERP export synchronization.
   - ESC/POS thermal receipt printer support via Web Bluetooth / USB.
4. **Mobile & PWA Improvements:**
   - Progressive Web App (PWA) offline service workers.

---

## 🛠️ Local Development Setup

### 1. Fork and Clone
```bash
git clone https://github.com/<your-username>/likhlo-ai.git
cd likhlo-ai
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### 3. Run Locally
```bash
python -m uvicorn likhlo_ai.server:app --host 127.0.0.1 --port 8000 --reload
```
Open `http://127.0.0.1:8000` in your browser.

---

## 🧪 Running Tests

Always ensure all automated tests pass before submitting a Pull Request:

```bash
python -m unittest discover tests -v
```

All 31+ unit and API tests must pass with zero warnings.

---

## 📐 Pull Request Guidelines

1. **Branch Naming:**
   - `feat/your-feature-name` (for new features)
   - `fix/bug-description` (for bug fixes)
   - `docs/documentation-update` (for README or documentation updates)
2. **Code Style:**
   - Keep code modular, clean, and well-typed.
   - Add tests for any new endpoints, parser rules, or reminder logic.
3. **Commit Messages:**
   - Use standard conventional commits (e.g. `feat: add Tamil number word parser`, `fix: handle edge case in UPI deep link`).

---

## 📜 Code of Conduct

Be kind, respectful, and collaborative. We are building technology to empower real neighborhood shopkeepers and working people. Treat fellow contributors with empathy.
