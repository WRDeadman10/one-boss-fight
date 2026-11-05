# Failure catalogue telemetry cross-check (S134)

Reviewed `Docs/BossCombatReview/Execution/Codex/Proofs/FAILURE_MODE_CATALOGUE.md` against current schemas in `validate_framework_proof_logs.py` and the C++ emission paths. Every named FrameworkProof token in the active catalogue rows is registered and has a source emission: warp (`warp_ease`, `warp_step`, `warp_summary`, `warp_blocked`), strafe (`strafe_start`, `strafe_stuck`, `strafe_budget_restarted`, `strafe_end`), yaw/cone (`yaw_probe`, `cone_hysteresis`), guard chip, parry recovery/stamina/tag, telegraph scale/restore, aggro switch/dodge injection, fatigue, and overlay. Non-FrameworkProof diagnostics such as `parry_tag` are emitted by `RPGPlayerParry.cpp:200` and are explicitly used as corroborating logs.

## Finding — BUG (corrected)

The WarpEaseInOut wrong-card/profile/map row said `playback_start` identifies the active card. Current `RPGFrameworkMoveExecutor.cpp:172` emits encounter/generation/instance, montage path, slot, rate, and label; it does **not** emit the card ID, map, or profile. The row now states this limitation and points to `telegraph_scale card=...` only when the separate telegraph opt-in is active (`:141`). Map/profile identity must come from an authoring readback or external run manifest, not playback telemetry. Thus the previous diagnostic could not identify the claimed cause from that token alone.

This review verifies token registration/emission and the cited diagnostic meaning; it does not establish that any listed failure happened in a live run. No tests, build, or Unreal session were run.
