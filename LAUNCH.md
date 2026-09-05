# 🚀 LikhLo AI: 100k Stars Viral Launch Playbook

This document contains copy-paste submission materials to launch **LikhLo AI** across Hacker News, Product Hunt, Twitter/X, and Reddit to drive developer momentum and trend on GitHub.

---

## 1. Hacker News (Show HN)

* **URL to submit:** `https://news.ycombinator.com/submit`
* **Title:** `Show HN: LikhLo AI – Open-source voice khata for 63M Indian merchants (FastAPI, Claude, Hermes)`
* **URL:** `https://github.com/akanshasingh30nov-creator/likhlo-ai`

### Text / First Comment:
```markdown
Hi HN! I built LikhLo AI ("Bhaiya, Likh Lo!"), a voice-first, offline-first digital ledger designed for small neighborhood retail shops (kirana stores).

Over 63 million micro-merchants in India run on credit (udhaar). Existing apps like Khatabook and OkCredit raised hundreds of millions of dollars, but they made a fatal assumption: that shopkeepers have time to tap through 6 smartphone screens to log a transaction while 5 customers are shouting orders.

When things get busy, shopkeepers don't tap screens - they shout "Bhaiya, likh lo!" (Brother, write it down in the ledger).

LikhLo AI solves this with voice-first architecture:
1. Universal Multi-Provider Engine: Runs on Anthropic Claude 3.5 Haiku, local Nous Hermes 3 via Ollama (for 100% private, zero-cost local inference), or OpenAI GPT-4o-mini.
2. Zero-Downtime Fallback: If cloud models timeout or connectivity drops in basement shops, a built-in deterministic heuristic engine parses code-mixed Hindi/Hinglish/English locally with 0ms latency.
3. Automatic Itemization: Captures line items (e.g. "5kg Atta, 2 pkt milk") alongside totals so customers can never dispute "ghost" debt weeks later.
4. Culturally Calibrated WhatsApp Reminders: 3 relationship-preserving tones (Polite, Friendly, Formal) that recover money without ruining neighborhood trust, complete with NPCI-compliant UPI payment links.
5. 100% Offline Persistence: Built on SQLite WAL mode and client LocalStorage. No predatory loan popups, no telemetry tracking.

The project is 100% open-source under the MIT license:
https://github.com/akanshasingh30nov-creator/likhlo-ai

Would love to hear your thoughts, feedback on the dual-engine parser, and pull requests for regional language dictionaries!
```

---

## 2. Product Hunt Launch

* **Name:** LikhLo AI
* **Tagline:** Voice-first AI khata and ledger for 63M+ micro-merchants
* **Topics:** Artificial Intelligence, Developer Tools, Open Source, Fintech
* **Thumbnail:** `assets/dashboard.png`

### Maker Comment:
```text
Hello Product Hunt community! 👋

We are the contributors behind LikhLo AI.

Across India and emerging markets, millions of small neighborhood stores still rely on loose paper chits to track customer credit. Digital ledger apps forced them to type names, search phonebooks, and enter numbers during peak rushes.

We built LikhLo AI to bring voice-first, touchless bookkeeping to micro-merchants:
🎙️ Hands-free 5-second voice notes in Hindi, Hinglish, and English
🧠 Pluggable AI freedom: Claude 3.5 Haiku, local Hermes 3 via Ollama, or built-in offline heuristics
📦 Auto-extracted itemization to prevent debt disputes
💬 Relationship-preserving WhatsApp reminders with 1-click dynamic UPI links
🔒 Local SQLite WAL persistence - no cloud lock-in or ads

It is completely open-source (MIT). Try it out, star the repo, and let us know what you think!
```

---

## 3. Twitter / X Viral Thread

### Tweet 1 (Hook + Video):
```text
63 million Kirana shopkeepers run India’s retail economy.
Yet, almost every digital khata app failed to replace paper books.

Why? Because typing during rush hour is impossible.

I built LikhLo AI: A voice-first, open-source AI Khata copilot.

Here’s how it works 🧵👇
[Attach 30s demo video or assets/dashboard.png]
```

### Tweet 2 (The Voice Engine):
```text
Instead of 6 taps per transaction, merchants just speak:
"Sharma ji ko 5kg atta aur 1 packet surf udhaar diya, 280 baki hai, somvaar denge"

LikhLo AI extracts:
• Customer: Sharma ji
• Items: 5kg Atta, 1 pkt Surf
• Balance: ₹280 (Credit)
• Due Date: Monday
```

### Tweet 3 (Multi-Provider Architecture):
```text
No vendor lock-in. LikhLo AI supports:
🟣 Anthropic Claude 3.5 Haiku
🦙 Nous Hermes 3 / Llama 3 via @ollama (100% private & free on local laptops)
🟢 OpenAI GPT-4o-mini
⚡ 100% Offline Rule Engine with 0ms latency during internet outages
```

### Tweet 4 (WhatsApp & UPI):
```text
Automated debt reminders usually sound like aggressive bank recovery agents, damaging neighborhood trust.

LikhLo AI generates culturally calibrated polite messages with embedded NPCI-compliant UPI links:
"Namaste Sharma ji! 🙏 A gentle reminder from Gupta Store..."
```

### Tweet 5 (Call to Action):
```text
100% open-source under MIT license.
Clean FastAPI backend, SQLite WAL, and responsive dark-mode UI.

Star the repo on GitHub:
👉 https://github.com/akanshasingh30nov-creator/likhlo-ai

Built by the LikhLo AI Open-Source Community
#OpenSource #VoiceAI #Fintech #Claude35 #Hermes #FastAPI
```

---

## 4. Reddit Communities

### Subreddits to Post:
1. **r/Python:** Focus on the FastAPI backend, dual-engine fallback, and SQLite WAL architecture.
2. **r/MachineLearning & r/LocalLLaMA:** Focus on the Ollama Hermes 3 local inference integration for edge devices.
3. **r/developersIndia:** Focus on the real-world Kirana commerce problem, Hinglish acoustic parsing, and open-source contribution opportunities.
4. **r/selfhosted:** Focus on the Docker 1-command deployment and 100% offline data sovereignty.
