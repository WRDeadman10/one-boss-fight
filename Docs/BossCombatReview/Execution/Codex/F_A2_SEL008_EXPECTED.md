# F-A2 — BOSS-SEL-008 no-candidate fallback live witness

Requirement source: ledger v3.36 row `BOSS-SEL-008` (PARTIAL). Existing B_MOV PIE proof already records `reposition attempt ... reason=NoCandidate`, navigation, a walk back into band, and a later reposition turn. This run refreshes that behavior through the required F4 driver and keeps the remaining continuous-neutral-strafe gap explicit; it cannot alone change the ledger to WITNESSED.

## Setup

Use existing `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofMOV` and its `DA_Sevarog_RepositionProof_MOV` setup; no assets or content scripts are changed. Run from `Docs/BossCombatReview/Execution/Claude/F4`:

```powershell
.\run_pie.ps1 -Map /Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofMOV -OutDir "$PWD\..\..\Codex\F_A2_SEL008\no_candidate" -Task F-A2_SEL008_reposition -Console "rpg.BossOverlay 2"
```

The overlay command is diagnostic-only. Keep the full raw log and result files. Do not set `RepositionMax` or move the target by console; use the authored existing MOV proof map so the existing no-candidate condition occurs naturally.

## Control

Use the retained matched control `Docs/BossCombatReview/Execution/Claude/B_MOV/pie_run2/editor_raw.log` as historical reference, and in the new run verify ordinary eligible-candidate decisions/playback before and after the no-candidate event. The control must not trigger reposition when a candidate is eligible.

## PASS

- Log contains `[FrameworkProof] reposition attempt=... reason=NoCandidate` only after candidate refusals/no choice.
- The boss issues a navigation request, emits `[FrameworkProof] walk start`, reaches its authored band, then continues selection/playback rather than remaining frozen.
- If present, `[FrameworkProof] reposition_turn start` occurs only after band arrival; the later selected-card/playback token follows.
- Report whether the map naturally exercises continuous strafe. The current ledger says continuous neutral-strafe is not built; do not reinterpret reposition/walk-back as proof of strafe.

## FAIL

Fail if a candidate was eligible at the no-candidate marker, the walk/navigation request is absent or fails, the boss remains stuck/frozen after the bounded attempt, or a new engine/target fault occurs. If the walk-back succeeds but continuous strafe remains absent, pass only the narrow reposition sub-proof and leave BOSS-SEL-008 PARTIAL.

## Token checks

- `[FrameworkProof] refusal ... reason=MoveModel.Range` (or other named refusal) for every candidate at the gate; verify no chosen candidate precedes the no-candidate branch.
- `[FrameworkProof] reposition attempt=... reason=NoCandidate`.
- `[FrameworkProof] nav request=...` and `[FrameworkProof] walk start=...`.
- `[FrameworkProof] reposition_turn start ...` and a later `[FrameworkProof] playback_start` if the scenario reaches turn/redecision.
