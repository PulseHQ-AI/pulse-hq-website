# TEMPORARY — Fixes for Alex's Review

**This file is temporary and is not part of the pipeline.** It exists for one reason (Ben's ruling, 2026-10-30): the fixes are posted here so Alex can read them with his own eyes, and **nothing in this file becomes part of the pipeline — not published into the real files, not adopted, not built on — until Alex has approved it in the Chicken conversation.** Alex's approval is the promotion step. Ben's words: "don't make them part of the pipeline until he's approved it."

Rules for this file:
- One entry per proposed fix: what it changes, which real file it would touch, the candidate's SHA-256, the evidence, and a status.
- Statuses: **WAITING** (posted, no verdict yet) · **APPROVED** (Alex approved in Chicken; incorporation proceeds separately, through the publish gate) · **REJECTED** (Alex declined; the candidate stays local and is not used) · **INCORPORATED** (approved fix has been moved into the real files through the normal gate; entry kept here as the trail).
- No secrets. No real-client data. Test/synthetic material only. This repository is public.
- When every entry is resolved, this file is deleted.

---

## Entry 1 — Glass Desk wired into the portal (Step 2 of the portal completion plan)

- **Status: INCORPORATED** — Alex approved incorporation (Chicken, 2026-10-30 14:03) and accepted the release (15:01); published through the gate 15:09–15:11 (commit b9f8e89) under Ben's 2026-10-29 16:50 delegation; live fetch matched the candidate SHA-256 7102bd86… exactly; Alex accepted the publication + verification report 15:31. (Entry text below is the original WAITING record, kept as the trail.)
- **What it changes:** replaces the portal's old Desk with the glass Desk Ben approved as a prototype on 2026-10-30 — tabbed Waiting / In flight / Done views, counts derived from the records actually shown, a loading failure never presents as a successful empty state. Workspace-scoped data path; isolation and authorization untouched.
- **Real file it would touch:** `liaison-demo/index.html` (the portal).
- **Candidate:** local portal source, SHA-256 `c736b1afff637bea656aa40003ae2ec36a2b6392e80bd16f950fd4758148f4b` — currently NOT published; the live portal is still the previous build (SHA-256 `e4418f8589d5eb86f5b28d65a088f8caaa191d66677d99654863b9d39323ef28`).
- **Design source of record:** the approved prototype `desk-glass.html`, SHA-256 begins `bfad53e1`.
- **Evidence:** test suites green (board 38/38; browser walk 6/6 on a phone viewport; regressions pkg2 44/44, pkg3 48/48, pkg4 33/33, Item 14 24/24, isolation 12/12). Full evidence: `portal-completion-step2-glass-desk-2026-10-30.md` (Remmy's workspace; quoted in Chicken).

---

## Entry 2 — Ben's phone-walk findings on the live glass Desk (2026-10-30, ~15:41–17:27)

Source: Ben's own acceptance walk (A10) on his phone, live portal, PULSE-9052. Three findings, one palette decision. Nothing here is built or published; statuses per item.

- **2a — "Completed actions" headline margin. Status: INCORPORATED** — Alex approved incorporation (Chicken, 2026-10-30 20:13), cleared the exact candidate for publication (20:44), and it was published through the gate 2026-10-30 (commit 0b8ecd3, candidate SHA-256 82d288f5…) under Ben's 2026-10-29 16:50 delegation; live fetch matched the candidate hash exactly and the cache-busted live walk passed (Desk + neighbours).** The section headline sits flush against the screen edge, outside the inset its card content respects. Fix: give section headlines the same horizontal inset as the cards (prototype: 22px, matching card padding). Real file it would touch: `liaison-demo/index.html` (portal CSS).
- **2b — Packages tab text colour, light mode. Status: INCORPORATED** — same approval, clearance, gate publication (commit 0b8ecd3, candidate SHA-256 82d288f5…) and live verification as 2a.** The unselected "Waiting" / "In flight" labels render in a washed-out blue-grey on the dark segmented track — nearly unreadable in light mode. Fix: unselected labels to the palette's near-white tab label (#EFEDFF on track #332C5E under Palette B). Real file: `liaison-demo/index.html` (portal CSS).
- **2c — Light-mode palette. Status: DECIDED BY BEN (recorded for Alex's information, not a verdict ask).** Ben picked **Palette B — Frosted Violet** (tap, 2026-10-30 17:27): background #F8F7FE → #ECEAF8, card glass white 75%, section headers #5A4BD1 violet (this also answers Ben's "headers are too dark" finding — near-black #16233a is retired for light-mode headers), titles #262157, body #4C4880, muted #8B87B8, action gradient violet #7C5CFF → cyan #00B8E6. Applied so far only to the standalone prototype (v3). Live application rides with the 2a/2b fix pass once approved.
- **2d — Bottom navigation, nine items cramped. Status: BEN-APPROVED** — Ben approved the nav prototype v3 (five primaries + More, Palette B) in the main chat 2026-10-30 20:32 ("That's it bud." after the Phase A acceptance was stated back), and Alex acknowledged that approval in Chicken 2026-10-30 21:01, noting the separate 2d ruling request follows this status update. A ruling from Alex is now requested before any build into the portal. (Original record: Ben's walk found the nine-item bottom bar cramped on a phone. A standalone prototype (live portal untouched) rebuilds it as five primaries (Overview, Requests, Clients, Liaison, Desk) + a More sheet holding the other four. Ben's instruction was: "See what you can do and I'll see how it feels.")
- **Prototype evidence:** `~/workspace/desk-prototype/nav-fix-prototype-v3.html` (Palette B applied; v1/v2 retained). Ben has viewed v1 (his screenshot confirmed the headline + tab findings render as reported) and holds v3.

