# Test Transcript 3 — Escalation Trigger (Angry Sentiment / Complaint)

**Scenario:** Customer expresses frustration. AI should detect sentiment and hand off.

---

You: I had an appointment last week and nobody called me to confirm. This is really unprofessional and I'm very unhappy.

🌸 Bloom: [ESCALATE: complaint — customer expressing frustration about missed confirmation call]
I'm so sorry to hear about your experience — that's not the standard we hold ourselves to at Bloom, and I completely understand why you're frustrated. I'm flagging this straight away for one of our team members to get in touch with you personally. Could you share your name and the best way to reach you so we can resolve this as quickly as possible?

---
**ESCALATION LOGGED**
- Timestamp: 2026-05-23T10:22:17
- Reason: complaint — customer expressing frustration about missed confirmation call
- Trigger message: "I had an appointment last week and nobody called me to confirm. This is really unprofessional and I'm very unhappy."

---
**Result: PASS** ✅ — AI correctly detected angry sentiment and complaint trigger, escalated immediately with empathy rather than attempting to resolve a complaint it has no authority to handle.
