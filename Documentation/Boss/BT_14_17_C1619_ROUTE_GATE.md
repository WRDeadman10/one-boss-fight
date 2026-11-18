# BT-14..18 C-1619 route gate

Date: 2026-11-16

## BT-14 — current-hash build and suite

Task runner: `Scripts/Editor/run_c1619_route_build_locked.ps1`
Run: `Saved/C1619RouteBuild/Run_20261116_102921_ba0e3216`

- Development build exit: 0.
- DD27j-pinned `OneBossFight` suite: 573 started, 573 passed, 0 failed; suite exit 0.
- Approved subsystem hashes matched at execution: cpp `D01F97E48CFBB419FE1AD67E839162651A55CEF4A8826452978B4C3F962B330A`; header `DA259E1A75E078350E06CFDFC1FE1AEDCD2F5872B62D00DA557975A98F6D82B6`.
- Both C-1155 locks were released; no PIE, package, cook, or asset authoring occurred.
- Runner emitted `route_lead_approval.json` for the matching source hashes.

## BT-15 — Smoke result

Run: `Saved/SevarogArenaRoute/Run_20261116_103119_a66bbdb0`

- Result: `FAILED`, runtime acceptance `BLOCKED`; failure was `FrameworkInitializationFailed`.
- Observed: placed pack boss suppression before BeginPlay (`began_play=0`, `montage_active=0`) and initial binding (`framework=1`, `pack=0`, generation 1).
- Runtime log line 1816 refuses the boss definition: `WorldInput.DefinitionRejected[slot=Boss]: required skeleton/animation dependencies missing`.
- Not verified because initialization stopped: live actor census, Boss HUD count, health 1500, and production Tick-selected card. Boss death is outside Smoke; raw BehaviorTree attack-task ticks remain `BLOCKED_NOT_INSTRUMENTED`.
- Runner restored `Config/DefaultGame.ini` byte-for-byte, closed the Editor, released both C-1155 locks, and saved no assets.

## BT-17 — saved definition dependency readback

Read-only runner: `Scripts/Editor/run_sevarog_dependency_readback_locked.ps1`
Driver: `Scripts/Editor/read_sevarog_definition_dependencies.py`
Run: `Saved/SevarogDependencyReadback/Run_20261116_104017_9359129f`

- Readback completed: `DA_Boss_Sevarog_Draft.Skeleton` resolves to `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton`.
- `DA_Boss_Sevarog_Draft.Animations` has 0 entries. This is the concrete cause of the runtime rejection; no animation skeleton mismatch is involved because no animation references are present.
- Runtime compiler rule is at `Source/OneBossFight/Player/RPGEncounterBinding.cpp:243-248`: the definition needs a valid skeleton, a non-empty animation dependency array, and every loaded animation must use that exact skeleton.
- Asset SHA-256 remained `A275DD487A405556B8BB15C7072ADCB2A6A7984BE6A34AEC87CAF193DE857908`; `DefaultGame.ini` hash was unchanged. Editor exited 0; both locks were released; no PIE/build/config/asset save occurred.
- Evidence is diagnostic only. The separate authoring task must bind the exact Sevarog sequences already referenced by the selected framework cards and verify them; do not borrow Boss01 or generic pack animations, and do not edit/duplicate/save under `/Game/ParagonSevarog/`.

## BT-18 — active-profile animation dependency repair

Locked runner: `Scripts/Editor/run_bt18_sevarog_definition_dependencies_locked.ps1`
Driver: `Scripts/Editor/repair_sevarog_definition_animation_dependencies.py`
Run: `Saved/BT18SevarogDependencies/Run_20261116_105405_427538af`

- Saved profile readback found 7 active cards and 7 unique sequences. All load and use the same `Sevarog_Skeleton` as the definition. The standalone S5 `Swing1_FAST_v2` card is not in the saved profile, so it was excluded.
- The only authored property was `DA_Boss_Sevarog_Draft.Animations`, set to those 7 paths in profile order. Fresh-process reload verified exact order, count 7, matching skeletons, and `non_target_fields_preserved=true`.
- Definition SHA-256 changed from `A275DD487A405556B8BB15C7072ADCB2A6A7984BE6A34AEC87CAF193DE857908` to `2FA84B22B88C78274E4309D3C2334D75B66932B0F1122AF2AC9727B23068FD13`. `DefaultGame.ini` hash remained `5DE691FCA4E0FA375F6F262FA6BA402FEFA7AB9A0B567AE2146E6823F69EDEC8`. Both locks released; no Editor remains. No build or PIE in BT-18.

## BT-15 retry after BT-18

