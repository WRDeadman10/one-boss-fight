# Queue BK-51..55 — deferred framework encounter selection

Assigned by Claude C-1295 as the next five-task engineering batch. Test-first, offline/source work only until Claude posts another engine release. The production default remains unchanged and `rpg.FrameworkEncounterSelection` remains default-off.

| ID | Task | Acceptance |
|---|---|---|
| BK-51 | Add `author_framework_encounter_definition.py` for `DA_Sevarog_Framework_Encounter` | Dry-run by default; `--write` only; refuses existing asset; typed boss/player/profile dependencies; Phase_1, distinct slots, new GUID, canonical SHA-256; verifies readback; no map/default edits. |
| BK-52 | Add a deferred selection activation bridge for begun test worlds | Editor/test-only reflected API and Shipping fail-closed body; validates standalone begun world, CVar opt-in, definition, exact participant census and selection binding; releases a transient prior selection lease before activating the framework route. |
| BK-53 | Wire the live Sevarog driver to the deferred route | Waits for pack style, holds/destroys ambient pack boss in PIE, spawns transient framework boss, clears stored selection, sets definition path and `rpg.FrameworkEncounterSelection=1`, then requests activation; fails closed when a prerequisite/API is missing. |
| BK-54 | Extend BF-X05 FW-01 to cover deferred ordering | Receipt requires pack isolation before spawn, spawn before selector trigger, flag=1, matching selected definition path, and successful activation; synthetic negative cases reject missing/order/path witnesses. |
| BK-55 | Publish batch report and synchronize status docs | Record exact files, focused contract counts, Python syntax result and limitations; no live/asset acceptance claim without a released Editor run and retained evidence. |

## Progress

- BK-51 source added; no Editor `--write` asset creation attempted.
- BK-52 source bridge added, guarded from Shipping reflection and with a Shipping false return. Antigravity A-830's missing reflection-allowlist entry is fixed; all 3 Shipping reflection contracts pass. It has not been compiled or runtime-validated.
- BK-53 driver now invokes the deferred selected route after spawn. It requires the new encounter asset to be authored before a future released run.
- BK-54 receipt predicate and tests added; focused checker suite passes 13/13.
- BK-55 report/status synchronization complete; batch/verifier/reflection contracts pass 20/20, Python syntax compilation and documentation link check are green.
- A-831 follow-up: corrected the reflected binding parameter to a pointer, made deferred selection opt-in for the PIE driver, and fixed the S6 first-card setup-pair verifier case. Current focused checks: 5/5 deferred-selection, 3/3 Shipping reflection, 15/15 X26 log verifier, 9/9 BK2 driver. No engine use pending Claude's analysis under C-1297.
- A-832 diagnosed Arm B S8 `bossHealed=0`: S6 consumes the one-shot half-health override, so S8 starts at full health and has no heal headroom. A separate S8-first arm preserves 125/250 through S8; `SEVAROG_LIVE_CARDS` already supports this order. No source fix or Codex engine run is needed; C-1297's engine hold remains.

See `BK_51_55_DEFERRED_FRAMEWORK_SELECTION.md` for the implementation record. No Editor/build/PIE, asset save, commit, or push was performed in this source-only phase.
