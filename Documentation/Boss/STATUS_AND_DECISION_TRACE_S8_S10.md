# Proof status and decision trace audit (Queue C S8–S10)

Read-only comparison of current evidence classifications and selected active policy notes. `witness_status_v3.json` remains authoritative for requirement status; this audit does not edit or promote ledger rows.

## S8: evidence type vs current partial plan

Ledger v3.36 has 75 WITNESSED, 7 PARTIAL, and 0 NOT YET (ledger `census`). Its seven PARTIAL ids are AWR-004, SEL-008, COM-004, HIT-008, MOV-001, QA-001, and QA-005. The zero-NOT-YET census agrees with the ledger (`NOT_YET_CENSUS.md:1–14`). The partial plan names the same seven ids, but its explanatory text has stale implementation/proof claims:

| Row | Stale plan text | Current evidence / precise remaining boundary |
|---|---|---|
| BOSS-AWR-004 | `PARTIAL_UPGRADE_PLAN.md:7` says selector-side hysteresis memory “not built”; line 29 says its unit test is the upgrade target. | `DECISIONS.md:1292–1294` records the opt-in selector memory; `TEST_PLAN.md` BUILD-146 records built tests and live profile wiring. Ledger remains PARTIAL because the cited row evidence is still narrow; the live edge-flicker oscillation itself is not proven. |
| BOSS-SEL-008 | Plan line 8 says the neutral strafe loop and opt-in policy are “not built.” | `DECISIONS.md:1304–1306` specifies the opt-in `NeutralStrafeSeconds` behavior. KI-149 and the open-issue digest say ordinary neutral strafe is implemented, while the stuck-recovery branch is unit proven/live not proven after R3c emitted no `strafe_stuck`. |
| BOSS-MOV-001 | Plan line 11 says only a single band is observed and all 15 families await authoring. | `DECISIONS.md:1300–1302` describes opt-in range-band partitioning and reuse of two additional cards. The current ledger still has MOV-001 PARTIAL; confirm the required family/reach witness against the exact observable before changing status. |
| BOSS-QA-001 | Plan line 12 describes a live overlay screenshot as the remaining witness. | Ledger evidence includes live log lines and formatter unit evidence; TEST_PLAN BUILD-144 documents the screenshot capture blocker and connected-owner route. The blocker remains accurately scoped to viewport pixels. |
| BOSS-QA-005 | Plan line 13 says packaged RTX 2060 Super measurement is parked. | This is consistent with the project gate target and no packaged target-hardware run is recorded in the reviewed current docs. |

COM-004/HIT-008 remain partial for the player guard/parry integration witness called out in `DECISIONS.md:1290`; the cited live Guarded edge does not prove Parried. The partial plan's rows for those remain directionally current. This review flags stale descriptions without treating code, compilation, or unit tests as live proof.

## S9: recommended evidence vocabulary

Use these terms in future notes; do not rewrite historical rows as part of this audit.

| Term | Minimum evidence meant by the term |
|---|---|
| **Authored** | Source, script, or content change exists. No compile or execution claim. |
| **Built** | The intended source/content compiled or was loaded successfully; does not imply a behavior test passed. |
| **Unit proven** | The named automated test actually ran and passed for its stated pure/runtime boundary. |
| **Live proven** | A retained editor/PIE or packaged run shows the requested behavior and its acceptance criteria. |
| **WITNESSED / PARTIAL / NOT YET** | Canonical ledger classifications; they summarize requirement-level evidence and are not substitutes for the four work/evidence terms above. |

Record evidence path, run identifier, and the exact observable whenever using “unit proven” or “live proven.” A build alone must never be described as either.

## S10: sampled active policy-to-decision trace

| Active constraint | Decision source | Implementation/evidence pointer | Audit result |
|---|---|---|---|
| Cone hysteresis is opt-in and defaults off; preserve old behavior at zero. | `DECISIONS.md:1292–1294`, BOSS-AWR-004. | Profile/selector/model path; BUILD-146 in `TEST_PLAN.md`; exact edge oscillation remains a live-proof limit. | Direct dated decision exists; retain its proof limit. |
| Player parry resolves after dodge i-frames; the pack parry remains a stub. | `DECISIONS.md:1296–1298`, owner decision. | `URPGPlayerParry`, resolver and KI-153. | Direct owner decision exists; animation/reaction/stamina remain open design questions in source note. |
| Range-band partition is opt-in; band sets walk target, card range remains its own eligibility gate. | `DECISIONS.md:1300–1302`, owner approval. | `bRangeBandPartition` and MOV-001 evidence. | Direct decision exists; profile/family witness remains partial. |
| Neutral strafe is opt-in, budget defaults to zero, and follows reposition branches. | `DECISIONS.md:1304–1306`, BOSS-SEL-008. | `NeutralStrafeSeconds`, KI-149; live stuck-recovery gap in `OPEN_ISSUES_DIGEST.md`. | Direct decision exists; default-off and live-proof limit must remain explicit. |
| Boss parry posture damage defaults to zero until owner selects a production value. | `DECISIONS.md:1308–1310`, owner policy recorded by Claude. | `ParryPostureAmount`; production profile remains zero per BUILD-150 notes. | Direct dated policy exists; no inferred product value. |
| Restart result counters remain lifetime totals unless Lead changes that contract. | No direct decision row found in current `DECISIONS.md` sampled sections. | `RESULT_COUNTER_SCOPE_S3.md` and `RESULT_COUNTER_SCOPE_S6_S7.md`; F8 restart logs show cumulative values. | Marked as an observed implementation fact with contract awaiting Lead; do not present as a product decision. |

No code or ledger status was changed in S6–S10.
