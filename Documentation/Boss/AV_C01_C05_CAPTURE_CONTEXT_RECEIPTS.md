# AV-C01–C05 — capture context and warmup receipt hardening

## Implemented offline

- `fight_capture_receipt.py` now requires exactly one `FRAME_CONTEXT` per `FRAME`, checks run/frame/action/time identity, coordinates, framing states, and explicit occlusion status. `world_occlusion` must remain `UNMEASURED` or `UNKNOWN`; historical pre-context logs cannot be silently upgraded. The JSON receipt now returns each frame's linked context.
- Camera projection and point-in-component-bounds calculations are pure, testable helpers. Non-finite geometry or unusable FOV yields `UNKNOWN`; the center-point projection is only a framing estimate, not a visibility verdict.
- The receipt checker validates parry montage-transition diagnostics, one timeout marker per action slot, and the live-sweep condition on the montage fallback. `GS_Attack04_Montage` by itself is rejected as A4 evidence.
- Aura manifests record game time. `aura_warmup_receipt.py` checks that approved/candidate PNG records follow same-run, same-route warmup frames, achieve decoded mean-gray >=5 within 20 frames and 4 game seconds, and keep the target frame within the same bound. Missing, black, stale, delayed, or non-finite evidence fails closed.
- Refreshed status handoff remains tied to currently received Lead evidence; no new source-pixel or PIE claims were added. Seven owner checklist fields remain blank.

## Verification and limits

Focused AU/AV combined offline contracts: **78/78**. Changed Python modules compile and `git diff --check` passes. No Editor/Unreal/PIE/build/package or media render was run by Codex. AU-C10/C15/C25/C30/C40/C45 runtime evidence and owner visual choices remain open; this batch validates receipts only.
