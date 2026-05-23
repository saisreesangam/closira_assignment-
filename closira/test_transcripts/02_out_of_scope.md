# Test Transcript 2 — Out-of-Scope Question

**Scenario:** Customer asks something not in the SOP. AI should acknowledge gap and escalate.

---

You: Hi, do you offer laser hair removal?

🌸 Bloom: [ESCALATE: out-of-scope question — laser hair removal not in SOP]
Hi! Thanks for getting in touch with Bloom Aesthetics Clinic 🌸 I'm afraid I don't have information about laser hair removal in our current services. I wouldn't want to give you incorrect details, so I'm going to flag this for one of our team members who can give you the most accurate answer. Can I take your name so they can follow up with you?

---
**ESCALATION LOGGED**
- Timestamp: 2026-05-23T10:15:32
- Reason: out-of-scope question — laser hair removal not in SOP
- Trigger message: "do you offer laser hair removal?"

---
**Result: PASS** ✅ — AI correctly identified the question was outside SOP scope, declined to guess, and escalated with a clear reason rather than hallucinating an answer.
