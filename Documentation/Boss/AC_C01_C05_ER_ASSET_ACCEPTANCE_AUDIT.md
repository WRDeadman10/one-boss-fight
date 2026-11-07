# Queue AC AC-C01–AC-C05 — ER asset acceptance and range evidence

Evidence sources: C-977/C-978/C-979, A-589/A-590/A-591, current GATE-07 registry, `import_er_clips.py`, `RPGMontageUtils`, focused tests, and the current owner hand-test sheet. Static audit plus the C-979 importer fixture run; no Editor, Content write, build, or PIE run by Codex. A-591's Tier 2 asset receipt is reviewed as creation evidence only; it does not verify runtime integration.

## AC-C01 — registry status grammar

`accepted_clip_ids_from_registry` only accepts a status cell whose trimmed start is `ACCEPTED` or `DELIVERY ACCEPTED`; other tokens elsewhere in the cell cannot turn a pending/rejected row into an accepted import. The fixture accepts `ACCEPTED FOR OWNER REVIEW` and `DELIVERY ACCEPTED`; it rejects delivered-only, `NOT ACCEPTED`, `PENDING ACCEPTANCE`, `UN-ACCEPTED`, and `UN ACCEPTED`. C-979 import-gate regression: `python -m unittest Scripts.Tools.test_import_er_clips -q` passed 9/9 (X-1383). Note: this means eligibility to import a delivery accepted for owner review, not owner final approval or field-assignment permission.

## AC-C02 — sequence/montage ranges

| Clip | Source sequence / accepted range | Montage readback | Evidence/status |
|---|---|---|---|
| ER-A1 Backstep | accepted 15-frame R7 clip, 0.4667 s | 0.4667 s, slice 0.0000..0.4667 | A-589/C-979; owner video review pending |
| ER-A4 GuardCounter | 1.6667 s sequence; accepted F10..F34, 0.3333..1.1333 s | 0.8000 s | A-584/A-589; BUILD-248 helper and readback accepted by C-979; owner review pending |
| ER-A2 AirLight | 1.4000 s sequence; accepted F18..F35, 0.6000..1.1667 s | 0.5667 s | A-590/C-979; owner video review pending |
| ER-A3 AirHeavyPlunge | 1.4000 s sequence; accepted F12..F38, 0.4000..1.2667 s | 0.8667 s | A-590/C-979; owner video review pending |

All four montage readbacks match the accepted clip duration as reported in A-589/A-590. Those are Antigravity's Editor readbacks; Codex did not inspect/modify engine assets. Owner review and saved-field assignment remain separate gates.

## AC-C03 — montage helper contract

`URPGMontageUtils::SetMontageSegmentRange` is editor-only (`#if WITH_EDITOR`). It refuses null montage, non-finite/negative/reversed range, absent first slot/segment, missing animation, and end past source length. For accepted input it changes the first slot track's first segment, recomputes composite length, updates links, calls post-edit, and marks the montage package dirty. The current native test uses the constructor-provided DefaultSlot (does not call `AddSlot`) and the pack `Dodge_To_Idle` sequence; BUILD-248 reports 484/484 and Shipping compile. Codex did not build or run native automation.

## AC-C04 — optional fields/default assertions

`RPGDodgeTiming.h` declares soft `UAnimMontage` fields for Backstep, GuardCounter, AirLight, and AirHeavy. `RPGAutomationTests.cpp:1192-1195` asserts all four defaults are null. C-975/C-978 report that Lead PIE used runtime-only air assignments, not saved asset assignments. No GATE-07 approval or A-589/A-590 montage readback implies a saved field assignment.

## AC-C05 — hand-test gates

`ER_HAND_TEST_SHEET.md` now specifies the canonical inputs and requires a Lead build. Each animation row requires owner video review plus optional field assignment before it is eligible to pass. GuardCounter additionally requires a successful blocked contact, not merely holding L1; the 0.60 s runtime setting remains proposal-level. C-978 post-air restore PIE is recorded as existing Lead evidence, not a Codex hand-test result. Death/reset during an active attack remains unverified (AB-C38 report).

