# DD14 package 01: production preflight fixture, source and test delivery for review (NOT built, NOT run)

Order: Codex X-268 / `Codex/DD14_PRODUCTION_PREFLIGHT_FIXTURE_PACKAGE_01.md`. Implementer: Claude. ONE NEW file, no existing Source, Build.cs, config, script, asset or pack file touched. Nothing was built, no UHT, no automation, no engine process, no git operation.

| item | value |
|---|---|
| new file | `Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp`, 673 lines, CRLF, 0 bare LF, 0 bare CR |
| sha256 | `a418076bee99b76553fd61f3346917d499d7685ce8c26463b85752c35897e170` |
| diff | `one_file.diff` (new file against /dev/null) sha256 `3c260f6e7e3d5566f76132652efd4f9423f03951b2fb5bfb7ee0cf749bfb7cfa`; Review copy `Review/RPGBossProductionPreflightTests.cpp` (same hash) |
| manifests | `pre_source_manifest_sha256.txt` 177 files (equals the accepted DD13 `post_write_source_manifest_sha256.txt`), `post_write_source_manifest_sha256.txt` 178 files; `manifest_diff.txt` is exactly one added line (the new file); all 177 old files byte-identical |
| pins | `pre_pins.txt` 24 pins, all OK before and after (`post_pins_check.txt`); compiler `RPGEncounterBinding.h ce0a7da73e83...`, `.cpp c7255051e5f6...`; preflight `.h ba91b5a79e68...`, `.cpp b1742b5c9410...`; DD13 tests `37dac0a5bf66...`; native consumers Stagger `c711d766b4fe...`/`7cfaaadbc339...`, Phases `c43615412e1f...`/`0887f37564a2...`, Encounter `dc149393f2ff...`/`4f3ab203562e...`, DormantWake `fd3df15b1530...`/`ff450db792f5...`, Posture `b26e184b0410...`/`bca70f5816a4...` |
| baseline | HEAD `79d55906d155574a0c308b33d4442f4a7acbf8b9`; DLL `d6dfb9aaf0f109e638245814e355fcd931ad3e2d516d7dc671eaccc2e7767336`, exe `5495fb88c31c1546a01329165d4bbe697671176dd263ee46f57ff2e3c9c34b65` (`pre_binary_sha256.txt`); no engine, build or compiler process present |
| candidate assets | `candidate_assets_sha256.txt`: sha256 of the 14 `.uasset` files the fixture uses or reads (the two Blueprints, `SKM_CombatMannequin_Simple`, `SK_CombatMannequin`, the 7 boss/player clips, the 3 montages) |

## Tests (exact names)

1. `OneBossFight.Binding.ProductionPreflight.PositiveBatch`
2. `OneBossFight.Binding.ProductionPreflight.DependencyRejections`

Both `EditorContext | ProductFilter`. Expected discovery if released: 2 focused; full suite 108 + 2 = 110 (to be counted from the run, not assumed).

## What the fixture is

- The two pack character Blueprint classes (`BP_CombatPlayerCharacter_C`, `BP_ExampleGreatSwordBoss_C`, quoted literals under the always-cooked `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints`; the only two quoted `/Game/` literals in the file) are loaded ONLY to read `GetMesh()->GetSkeletalMeshAsset()` of their default object. No Blueprint actor is spawned, no default object is written, nothing is saved.
- The OBSERVED meshes are put on two isolated native `ACharacter` actors (deferred spawn, mesh set before finish) in a test-local headless game world that never begins play. The skeletons are the skeletons the observed meshes report (no skeleton path literal; the mannequin folder is not an always-cooked directory).
- Two transient `URPGBossDefinition` objects with valid typed values: the typed records are set explicitly to the authoring defaults (the cooked-directory candidates), the phase list (`PhaseTwo`), stats and the 51 manifest rows are FIXTURE values (not authority; each row says so). Boss animations: nine paths from the dormant wake, phase dependency and stagger profile records (dormant, wake, roar, three montages, fall, down, riposte boss reaction); player animations: the riposte player clip. Content epoch: the existing `RPGCombatRegistry::Legacy()`.
- The genuine production compiler `RPGCombatHydration::CompileParticipant` (bSyntheticFixture false) loads the skeleton and every animation; then `CompilePreflight` runs boss (BossCore, explicit phase id `PhaseTwo`) plus player (TargetOnly).

## PositiveBatch asserts

