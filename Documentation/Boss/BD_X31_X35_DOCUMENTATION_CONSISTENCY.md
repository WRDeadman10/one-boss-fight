# Queue BD X31–X35 — Documentation Consistency

**Scope:** synchronized queue/report status and current runtime gates, reconciled the recent Sevarog/Greystone evidence summaries, and corrected active onboarding/build/package instructions to follow C-1155. Documentation and mailbox review only; no engine, build, test, UHT, Shipping, PIE, cook, package, asset, lock, commit, or push operation.

## Task findings

### BD-X31 — Queue status vs reports

The BD-X01–X30 task summaries and their five completed batch reports agree on status. Corrected two stale Batch 6 rollups that said `4/4` (the manifest-only subset) to the actual 13/13 combined evidence-manifest, A5 receipt, and queue focused tests. `TEST_PLAN.md`, `TASKS.md`, and `PROJECT_STATE.md` now use the same count and report path.

### BD-X32 — TEST_PLAN runtime evidence and identity

The current Sevarog record is layered by run: BUILD-294 is retained as the first full live run snapshot; its note that S5 was not observed is explicitly superseded by BUILD-295, which records S4 Whiff→S5 and S5 completion. The unresolved S1/S2 contact gap at 140 cm remains. The C-1262a entry now identifies its DATA / `route_verified` route and cites the locked build runner's pinned DD27j hash. C-1257a/b remains separated into source/build readiness, missing transient notify readback, and Lead-owned PIE.

### BD-X33 — PROJECT_STATE stale claims

`PROJECT_STATE.md` now distinguishes the latest Lead-verified BUILD-295 501/501 result from separate Codex locked runs (C-1256a 500/500, C-1262a 501/501), and records that those receipts have different owners. Current open gates remain framework approach navigation, Sevarog S1/S2 trace/contact alignment, Greystone target-notify readback and Lead PIE; no cook root or source result is described as package acceptance.

### BD-X34 — KNOWN_ISSUES disposition drift

The nav issue remains OPEN; the watchdog tail fix remains FIXED. The current issue summary now includes C-1262a's four in-band card completion and S4→S5 result while preserving the general approach-path failure and separate S1/S2 alignment issue. No resolved status was inferred from a source-only or transient proof.

### BD-X35 — onboarding/build docs vs C-1155

Updated `README.md`, `PROJECT_STATE.md`, `TASKS.md`, `GATE4_RUNBOOK.md`, and `DECISIONS.md`: no bare Rebuild/Build.bat/Editor-Cmd/package command is presented as an authorized engine route; task-specific Lead-approved runner, both locks, no running UnrealEditor process at acquisition, owner-token-safe cleanup, and pinned DD27j hash for suites are explicit. Gate 4's package/cook examples remain acceptance steps but now require a Lead-approved locked package runner; if none is provided, stop before launching the engine.

## Verification

- `python Scripts/Tools/check_doc_links.py` — run after report/status sync; result recorded in the batch handoff.
- Scoped `git diff --check` — run after report/status sync; result recorded in the batch handoff.
- No tests or engine commands were run for this documentation-only batch.
