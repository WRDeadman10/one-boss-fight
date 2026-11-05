# F-A1 — BOSS-QA-001 runtime overlay viewport witness

Requirement source: `Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json` v3.36, row `BOSS-QA-001`. The row remains PARTIAL because a real game-view PNG has not been witnessed. Existing F8 PIE logs prove telemetry states but do not prove visible pixels.

## Setup

Use existing map `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF8`. Confirm the framework proof profile resolves and the run reaches idle/committed/active states. Do not modify assets. The F4 PIE command captures logged overlay fields; the existing standalone capture helper captures actual game viewport pixels. Lead runs both with no engine process or `ENGINE_LOCK.json` present.

PIE telemetry command (PowerShell from `Docs/BossCombatReview/Execution/Claude/F4`):

```powershell
.\run_pie.ps1 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF8 -OutDir "$PWD\..\..\Codex\F_A1_QA001\pie_overlay_on" -Task F-A1_QA001_overlay -Console "rpg.BossOverlay 2"
```

Paired control: repeat with `-Task F-A1_QA001_overlay_off -Console "rpg.BossOverlay 0"`; ordinary combat must continue and logged overlay lines must be absent.

For the required visible game-view image, from `Docs/BossCombatReview/Execution/Claude`, use the existing owner/Lead helper (no new content script or asset authoring):

```powershell
.\B_QA001\run_game_shot.ps1 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofQA001 -OutDir "$PWD\B_QA001\F_A1_owner_run" -Task F-A1_QA001_viewport -ShotPath "$PWD\B_QA001\F_A1_owner_overlay.png" -At 6 -ShowUI 0
python -I .\B_QA001\png_stats.py .\B_QA001\F_A1_owner_overlay.png
```

The screenshot route requires a connected desktop session; if unavailable, retain the PIE log package and mark the screenshot criterion BLOCKED, not passed. Keep raw log, PNG, result JSON, and command line together.

## Control

The overlay-off PIE run is the paired control. Confirm it reaches a normal proof result without `[FrameworkProof] overlay` lines. The positive screenshot must be from the game viewport, not the editor viewport or a black/headless capture.

## PASS

- Positive telemetry log contains `[FrameworkProof] overlay` with `Card`, `State`, `Phase`, `Range`, `Cone`, `Window`, `Posture`, `Health`, `Stagger`, and `PhaseHold` fields; observed sequence includes idle, committed/active, and any states the current map naturally reaches. Do not require phase 2 if this selected map/profile does not enter it.
- Positive standalone log contains `[FrameworkProof] screenshot_requested` and `[FrameworkProof] screenshot_quit`; the PNG opens as 1280x720 and is manually readable as game-view content.
- `png_stats.py` reports `nonblack_fraction > 0` and `yellow_overlay_pixels > 0`; these are image sanity checks, not a replacement for visual inspection.
- Paired control has no overlay line and no visible yellow overlay while normal combat continues.

## FAIL

Fail or classify BLOCKED if the F8 profile/map is unavailable, the required overlay fields are absent, the screenshot is missing/black/unreadable, the control still shows the overlay, normal combat changes under the diagnostic toggle, or the engine/lock guard refuses the run. No screenshot means the ledger row remains PARTIAL even if PIE log tokens pass.

## Token checks

- Positive PIE: `[FrameworkProof] overlay` schema and required key/value fields.
- Negative PIE control: no `[FrameworkProof] overlay` line.
- Standalone positive: `[FrameworkProof] screenshot_requested`, `[FrameworkProof] screenshot_quit`.
- Verify each token against `Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py`; don't treat an unrelated editor screenshot token as the game-view image.