Actors are native `ACharacter`, hold the observed meshes, have not begun play, hold no managed consumer; boss and player skeleton `IsCompatibleMesh` their mesh (a mismatch fails with the observed names); both production compiles succeed (a failure prints the compiler's exact errors); configs are production (not synthetic), distinct, lease the very content epoch, retain the loaded skeleton the mesh reports and every listed animation (9 and 1), each animation a valid lease with `GetSkeleton() == Skeleton`; `CheckCompiledDependencies` accepts both; the batch compiles: scope marker `ExpandedNativeSubsetPreflight`, IsCompletePlayableBundle/IsReservation/IsReady false, world/encounter/content lease retained, 2 participants in request order, slots/targets/roles/actors, the very config leases, 5 boss plans in the order Stagger, Phases, Encounter, DormantWake, Posture with the legacy instance names and bound callbacks, the union of required paths equal to the 51 independent literals, 5 class leases, the target has 0 plans and 0 leases; a repeat compile gives another plan object; the world state (component counts, begun flags, managed consumers, context counts) is unchanged, no consumer created, the touched packages' dirty flags unchanged across the preflight, the CDO meshes still the observed objects. Everything observed (class, mesh, skeleton, each animation and its skeleton, and what was in memory before the fixture) is logged with `AddInfo`.

## DependencyRejections asserts

From the SUCCESSFUL real-asset result: an unmutated clone is accepted (control); then one change at a time, each refused with `Preflight.ProductionPrerequisite` plus the detail text, the earlier valid plan cleared, world state unchanged: null animation lease #0; no animation; no compiled skeleton; a transient animation on a transient skeleton appended (negative control, "belongs to skeleton"); the compiled skeleton replaced by a transient skeleton ("not the compiled skeleton"); a native character with no mesh (mesh reason only, no animation reason). Then the production compiler itself from the same definitions, with the output pre-set to a valid config (must be cleared and nothing published): no skeleton reference and no animation reference ("required skeleton/animation dependencies missing"), a null animation reference after the real ones and a transient skeleton that is not the animations' skeleton ("animation/skeleton identity mismatch"). Finally: world state and touched-package dirty flags unchanged, the successful configs and the earlier plan untouched. The transient skeleton/animation are negative controls only; nothing is retargeted, substituted or weakened.

## Judgement calls (please confirm or change)

1. The player and boss meshes are what the two class default objects report. My offline name scan of the two Blueprint packages shows `SKM_CombatMannequin_Simple`, not `SKM_CombatMannequin` as the A165 table lists; the test reads the real value and logs it, it does not assume either (offline scan only, not runtime proof). All 10 default boss/player clips and montages import against `SK_CombatMannequin` by the same offline scan; the runtime pairing is exactly what the test establishes or fails with names.
2. The nine boss animations include the three pack montages (A165 lists them as candidates); if one is on another skeleton the positive batch fails with the exact name, which is the intended evidence, and nothing is dropped to make it pass.
3. The boss and player share one definition shape (the player definition carries the same defaults); only the target-only member role differs.
4. The dirty-flag check covers the preflight and the negative cases only; the class load, spawn and production compile precede the first snapshot (stated in the code and here).

## What this does NOT establish

A cold load (the pack classes load first; what was already in memory is only logged), the packaged or cooked build, the arena level or the placed Blueprint boss, abilities and effects (class paths structural only), animation playback or root motion, the authored boss definition (typed values, phases and rows are fixture values), a game-instance content epoch, a mesh of another skeleton on a real character, a missing-asset reference (it would log load warnings), a retargeted dependency, BeginPlay, registration, context binding, startup, activation or any wiring, the death/presentation/audio systems, the 40-row gate. The result is still an expanded native subset: not a complete playable bundle, not a reservation, not Ready.

## Independent read-only pass (not by me) and what it changed

One compile and logic review of the file against the UE 5.5 headers and the project sources found no compile-severity issue and verified every expected failure string against the compiler and kernel text. Two findings were fixed before delivery: (1) the bare character was spawned after the state snapshot, which would have made the final state comparison always fail: it is now spawned before the snapshot; (2) the dirty-flag claim was wider than what is measured: comments narrowed. The state before these two edits was not preserved as a separate copy (the diff is against the final file); the two edits are exactly the ones named.

## Next, when you release it

Fresh safety; UHT only if invoked (a new .cpp with no reflected types: not expected, report the actual output); build; focused `OneBossFight.Binding.ProductionPreflight` (expect 2); full suite only if clean (expect 110, `OneBossFight.Content.CookCoverage` passing); exact diagnostics; manifests and pins after; stop on any failure with the first failing source and logs preserved.
