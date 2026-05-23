# Prompt Design — Closira AI Support Workflow

## Overview

This document explains the system prompt design, hallucination prevention strategy, escalation logic, and tone decisions made for the Bloom Aesthetics Clinic AI workflow.

---

## System Prompt

The full system prompt is embedded in `workflow.py` under `SYSTEM_PROMPT`. Key sections:

1. **Role definition** — Establishes the AI as "Bloom", a receptionist-style assistant for a specific UK aesthetics clinic.
2. **SOP injection** — The entire SOP JSON is embedded directly into the system prompt so the model has grounded context at all times.
3. **Stage instructions** — Each of the four workflow stages (FAQ, Qualification, Escalation, Summary) is explicitly described with clear behavioural rules.
4. **Escalation format** — The model is instructed to output `[ESCALATE: <reason>]` as a structured, parseable flag.
5. **Tone guidelines** — Specific persona and communication style instructions.

---

## Design Decisions

### Why embed the full SOP in the system prompt?
Embedding the SOP directly ensures it is present in every API call without requiring a retrieval step. For a small SOP like this one, it fits well within the context window and guarantees the model cannot "forget" the source of truth between turns.

### Why use a structured `[ESCALATE: reason]` tag?
A machine-parseable tag at the start of the response allows deterministic escalation detection without requiring a second LLM call to classify the response. This keeps latency low and logic simple. The tag is stripped from the displayed response so customers never see internal flags.

### Why separate the four stages in the prompt rather than using separate prompts?
A single coherent system prompt maintains conversational context across all stages. Switching system prompts mid-conversation would lose context and feel disjointed to the customer. The model naturally transitions between stages based on conversational cues.

---

## Hallucination Prevention

Three explicit strategies are used:

### 1. Hard grounding instruction
The prompt states clearly:
> "Your ONLY source of truth is the SOP data below. Never make up, infer, or guess any information not explicitly present in it."

### 2. Explicit failure mode instruction
Instead of telling the model what to do when it knows something, the prompt also tells it what to do when it does NOT know:
> "If a question cannot be answered from the SOP, say clearly: 'I don't have that information right now' and trigger escalation."

This prevents the model from attempting to be helpful by guessing, which is the most common hallucination failure mode in customer support contexts.

### 3. Escalation as the fallback
By making escalation the explicit fallback for any uncertainty, the model is never in a position where generating a plausible-sounding but unverified answer is the "best" option. The safe path is always escalation.

---

## Confidence-Based Escalation

Escalation is triggered under five conditions, in order of priority:

| Trigger | Detection Method |
|---|---|
| Angry sentiment / complaint | Model detects tone and outputs `[ESCALATE: complaint]` |
| Medical question | Model identifies medical content and outputs `[ESCALATE: medical question]` |
| Pricing negotiation | Model detects negotiation intent and outputs `[ESCALATE: pricing negotiation]` |
| >2 unanswered questions | Model tracks its own inability to answer and escalates |
| Explicit human request | Customer says "speak to someone", "human", etc. |

The detection is model-driven rather than rule-based for the first four triggers. This allows nuanced detection of frustration ("this is ridiculous") that keyword matching would miss.

All escalations are:
- Flagged in the AI response with `[ESCALATE: reason]`
- Logged to `escalation_log.json` with timestamp, reason, and trigger message
- Communicated transparently to the customer ("I'm going to connect you with one of our team members")

---

## Tone and Persona

**Persona:** "Bloom" — a warm, professional clinic receptionist.

**Key tone decisions:**

- **British English** — The clinic is UK-based (prices in £, "enquiries" not "inquiries"). Using British spelling signals cultural authenticity to customers.
- **Short responses** — 2-4 sentences per reply unless summarising. Customers contacting via WhatsApp expect concise replies, not paragraphs.
- **No unsolicited medical jargon** — The model avoids terms like "neurotoxin" or "hyaluronic acid" unless the customer introduces them. This keeps conversations accessible.
- **Always ends with a next step** — Every response closes with a clear action (book, ask another question, speak to the team). This mirrors good receptionist behaviour and keeps the conversation moving.
- **Warm but professional** — Not overly casual ("Hey!") or overly formal ("Dear valued customer"). The target is the tone of a friendly GP receptionist.

---

## Lead Qualification Design

The qualification questions are designed to be:
1. **Non-intrusive** — Asked after the customer's initial question is answered, not immediately on greeting
2. **Conversational** — Phrased as natural follow-ups, not a form-filling exercise
3. **Actionable** — Each answer feeds directly into the conversation summary's recommended next action

The three questions:
1. *What treatment are you interested in?* → Identifies service fit
2. *Have you had aesthetic treatments before?* → Identifies new vs returning patient
3. *When are you looking to book?* → Identifies urgency and booking readiness

---

## Known Limitations and Trade-offs

- **No persistent memory** — Conversation history is in-memory only. Restarting the script loses the session. A production system would store history in a database.
- **Model-driven escalation** — The model decides when to escalate. In rare cases it may miss subtle frustration. A production system could add a secondary sentiment classifier.
- **SOP in prompt** — For larger SOPs, embedding the full document would exceed context limits. A RAG (retrieval-augmented generation) approach using a vector database (e.g., Qdrant) would be more scalable.
- **No auth or rate limiting** — This is a CLI prototype. A production WhatsApp integration would require proper webhook handling, rate limiting, and user identification.
