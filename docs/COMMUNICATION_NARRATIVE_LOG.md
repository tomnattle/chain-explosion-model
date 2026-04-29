# Communication Narrative Log (Privacy-Safe)

Purpose: record project communication narrative only, without personal/private data.

## Redaction Rules (Mandatory)

- Do NOT store: real names, email addresses, phone numbers, institution IDs, account handles.
- Do NOT store: raw email headers, signatures, full quoted threads.
- Do NOT store: any credential, token, local path revealing personal identity.
- Use role labels only: `Expert-A`, `Advisor-B`, `External Reviewer`, etc.
- Keep entries factual: question -> action -> result -> next step.

## Entry Template

```text
Date:
Channel: (email/chat/meeting)
Counterparty Role: (Expert-A / Advisor-B / Reviewer)
Topic:
Question Received:
Response Strategy:
Evidence Used: (file paths / result IDs only)
Outcome:
Next Action:
Privacy Check: PASSED
```

---

## Entries

### Entry 001
Date: 2026-04-29
Channel: email
Counterparty Role: Expert-A
Topic: Pairing-window sensitivity and reference-clock semantics
Question Received: Whether observed sensitivity is related to coincidence-loophole structure.
Response Strategy: Separate external-clock modes vs event-anchored probe modes; report binary CHSH separately from continuous diagnostics.
Evidence Used:
- `battle_results/nist_clock_reference_audit_v1/results/nist_unified_semantics_audit_v4.json`
- `battle_results/nist_clock_reference_audit_v1/email_pack_v4/EMAIL_SUMMARY_v4_EN.md`
Outcome: Technical follow-up prepared with reproducible numbers and boundary conditions.
Next Action: Send conservative technical update with two summary figures.
Privacy Check: PASSED

### Entry 002
Date: 2026-04-29
Channel: internal
Counterparty Role: Advisor-B
Topic: Progress update after expert consultation
Question Received: Whether the audit reached mechanism-level closure.
Response Strategy: Share concise status only; avoid requesting out-of-scope technical ruling.
Evidence Used:
- `battle_results/nist_clock_reference_audit_v1/FINAL_AUDIT_VERDICT.md`
Outcome: Short status message drafted.
Next Action: Keep long-form technical details in expert-facing channel only.
Privacy Check: PASSED

