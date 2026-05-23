# Closira AI Support Workflow — Bloom Aesthetics Clinic

A Python-based AI customer support workflow built for the Closira internship assignment. Handles inbound customer enquiries using SOP-grounded responses, lead qualification, escalation detection, and conversation summarisation.

---

## Features

- **Stage 1 — FAQ Answering:** Answers customer questions strictly from SOP data. Never halluccinates.
- **Stage 2 — Lead Qualification:** Naturally collects treatment interest, experience, and booking timeframe.
- **Stage 3 — Escalation Detection:** Detects complaints, medical questions, pricing negotiation, out-of-scope questions, and human requests. Logs all escalations to `escalation_log.json`.
- **Stage 4 — Conversation Summary:** Generates a structured summary when the session ends.

---

## Setup

### Prerequisites

- Python 3.9+
- An Anthropic API key ([get one here](https://console.anthropic.com))

### Installation

```bash
# Clone the repo
git clone <your-repo-url>
cd closira

# Install dependencies
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY=your_api_key_here   # Mac/Linux
set ANTHROPIC_API_KEY=your_api_key_here      # Windows
```

### Run the workflow

```bash
python workflow.py
```

---

## Project Structure

```
closira/
├── workflow.py           # Main AI workflow (4 stages)
├── sop_data.json         # SOP source of truth (Bloom Aesthetics Clinic)
├── prompt_design.md      # System prompt + design decisions
├── escalation_log.json   # Auto-generated escalation log
├── README.md             # This file
└── test_transcripts/
    ├── 01_in_sop_question.md
    ├── 02_out_of_scope.md
    ├── 03_escalation_complaint.md
    ├── 04_lead_qualification.md
    └── 05_full_conversation_summary.md
```

---

## How It Works

### Conversation Flow

```
Customer message
      │
      ▼
Claude API (system prompt + SOP + history)
      │
      ├─ [ESCALATE: reason] detected? ──► Log to escalation_log.json
      │                                   Inform customer + request handoff
      │
      ├─ Session end trigger? ──────────► Generate structured summary
      │
      └─ Normal response ───────────────► Display to customer
                                          Track lead qualification data
```

### Escalation Triggers

| Trigger | Example |
|---|---|
| Complaint / anger | "This is unacceptable" |
| Medical question | "Is Botox safe if I'm on blood thinners?" |
| Pricing negotiation | "Can you do it for less?" |
| Out-of-scope question | "Do you offer laser hair removal?" |
| Explicit human request | "Can I speak to someone?" |

### Session End Triggers

Say any of: `bye`, `goodbye`, `done`, `that's all`, `end` → Generates conversation summary.

---

## SOP Data

The AI operates on `sop_data.json`:

```
Business: Bloom Aesthetics Clinic (UK)
Hours:    Monday–Saturday, 9 AM–7 PM
Services: Botox (from £200), Fillers (from £250), Free Consultations
Booking:  Via WhatsApp or website (24hr cancellation notice required)
Escalate: Complaints, medical questions, pricing negotiation, >2 unanswered questions
```

---

## Trade-offs and Known Limitations

| Limitation | Notes |
|---|---|
| No persistent storage | Conversation history is in-memory. Restarting loses context. Production would use a database. |
| SOP in system prompt | Works for small SOPs. For large SOPs, use RAG with a vector database (e.g., Qdrant). |
| Model-driven escalation | Relies on Claude to self-detect triggers. A secondary sentiment classifier would add robustness. |
| CLI only | No WhatsApp/web frontend. A production version would use Twilio or Meta Cloud API. |
| No auth | No user identification or session tracking. Production requires user ID management. |

---

## Model Used

`claude-sonnet-4-20250514` via the Anthropic Messages API.

---

