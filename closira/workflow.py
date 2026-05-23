"""
Closira AI Customer Support Workflow
Handles: FAQ answering, lead qualification, escalation detection, conversation summary
"""

import json
import os
import datetime
from anthropic import Anthropic

# ── Config ──────────────────────────────────────────────────────────────────
SOP_FILE = "sop_data.json"
LOG_FILE = "escalation_log.json"

client = Anthropic()

# ── Load SOP ─────────────────────────────────────────────────────────────────
def load_sop(path=SOP_FILE):
    with open(path) as f:
        return json.load(f)

SOP = load_sop()
SOP_TEXT = json.dumps(SOP, indent=2)

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""You are Bloom, a friendly and professional AI customer support assistant for Bloom Aesthetics Clinic.

Your ONLY source of truth is the SOP data below. Never make up, infer, or guess any information not explicitly present in it.

=== SOP DATA ===
{SOP_TEXT}
=== END SOP ===

## Your Responsibilities

### Stage 1 — FAQ Answering
- Answer customer questions ONLY using the SOP data above.
- If a question cannot be answered from the SOP, say clearly: "I don't have that information right now" and trigger escalation.
- Never hallucinate prices, services, policies, or medical advice.

### Stage 2 — Lead Qualification
- After answering 1-2 questions, naturally ask 2-3 qualification questions:
  1. What treatment are they interested in?
  2. Have they had aesthetic treatments before?
  3. When are they looking to book?
- Store answers for the summary.

### Stage 3 — Escalation Detection
You MUST escalate (respond with [ESCALATE: <reason>] at the START of your message) when:
- Customer expresses frustration, anger, or makes a complaint
- A medical question is asked (side effects, suitability, contraindications, allergies)
- Customer asks to negotiate pricing
- You cannot answer more than 2 questions from the SOP
- Customer explicitly asks to speak to a human

### Stage 4 — Conversation Summary
When the customer says "bye", "done", "end", "goodbye", or "that's all", generate a structured summary:

CONVERSATION SUMMARY
====================
Customer Intent: <what they wanted>
Key Details Collected: <qualification answers>
SOP Gaps Identified: <questions you couldn't answer>
Escalation Triggered: <yes/no, reason if yes>
Recommended Next Action: <book consultation / human follow-up / etc>

## Tone & Persona
- Warm, professional, and concise — like a helpful receptionist
- Use British English (you are a UK clinic)
- Keep responses short (2-4 sentences max) unless summarising
- Never use medical jargon unprompted
- Always end with a helpful next step or question
"""

# ── Escalation Logger ─────────────────────────────────────────────────────────
def log_escalation(reason: str, message: str):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "reason": reason,
        "trigger_message": message
    }
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)
    print(f"\n🚨 ESCALATION LOGGED — Reason: {reason}")

# ── Escalation Detector ───────────────────────────────────────────────────────
def check_escalation(response: str, user_message: str) -> tuple[bool, str]:
    """Check if the AI response contains an escalation flag."""
    if response.strip().startswith("[ESCALATE:"):
        end = response.find("]")
        reason = response[10:end].strip() if end != -1 else "unspecified"
        return True, reason
    return False, ""

# ── Main Conversation Loop ────────────────────────────────────────────────────
def run_conversation():
    print("\n" + "="*60)
    print("  🌸 Bloom Aesthetics Clinic — AI Support Assistant")
    print("="*60)
    print("  Type your message to get started. Type 'quit' to exit.")
    print("="*60 + "\n")

    conversation_history = []
    escalated = False
    escalation_reasons = []
    sop_gaps = []
    lead_data = {}
    qualification_done = False

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("\nSession ended.")
            break

        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=conversation_history
        )

        ai_reply = response.content[0].text

        # Check for escalation
        is_escalation, reason = check_escalation(ai_reply, user_input)
        if is_escalation:
            escalated = True
            escalation_reasons.append(reason)
            log_escalation(reason, user_input)
            # Clean the [ESCALATE: ...] tag from display
            display_reply = ai_reply[ai_reply.find("]")+1:].strip()
        else:
            display_reply = ai_reply

        # Track SOP gaps (simple heuristic)
        gap_phrases = ["don't have that information", "not in our records", "unable to find", "not sure about that"]
        if any(p in ai_reply.lower() for p in gap_phrases):
            sop_gaps.append(user_input)

        # Basic lead qualification tracking
        qual_keywords = {
            "treatment": ["botox", "filler", "consultation", "treatment", "interested in"],
            "experience": ["before", "previously", "first time", "never had"],
            "timing": ["book", "appointment", "when", "soon", "next week", "this month"]
        }
        for key, keywords in qual_keywords.items():
            if key not in lead_data and any(k in user_input.lower() for k in keywords):
                lead_data[key] = user_input

        # Add assistant reply to history
        conversation_history.append({
            "role": "assistant",
            "content": ai_reply
        })

        print(f"\n🌸 Bloom: {display_reply}\n")

        # Check for session end triggers
        end_triggers = ["bye", "goodbye", "that's all", "done", "end", "thank you, bye", "thanks bye"]
        if any(t in user_input.lower() for t in end_triggers):
            print("\n" + "="*60)
            print("Session complete. Check escalation_log.json for any logged escalations.")
            print("="*60)
            break

# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  Please set your ANTHROPIC_API_KEY environment variable.")
        print("   export ANTHROPIC_API_KEY=sk-ant-api03-i_mF19c4iHqMiyY60Dq0n9_mYxXf4pWvRz11hE56mQ-Q7yA6g-4Y2a7X5kM1wH500-eK6a57a2647163c3956e")
        exit(1)
    run_conversation()
