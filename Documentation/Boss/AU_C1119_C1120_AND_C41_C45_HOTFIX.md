# AU C-1119/C-1120 hotfix and AU-C41–C45 batch handoff

## Claude findings and offline corrections

- **C-1119 parry watcher:** the natural DATA-route A4 montage can run without the Python tracker reporting `A4`/active. The driver now emits one `PARRY_DIAG` per boss-montage transition with tracker move, instance, active state and position, plus sweep state/count. A live `GS_Attack04_Montage` together with `RPGBossLowSweep.IsBladeActive()` is accepted as the alternate live-window witness, using the sweep count as its instance ID. The watcher timeout marker is deduplicated by action slot. These changes do not claim a parry; only the sweep's exact parried-count increment records contact.
- **Scope caution:** `RPGAttackTracker.cpp` maps `GS_Attack04_Montage` to `A1b`; its separate A4 entry uses `AN_Boss01_A4_LowSweep`. Therefore the montage name alone is not treated as A4, and the fallback additionally requires the sweep component to report active. Claude's Lead rerun must verify this pairing before any natural A4 is claimed.
- **C-1120 runner:** `RunLeadPie.ps1` now splits each `-Env` string on commas, validates each `NAME=value`, rejects route-owned variables, applies each parsed value separately, and prints each applied value. Its dry-run contract verifies the same `-Env FIGHT_MAX=30,FIGHT_RUN=test` form Claude used.
- **C-1120 aura captures:** replaced the fixed three-frame warmup for approved and candidate captures with pixel-driven warmup. It discards up to 20 decoded frames, stopping when mean gray reaches 5; total warmup is capped at four game seconds. If the floor is never reached, capture fails closed before the approved comparison frame. A fake capture sequence proves retry-until-visible and max-frame failure.

## AU-C41–C45 offline work

- Added `fight_review_observation.py` to validate human-coded `seen`, `not_seen`, `obscured` and `inconclusive` states against same-run frame IDs. Seen/not-seen require decoded-frame review; component activation cannot replace visual evidence. Obscured/inconclusive require a reason. This validator does not create review verdicts.
- Full-fight frame capture now emits `FRAME_CONTEXT` tied to the same run/frame/action/time, with player/boss framing estimates, whether the camera lies inside a boss component bound, and `world_occlusion=UNMEASURED`. A point projection is diagnostic only; it does not claim pixel visibility or world clearance.
- Added a static guard that all seven owner checklist rows remain blank and the editor scripts do not write the owner review file.
- Updated BUILD-259 technical guide and owner review pack to separate BUILD-255, BUILD-259, focused PIE, and standalone showcase evidence and to keep owner visual choices in the owner checklist.
- **AU-C45 remains Lead-owned:** one readable move frame and one obscured-camera case still require a focused PIE capture with the build ID, raw log, matching frame-context/frame PNGs and route witness. Codex did not launch Unreal or render media.

## Verification

The C-1119/C-1120 hotfix regression set and AU offline suites pass **72/72**. Python syntax compilation and `git diff --check` pass. No Unreal/Editor/PIE/build/package/commit/push was run by Codex.

Lead capture recovery and AU-C40/C45 runtime receipts remain separate pending gates. No owner box, visual selection, source asset or production camera behavior changed.