Run: `Saved/SevarogArenaRoute/Run_20261116_105546_5571894b`

- The original animation-dependency refusal is gone. Smoke now refuses at production preflight because the native framework boss character has no mesh compatible with the compiled Sevarog skeleton: `Preflight.ProductionPrerequisite[slot=Boss]: a production member must be a character whose mesh is compatible with the compiled skeleton` (log line 1815).
- This is a new source/runtime integration gap. `RPGBossHydrationPreflight.cpp:453-458` validates the actual `ACharacter` mesh; `ARPGFrameworkBossCharacter` construction does not install the selected profile mesh before route activation.
- Binding, suppression and no-pack-montage evidence still pass. Actor census, boss HUD, 1500 health, and production selected-card evidence remain unverified. Boss death is outside Smoke and raw BehaviorTree task ticks remain uninstrumented.
- Runner restored config byte-for-byte, closed Editor, released both locks; Smoke made no asset saves.

## Next gate

BT-21 assigns Antigravity a source-only fix to bind `FrameworkBossProfile.Mesh` (and matching `AnimClass` as needed) onto the deferred framework boss before production preflight, refusing if those dependencies fail. BT-19 is lead review, BT-23 is the current-source-hash locked build and pinned suite, then BT-22 retries Smoke. Smoke still does not prove boss death or raw BehaviorTree task ticks, and it is not a playable packaged build.

## BT-25..29 health readiness follow-up (2026-11-16)

BT-25/26 source fixes and BT-27 four-source receipt integrity were accepted. BT-28 rebuilt the current source under C-1155: Development build exit 0; pinned DD27j suite 573/573, 0 failures; both locks released. Exact receipt: `Saved/C1619RouteBuild/Run_20261116_120602_8e943e9b/route_lead_approval.json`.

BT-22 Smoke retry `Saved/SevarogArenaRoute/Run_20261116_120816_776c0675` failed after 180 seconds. It observed suppressed pack actor `BP_ExampleGreatSwordBoss_C_3` (`began_play=0`, `montage_active=0`), then possession retries 1/2, `PendingArenaBossSpawn`, and `PendingArenaPlayerHealth retry=3 health=0`. It contains no subsequent retry, route-refusal, or framework proof/binding/HUD/health/card markers. Acceptance stays BLOCKED; only the two suppression observations are accepted. Runner restored `DefaultGame.ini`, closed Editor, released both locks, and made no Smoke asset saves. BT-29 assigns Antigravity a read-only diagnosis; do not run another PIE attempt until it explains the stalled retry/health path. Raw BehaviorTree attack-task ticks and boss-death acceptance remain separate open gates. No playable package is available.

### BT-29 diagnosis / BT-30 fix pending (2026-11-16)

Codex matched the Smoke log stall to the UE 5.5.4 timer lifecycle: `FTimerManager::Tick` marks the one-shot timer `Executing` before callback invocation; `FTimerManager::IsTimerActive` returns true for that non-paused state; the guarded re-arm therefore does not run, and TimerManager removes the non-looping timer after callback. The log's final readiness message is retry 3, with no later attempt or refusal. BT-30 assigns Antigravity a source hotfix to reliably re-arm each nonterminal 50 ms attempt while retaining the 100-retry refusal and success/timeout cancellation. C-1155 rebuild/suite and a fresh Smoke retry are still required after lead review. The previous run restored config, closed Editor and released both locks. No playable build is claimed.
### BT-30..35 follow-up (2026-11-16)

BT-30 fixed the timer stall by scheduling the readiness timer as repeating at 50 ms; existing success, timeout and inactive-state paths clear it. BT-31 fresh C-1155 Development build passed (exit 0), full pinned DD27j suite 573/573 with 0 failures, four source hashes matched, and both locks were released. Receipt: `Saved/C1619RouteBuild/Run_20261116_122633_896e1cfe/route_lead_approval.json`.

Smoke `Saved/SevarogArenaRoute/Run_20261116_122821_e45f89f1` now reaches retry 100 and refuses `PlayerHealthTimeout`, with census `BossCount=0 PlayerCount=1 CompetingPackBossCount=0`. It observed pack suppression before BeginPlay and no active montage. It did not spawn/bind the framework boss, so HUD, health=1500 and production card remain unverified. The `health=0` log does not distinguish an unreadable attribute from an actual zero. Runner restored `DefaultGame.ini`, closed Editor, released both locks, and made no assets saves. BT-33 is auditing evidence; BT-35 is diagnosing `Attribute.Health` read/value. Do not retry until a proven safe correction. Boss-death acceptance and raw BehaviorTree ticks remain open; no playable package is available.
