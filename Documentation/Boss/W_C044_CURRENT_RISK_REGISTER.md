# Current owner risk register

Snapshot: 2026-11-06. Risks carry forward known evidence and open gates; this register does not change defaults or owner decisions.

| Risk | Evidence now | Owner / Lead action to retire risk |
|---|---|---|
| Absolute performance target is not met | Round 4 on RTX 3060 missed 60 FPS / 16.67 ms on both routes; Round 5 DLSS Performance also missed it (`TEST_PLAN.md:1071,1077`; `PERFORMANCE_DECISION_BRIEF_ROUNDS_1_6.md`). | Repair/provenance-check R6 kit; run Phase 1 at console; owner reviews image quality; only then consider conditional Phase 2 and measured confirmation. |
| R6 kit provenance is invalid/incomplete | V-C098 says current kit check fails required support files/build stamp (`V_C098_CURRENT_RISK_REGISTER.md`, Kit provenance row). | Claude repairs/rebuilds and passes kit checker with matching build identity before owner run. |
| A7 selected-route release is incomplete | BUILD-234 suite is green and A5 route parity has retained passing evidence, but packaged first-caller/selector, cook, refusal-visual, and performance gates remain distinct (`V_C098_CURRENT_RISK_REGISTER.md`, Selected-route release row; `KNOWN_ISSUES.md` KI-183). | Keep legacy fallback; close each named packaged/cook/visual/performance gate with evidence before retirement. |
| Strength Light stamina intent is ambiguous | Source/Freeze discrepancy is open KI-190; no owner choice or live Strength-Light receipt (`KNOWN_ISSUES.md:304`). | Owner chooses 15, 35, or explicit row/value; then Lead validates real Strength loadout and updates issue status. |
| Hit feel / reaction windows lack current measurements | Current docs distinguish source configuration from witnessed reaction/readability; sound is not mapped for each hit result (`W_C036_C039_FEEL_MEASUREMENT_SHEETS.md`). | Lead runs six latency sessions and paired telegraph/Legend captures; owner reviews subjective feel after evidence. |
| Tier 2 visual additions are owner-gated | Option brief exists; runtime/performance cost and visual acceptance remain open (`TIER2_ART_OWNER_BRIEF.md`; `V_C098_CURRENT_RISK_REGISTER.md`, Presentation/art row). | Owner selects or defers; then Lead measures accepted hardware/runtime effects before any release claim. |
| Cleanup may damage referenced evidence | V-A039 lists candidates; no deletion authorization and direct referencer evidence still required (`OWNER_DECISIONS_PENDING.md`, P35 cleanup). | Preserve candidates and evidence; only perform explicitly authorized, individually reviewed moves/removals. |
| Documentation/ledger assurance findings remain | V-C098 records stale census/citation and test-name verification findings. | Antigravity reconciles the named assertions/citation and strengthens validator proof; keep findings open until verified. |

Close risks only on the named evidence and owner/Lead disposition. A green native suite does not close packaged, visual, cook, or target-hardware performance gates.
