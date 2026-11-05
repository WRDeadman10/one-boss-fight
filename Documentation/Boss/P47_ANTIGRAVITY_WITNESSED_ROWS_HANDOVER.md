# Queue P47 handover: witnessed rows for Antigravity

Evidence paths below were checked in the workspace. BUILD IDs and witness scope are transcribed from `Documentation/TEST_PLAN.md`; this handover does not edit the Antigravity ledger.

| Ledger row | BUILD evidence | Current witness | Evidence folder |
|---|---|---|---|
| BOSS-AWR-004 | BUILD-146 implementation; BUILD-170 live flicker pair | Live cone-edge retention in one matched control/hysteresis pair. Test covers flicker; BUILD-170 used only 2 of 24 yaw samples. | `Docs/BossCombatReview/Execution/Claude/B_YAW_CONE/` |
| BOSS-MOV-001 | BUILD-199 live | Four-map range-family selection at 102.87, 254.76, 380, 701.92 cm; expected Close/Medium overlap included. | `Docs/BossCombatReview/Execution/Claude/B_FAG5_MOV001/` |
| BOSS-HIT-008 | BUILD-203 live | Guarded contact applies chip (20 incoming, 5 applied) and does not apply full health damage; parry evidence is a separate prior run. | `Docs/BossCombatReview/Execution/Claude/B_FAG4_HIT008/` |
| BOSS-COM-004 | BUILD-204 Guarded/Hit; BUILD-208 Parried | Distinct Guarded -> D, Hit -> B, Parried -> E branches witnessed on root A. | `Docs/BossCombatReview/Execution/Claude/B_FAG23_COM004/`; `B_LIVE_20261104b/` |
| BOSS-SEL-008 | BUILD-208 live | Blocker/control pair shows strafe-stuck flip and eligible resume; no-wall control has no stuck event. | `Docs/BossCombatReview/Execution/Claude/B_SEL008_STUCK/`; `B_LIVE_20261104b/` |

All six evidence folders exist. Their checked `evidence_sha256.txt` manifests verified 269 listed files with zero missing files or hash mismatches (44 + 36 + 15 + 95 + 43 + 36). The mailbox/TEST_PLAN notes say the v3.36 ledger update remains Antigravity-owned; no WITNESSED status is asserted here beyond the Lead's explicit BUILD verdicts.
