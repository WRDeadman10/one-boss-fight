# AK-C21–C25 — ER owner content audit

| Task | Checked result |
|---|---|
| C21 | `ER_PLAYER_CONTROLS_SPEC.md` now distinguishes C-1021 owner reel approval and BUILD-255's four nonempty `AM_ER` Source defaults from C-1004's earlier runtime-only air-hit assignment. A fresh default-wired PIE and package gate remain open. |
| C22 | `GATE07_ANIMATION_REVIEW.md` rows for Backstep, GuardCounter, AirLight and AirHeavy now show owner reel approval / Source wiring rather than pending owner review. The retained readbacks are Backstep 0.4667 s, GuardCounter 0.8000 s, AirLight 0.6000 s and AirHeavy 0.8667 s; these agree with the review pack's rounded lengths and the C-1003 T3D segment lengths for the three attack montages. Runtime proof after BUILD-255 remains open. |
| C23 | The owner pack links to the reel, four ER review MP4s and strips, and three Tier 2 rows. `python Scripts/Tools/check_doc_links.py` reports `broken_links=0` across Documentation. The pack's own heading still describes a staging review pack; Antigravity owns that page's status wording after C-1021. |
| C24 | Saved `Saved/C1003_t3d/` exports put `StrongMeleeAttackData` on the AirHeavy and GuardCounter `ANS_CollisionTrace_C` notify subobjects (lines 15 and 28) and no AttackData override on AirLight. C-1004 r5 reports both-route AirLight -16.0 HP / JumpLight / Default and AirHeavy -22.4 HP / JumpHeavy / Strong. That proof predates default wiring. |
| C25 | Owner clip approval and Source default wiring are complete as reported in C-1021/BUILD-255. Remaining gates: fresh default-wired PIE for backstep, both air attacks and guard counter; live guarded-contact/hit proof for KI-198; package/cook proof for KI-193; separate Tier 2 in-game visual/runtime acceptance. |

No asset, engine, build, PIE, package or commit operation by Codex. The Lead holds `ENGINE_LOCK` for full-fight capture.
