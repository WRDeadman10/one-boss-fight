# E126 — integer extremes public contract

**Decision:** None required for the current implementation. **Authority:** project owner if a future runtime rule must choose a new saturation/refusal contract.

The D91 audit identified signed multiplication overflow in flask fill and unchecked finite-result edges in leash/yaw/strafe/track helpers. C-757 and C-771 dispositions now widen flask products (`RPGFlaskHudRules.h:28`), fail closed on nonfinite leash geometry (`RPGBossLeashRules.h:11-15`), and guard computed yaw/hold/ring/grounded outputs (`RPGBossYawProbeRules.h`, `RPGBossStrafeRules.h`, `RPGBossTrackRules.h`; summarized in `BOSS_RULE_FINITE_INPUT_AUDIT_D91.md`, C-771 disposition). The bleed proc counter also saturates at `MAX_int32` (`RPGBleedRules.h:68`; `RPGCodexTests.cpp:98-99`). The public contract is therefore already conservative at the audited numeric boundaries; no new project policy is needed. Do not widen accepted domains or change fallback behavior without an owner decision.

Scope is static source/document review only; this records no build or test result.
