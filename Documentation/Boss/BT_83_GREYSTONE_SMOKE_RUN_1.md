# BT-83 Greystone visual smoke: run 1

Date: 2026-11-17 (Asia/Kolkata)
Approval: Owner approved one no-save C-1155 visual-state smoke on `/Game/OneBossFight/Maps/L_SevarogArena`. The approval envelope is at `Saved/GreystoneVisualSmoke/OwnerApproval_a87434f6c3f44fd58cb1db3747dcc3b7.json`; run token `a87434f6c3f44fd58cb1db3747dcc3b7`.

## Bound sources

| Source | SHA-256 |
|---|---|
| `Scripts/Editor/run_greystone_visual_smoke.ps1` | `D485ED22A78DD84DE6F22941294D6D7C5208585CB9343A75B1BCB7DB6AEE5887` |
| `Scripts/Editor/pie_greystone_visual_smoke.py` | `68CF485F54858B943A5D7B1DE2D209768898E0F143B79E550D06B35836EB4AF1` |
| `Source/OneBossFightEditor/Private/RPGGreystoneRuntimeRetargetLibrary.cpp` | `22A04C1A5B12AAC1A045EC33AB2E346064D55FBABA83FA5E25FA2E749C5778AF` |
| `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp` | `60097589BA1FAF3C12827ECDF6AC0FD32651EA3AA292EF25C17AB1878D7FB838` |

## Outcome

- Runner exit code: `1`; the smoke receipt is `FAIL`, `accepted=false`.
- Receipt: `Saved/GreystoneVisualSmoke/Run_20261117_161913_a87434f6/receipt.json`.
- Log: `Saved/GreystoneVisualSmoke/Run_20261117_161913_a87434f6/editor.log`.
- Failure: `PIE game world lost while waiting for possession`. The map identity was correct, but the expected pawn was never observed; source/visible mesh criteria therefore failed. `GetMainAnimBP` error count was 0, continuous log monitoring passed, and CVar readback confirmed `rpg.GreystonePlayerTestPawn=0`.
- The wrapper's 60-second deadline expired about 7 seconds before the log reported `PIE_WORLD_FOUND` (~67 seconds after process start). The wrapper then requested graceful Editor shutdown; the PIE world disappeared before possession was observed. This timing makes the short cold-start deadline the likely cause; it is an inference from the runner deadline and log timestamps.
- The shutdown request initially left the Editor process alive, so the wrapper retained both C-1155 locks. After the Editor exited, Codex verified no Editor process remained, `DefaultGame.ini` still had SHA-256 `5DE691FCA4E0FA375F6F262FA6BA402FEFA7AB9A0B567AE2146E6823F69EDEC8`, and both lock records belonged to this exact token, then released those two locks. Final recovery state: no Editor process, no locks, config unchanged.
- The independent receipt validator correctly rejected the receipt because pawn/component evidence and the corresponding required log markers were absent. No assets were saved, no configuration was changed, and no build was run.

## Follow-up

BT-86 is assigned to Antigravity for a source-only cold-start timeout hotfix. No retry is authorized by the one-run approval. After BT-86 review, a new owner approval must bind the updated runner hash before another Editor/PIE run.
