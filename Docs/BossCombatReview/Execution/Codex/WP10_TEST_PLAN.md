# WP10 — tests and acceptance backlog

2026-10-25. NOT BUILT / NOT RUN. Two staged automation files and two staged Python drivers; no runner table changes. Nominal driver counts are planning values, not test results.

## Authored tests

`OneBossFight.Binding.DraftWorldIsolation`: real standalone UWorld creation, two simultaneous contexts sharing metadata, value snapshot independence, strict missing-content refusal/no substitution, explicit targets, foreign handle rejection, configure-before-register, repeated attach refusal, actual CollectGarbage, generation invalidation, encounter-local unbind, one world teardown and recreation while the other survives. Uses synthetic plain actors/config/native component; NOT two pack fights and NOT seamless travel.

`OneBossFight.Timeline.DraftCrossings`: malformed identity/hash/segment map/duplicate/empty rejection; two trace windows; start0, exact endpoint, fully skipped windows on hitch, duplicate samples, stop twice, same-asset new instance, generation change, reverse/jump/loop explicit inconclusive, independent cursor/teardown and uncertain instance metadata. Synthetic trace labels are explicit, never presented as frozen live replay or new gameplay results.

`pie_encounter_binding.py`: guarded fixture diagnostics, fresh legacy/auto/data and strict-invalid PIE sessions, explicit >=4-participant/two-encounter fixture requirement, ready/unique keys, real GC, end-PIE world teardown and new session identity. Nominal36 assertions on the success path. Strict-invalid expects zero ready components, not legacy fallback. It does not author a fixture or assign component properties. Existing arena has no binding fixture yet: failure there is EXPECTED and must not be counted as a new product regression.

`pie_timeline_shadow.py`: passive >=2-shadow fixture diagnostics, natural nonzero sample coverage, per-instance bounded records/no drops/GC/teardown. Nominal7 assertions. Does not wake/force an attack or invent natural coverage; zero samples fails coverage only. Does not prove off/on hit parity or write a fabricated run header.

Both drivers have wall-clock deadlines (100/70s), heartbeat10s, exception -> failing assertion, cleanup/unregister/end-PIE, `RESULT n/m passed`. Binding restores each touched cvar independently. No component set_editor_property, map load or asset authoring. RunDrivers entries would use at least Min36/7 and timeout120/90 only **after actual count/readiness verification**; not added now.

## Still required — not authored/proved by these diagnostics

EDITOR NEEDED: fixture content/readiness trace, placed vs deferred late spawn, pre-existing registered consumers, duplicate/missing target/config batches, foreign/ambiguous binding, target death and new player pawn rebind, actual live first reads and all D01 fields. The current no-live-rebinding policy needs an explicit lifecycle adapter for respawns before parity acceptance. This cannot be waved away by a standalone world test.

Real travel (OpenLevel/seamless as applicable), retained GI epoch across world teardown, actual soft dependency GC/cook, two simultaneous real encounters with separate targeting/HUD/camera/music/fog, all source modes with malformed asset/unknown schema/missing dependency cases remain open. Do not call PIE stop/start a travel proof. Network authority/canary evidence remains required in its approved delivery phase, never N/A.

Manual capture checks per C119/AG17: feet relative to a measured floor (not capsule-bottom or bounds proxy), greatsword hand/hilt grip continuity and victim clearance, actual production trace vs visible blade, and root/mesh/actor velocity plus motion ownership/foot sliding. Exact2cm floor tolerance or18-22cm hilt spacing is NOT silently adopted as a new owner requirement from AG's recommendation. Root-motion and movement speeds need a consistent coordinate/time domain, not an assumption that their magnitudes must always equal. A shared skeleton pointer cannot prove these physical properties.

Shadow still needs actual notify export -> artifact import, section/dynamic montage map fixtures, active blend/multiple montage visibility, unknown variant coverage, overflow/report schema/header validation/flush I/O tests, read-only delegate across ALL early returns, reset/destroy unsubscribe, GC of leased animation assets, source/artifact hash invalidation, trace replay against independently derived AG16 expected values, **observer off/on actual outcomes** and full integration. No observer cvar is implemented, so don't claim it was toggled. Compare identical presets/seeds/commands and actual damage/release/state/counters/rotation/asset hashes; differing logging/timing conditions invalidate temporal comparisons.

## Commands for Claude only

After reviewed promotion with complete integration seams and fixture: close editor; `powershell -ExecutionPolicy Bypass -File Scripts/Rebuild.ps1 -Tests`. The normal command runs all OneBossFight automation including the new tests. Start editor -nosound, warm it, keep unminimized, then run the promoted drivers with the existing `Scripts/run_in_editor.py` workflow. Drivers under Drafts can also be passed explicitly, but will fail until fixture/native code exists. No engine commands executed by Codex.

Preserve existing focused witnesses: pie_builds103, pie_build_select18, pie_build_hud, pie_build_hyperarmor, pie_flask_hud, pie_hyperarmor, pie_dormant_wake, pie_damage_path, pie_boss_encounter, pie_player_death_reset, pie_soak, phase/posture/riposte/death/fog/attack/trace/telegraph drivers. The **entire current RunDrivers table** stays the regression contract, not only this subset. Separate Claude's C113 stale-test fixes and WakeClip0 correction from DD1 changes. Record baseline/current raw results and DLL identity; no inferred passes.
