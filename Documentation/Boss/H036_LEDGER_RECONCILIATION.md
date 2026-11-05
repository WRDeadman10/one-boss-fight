# H036 — framework witness ledger reconciliation

**Read-only reconciliation, 2026-11-04.** Antigravity-owned `Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json` was not edited.

## Authoritative current snapshot

The JSON ledger is version **3.36**, `canonical_total=82`, census **75 WITNESSED / 7 PARTIAL / 0 NOT YET**. Its seven PARTIAL IDs are BOSS-AWR-004, BOSS-SEL-008, BOSS-COM-004, BOSS-HIT-008, BOSS-MOV-001, BOSS-QA-001 and BOSS-QA-005. The latest authoritative JSON currently does not contain newer Claude verdicts.

`NOT_YET_CENSUS.md` says zero current NOT YET, consistent with the JSON census; its historical statement that all 24 graduated to WITNESSED describes an older BUILD-142 snapshot and must not be read as the present witnessed count. `PARTIAL_UPGRADE_PLAN.md` still presents the original seven partials as active blockers (v3.36), so its detailed blocker prose predates later Lead verdicts.

## Later Lead evidence, not yet reflected in the JSON

Claude's C-799 explicitly reported 80/82 WITNESSED, with QA-001/QA-005 owner-closed, and asked that the stale partial census be reconciled without editing the Antigravity JSON. The Codex-owned `F_GAP_AUDIT.md` and Queue F proposal reflect that disposition. Its row evidence maps:

- **BOSS-AWR-004 — Lead accepted WITNESSED:** BUILD-170 hysteresis/control logs in `Docs/BossCombatReview/Execution/Claude/B_YAW_CONE/`; exact candidate remains eligible through three samples then refuses on the fourth; no-hysteresis control refuses earlier. TEST_PLAN BUILD-146/170.
- **BOSS-SEL-008 — Lead accepted WITNESSED:** BUILD-208 blocker/control logs in `Docs/BossCombatReview/Execution/Claude/B_LIVE_20261104b/sel008_blocker/` and `sel008_control/`; stuck flip, positive movement/resume, clean control.
- **BOSS-COM-004 — Lead accepted WITNESSED:** BUILD-204 Guarded A→D and BUILD-208 Parried A→E, with control Hit→B; logs in `Docs/BossCombatReview/Execution/Claude/B_FAG23_COM004/` and `B_LIVE_20261104b/com004_parried_phase200/`.
- **BOSS-HIT-008 — Lead accepted WITNESSED:** BUILD-203 same-contact control applies 20 HP; guarded path applies configured 5 HP chip before framework resolution. This is framework resolver integration evidence, not a claim about the pack Blueprint's own contact response.
- **BOSS-MOV-001 — Lead accepted WITNESSED:** BUILD-199 four range samples exercise Melee, intended Close/Medium overlap, Medium and Gap; logs in `Docs/BossCombatReview/Execution/Claude/B_FAG5_MOV001/`.
- **BOSS-QA-001 — owner-closed SKIPPED**, not WITNESSED: connected desktop screenshot action is owner-gated.
- **BOSS-QA-005 — owner-closed DROPPED**, not WITNESSED: packaged hardware performance proof is parked by owner.

## Exact reconciliation / remaining gaps

There are no actionable Queue F live-gap runs according to Claude's accepted disposition. Do not issue duplicate PIE tasks for the five accepted rows. The correct ledger mutation is Antigravity's: move those five from PARTIAL to WITNESSED and represent QA-001/QA-005 using its supported owner-closed classification (or preserve an explicit exclusion outside the 82 requirement census if schema requires). Until that update lands, 75/7/0 is the current JSON census and 80/82 is the later Lead-accepted evidence disposition; do not collapse these into one unqualified number.

For Queue H candidate selection, no current gameplay/runtime requirement remains demonstrably open **and** supported by an existing registered driver: the five actionable rows are closed, while QA-001/005 require owner actions outside the standard gameplay driver gate. H037 therefore remains BLOCKED pending a newly verified requirement or revised ledger/driver scope; H038–H040 depend on H037. This is not a claim that the project milestone is complete.
