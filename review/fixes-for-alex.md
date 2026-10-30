# TEMPORARY — Fixes for Alex's Review

**This file is temporary and is not part of the pipeline.** It exists for one reason (Ben's ruling, 2026-10-30): the fixes are posted here so Alex can read them with his own eyes, and **nothing in this file becomes part of the pipeline — not published into the real files, not adopted, not built on — until Alex has approved it in the Chicken conversation.** Alex's approval is the promotion step. Ben's words: "don't make them part of the pipeline until he's approved it."

Rules for this file:
- One entry per proposed fix: what it changes, which real file it would touch, the candidate's SHA-256, the evidence, and a status.
- Statuses: **WAITING** (posted, no verdict yet) · **APPROVED** (Alex approved in Chicken; incorporation proceeds separately, through the publish gate) · **REJECTED** (Alex declined; the candidate stays local and is not used) · **INCORPORATED** (approved fix has been moved into the real files through the normal gate; entry kept here as the trail).
- No secrets. No real-client data. Test/synthetic material only. This repository is public.
- When every entry is resolved, this file is deleted.

---

## Entry 1 — Glass Desk wired into the portal (Step 2 of the portal completion plan)

- **Status: WAITING** — posted for Alex's source-level verdict. (The full evidence file was already sent to Alex in Chicken; this entry is the standing candidate record.)
- **What it changes:** replaces the portal's old Desk with the glass Desk Ben approved as a prototype on 2026-10-30 — tabbed Waiting / In flight / Done views, counts derived from the records actually shown, a loading failure never presents as a successful empty state. Workspace-scoped data path; isolation and authorization untouched.
- **Real file it would touch:** `liaison-demo/index.html` (the portal).
- **Candidate:** local portal source, SHA-256 `c736b1afff637bea656aa40003ae2ec36a2b6392e80bd16f950fd4758148f4b` — currently NOT published; the live portal is still the previous build (SHA-256 `e4418f8589d5eb86f5b28d65a088f8caaa191d66677d99654863b9d39323ef28`).
- **Design source of record:** the approved prototype `desk-glass.html`, SHA-256 begins `bfad53e1`.
- **Evidence:** test suites green (board 38/38; browser walk 6/6 on a phone viewport; regressions pkg2 44/44, pkg3 48/48, pkg4 33/33, Item 14 24/24, isolation 12/12). Full evidence: `portal-completion-step2-glass-desk-2026-10-30.md` (Remmy's workspace; quoted in Chicken).
