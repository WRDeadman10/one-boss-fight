# E130 — aggro-band production eligibility

**Decision needed:** whether any shipped proof/profile should opt into aggro-band selection. **Authority:** project owner for profile/feature rollout; implementation already preserves default-off behavior.

The profile flag defaults off (`RPGBossFrameworkProfile.h:102`). When enabled, the framework boss gathers dodge observations and steps the band at selector decisions (`RPGFrameworkBossCharacter.cpp:124-131,443-450`), then selector context maps Close/Far to authored hug/kite multipliers (`RPGBossMoveSelector.cpp:63-66`). The helper is separately covered by pure tests; Queue E D96 tests pin transition edges, but those do not establish a shipping profile choice. Keep the flag off in production content until the owner approves the exact profile and intended weights. No new code is required for this audit.

Static source/doc audit only; no build or tests run by Codex.
