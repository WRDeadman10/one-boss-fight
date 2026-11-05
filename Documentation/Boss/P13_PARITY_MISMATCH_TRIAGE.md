# P13 A5 parity mismatch triage

## C-865 O4 — declared boundary observations (WARN-stochastic; accepted C-867)

| Observation | Pair history (legacy / data) | Disposition |
|---|---|---|
| A4 S9 roll at 0.40 s, invulnerable out of 3 | Four runs: `1, 2, 2, 0` / `0, 0, 0, 2`; BUILD-221 `_t1` is `0/3` / `2/3` | Boundary noise on both routes and in both directions. Only this row's invulnerable field is WARN-stochastic; trial count and other fields remain exact. |
| A4 S9 jump at 0.05 s | Before T1: legacy `0/3` in each run; data `2/3, 2/3, 1/3`. BUILD-221 `_t1` and `_t1b`: `0/3` / `0/3` in both pairs | CLOSED after T1: the repeat confirms both routes now match. Root cause was selected-route LowSweep-before-Tracker tick order; T1's explicit tracker prerequisite fixes the order (BUILD-221, accepted C-864; repeat C-867). |
| P06 `world_hits` field | BUILD-220 `_d5`, side roll `heal+1.30`: legacy `0`, data `1`; BUILD-221 `_t1`, side roll `heal+1.13`: legacy `1`, data `0`; `_t1` `heal+1.30`: `0` / `0` | Counter sample boundary varies across routes/trials. `world_hits` alone is WARN-stochastic; trial identity, `hits`, and `iframe_passes` remain exact. |
| A4 S6 world-blocker race | Seen on data twice before T1; zero occurrences since T1 | Retain as a known legacy race; no current S6 mismatch in the `_t1` pair. |

O3 `_t1` start-state rows report matching boss/player transforms, capsule sizes, mesh offsets and CharacterMovement values. The current paired receipts are both 14/14 (A4) and 32/32 (P06). The source-hash-verified temporary rebuild compares PASS for both with the declared WARN rows above; closed raw logs and receipts were not edited. The P06 exact fields are split into exact trial/hit/iframe data and a separate world-hit warning observable.

The confirming A4 repeat is in `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/pie_a4_low_sweep_t1b/{legacy,data}/editor_raw.log`; both terminal results are 14/14 and both S9 jump-at-0.05 counts are 0/3. The prior `_t1` pair is under `pie_a4_low_sweep_t1/`.

## C-859 O1 — P06 side-roll boundary (historical exact mismatch, superseded by C-865)

The P06 row tuple is `(trial, hits, iframe_passes, world_hits)` in `Scripts/Editor/pie_a5_heal_punish.py:321-325`; its final value is the javelin's world-hit counter, not a count of side rolls. At the disputed `side roll at heal+1.30` boundary, both arms recorded hits=0 and iframe_passes=0; data recorded world_hits=1 while legacy recorded 0. The paired raw evidence is `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/pie_a5_heal_punish_d5/legacy/editor_raw.log` and `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/pie_a5_heal_punish_d5/data/editor_raw.log`.

The event ordering supports a sampling explanation for this counter difference: legacy reports the P06 sample at frame 557 (`00:31:48.302`) then records the world-hit terminal at frame 558 (`00:31:48.326`); data records the world-hit terminal at frame 537 (`00:34:52.119`) before sampling at frame 543 (`00:34:52.311`). Both terminal lines name `RPGGreyboxArena_0`. C-865's later paired BUILD-221 observation flips the route carrying the count (legacy `1`, data `0` at `heal+1.13`; both `0` at `heal+1.30`). The accepted classification now treats only `world_hits` as WARN-stochastic; `hits` and `iframe_passes` remain exact. Keep the original O1 evidence below as history, not a current exact mismatch.

Source mechanisms to isolate on a repeat: `RPGBossHealPunish::GetSpawnLocation` chooses the first available `JavelinSpawn`/`hand_l` socket (`RPGBossHealPunish.cpp:36-50`, `.h:72`); release samples the current player position and derives direction/speed from spawn-to-target distance (`RPGBossHealPunish.cpp:162-176`). The P06 javelin-11 launch logs differ in origin/distance/speed (legacy `(63,33,154)`, 766 cm, 638 cm/s; data `(-30,69,165)`, 676 cm, 563 cm/s), a candidate trajectory input whose cause is unproven. Each javelin tick performs independent world and pawn sweeps; player contact wins only when it precedes/equal the world hit, otherwise a world hit terminates it (`RPGBossJavelin.cpp:118-138,171-174`). The current logs do not retain chosen socket, sweep hit times, or collision fractions. Instrument those plus projectile completion/sample timestamps before attributing the boundary to route wiring or changing combat behavior.

## C-860 D6d — stochastic diagnostics (STOCHASTIC)

Only three declared observations are treated as stochastic: `pie_close_attacks` C7 requires the five-trial 90 cm scenario to run and at least one hit; `pie_attack_rules` R5 check 0010 requires the 40 s natural fight to run and at least one tracked attack; R5 check 0013 requires accounted commits plus windup-stops to cover all tracked attacks. Each pair passes these observations when both arms meet their declared driver threshold and check status; differing raw counts are retained as WARN rows with both values. These are free-fight/AI-choice observations only. Scripted trials, per-trial counts, and other observables remain under D6c/D6b comparison. The underlying accepted driver checks remain visible and fail closed when either threshold or scenario-run condition is unmet.

The D6d/D6c source-verified scan covers 36 closed pairs: 26 PASS, 8 FAIL, 2 INCONCLUSIVE. `close_attacks_d5` passes with C7 2/5 vs 1/5 as WARN; `attack_rules_d5` passes with tracked attacks 1 vs 3 and accounted outcomes 1 vs 3 as WARN. Exact P06 fails on its typed per-trial world-hit value. Three A4 pairs, two HUD pairs, and both historical 2000-vs-1500 death-reset captures also fail; the old `pie_boss_hud` and `pie_damage_path` captures are inconclusive. Full pair output is posted in X-1236.

## C-863 D6d extension — natural soak health snapshots (STOCHASTIC)

Only `pie_soak.py`'s six natural-fight `no damage after reset` checks use this rule: check IDs 0007, 0042, 0077, 0112, 0147, and 0182 in the 213-check receipt. Each compares matching PASS/FAIL status and requires `before == after` within each route; health values remain visible as WARN. These are the six `natural()` runs in `Scripts/Editor/pie_soak.py:199-224`, finalized through the common check at `:155-197`. The scripted `break`, `roar`, `player_death`, and `boss_death` no-damage rows retain deterministic comparisons.

The source-hash-verified rebuild of the closed BUILD-220 `_d5` soak logs passes. Five natural pairs show 120/120 in both arms; check-0182 shows legacy 84/84 and data 120/120. Each arm meets its own no-damage condition, so that health baseline difference is retained as a WARN rather than treated as route mismatch. The six WARN rows are `check-0007`, `0042`, `0077`, `0112`, `0147`, and `0182` in the temporary report; raw logs remain unchanged.

F4 also rebuilds the `pie_iframes_d5` receipts after correcting the registered prefix. The comparison is PASS with source-log verification; legacy `editor_raw.log` SHA-256 is `d5cb9f03abac0d8745f9bd93194972c438fefa8462da58537f91425ed85250e3`, data SHA-256 is `9325fd8c0b4bbceffa3191a56664ca3b8febe4a72750a3cdfa93f8c7b3900153`. The generated receipts and comparison report were kept in a temporary folder; no closed evidence files were replaced.

## C-861 O2 — reset/start-state common-cause check (INCOMPLETE: capture fields absent)

| Requested comparison | Existing paired evidence | Finding |
|---|---|---|
| Boss/player location and rotation at scenario reset | A4 D2 S9 logs at `pie_a4_low_sweep_d2/legacy/editor_raw.log:2931,3064` and `.../data/editor_raw.log:2945,3082`; driver reset/placement is `Scripts/Editor/pie_a4_low_sweep.py:49,122-136`. | Logs report scenario elapsed/tracker state and final counts, but neither actor transform. `place()` derives player position/rotation from boss transform and distance; no reset transform is captured. Cannot establish a shared transform cause for S9/S6. |
| Capsule/mesh offsets and CharacterMovement values | The same A4 diagnostics (`:2931`, `:2945`) include montage, i-frame and component order only. Driver diagnostic implementation is `pie_a4_low_sweep.py:66-87`. | No capsule size, mesh relative transform, or movement-property values are emitted in either arm. |
| PIE start to first scripted action | A4 raw evidence around the first scenario is `pie_a4_low_sweep_d2/legacy/editor_raw.log:1710,1982` and `.../data/editor_raw.log:1710,1982`; state machine is `pie_a4_low_sweep.py:208-225`. | There is a “boss awake” marker and later scenario result, but no PIE-start timestamp or first-action marker, so elapsed time cannot be compared from these logs. |
| P06 launch geometry (adjacent evidence, not reset state) | `pie_a5_heal_punish_d5/legacy/editor_raw.log:2073,2085`; `.../data/editor_raw.log:2084,2097`; driver placement is `pie_a5_heal_punish.py:42,295-320`. | Launch origin/range/speed differ: legacy `(63,33,154)`, 766 cm, 638 cm/s; data `(-30,69,165)`, 676 cm, 563 cm/s. This confirms a geometry difference at release but does not identify whether actor reset, mesh/socket offset, or route setup caused it. Keep O1's route-cause question open. |

The D2 A4 initial S9 diagnostic lines also show component registration order differs: legacy `RPGAttackTracker#26,RPGBossLowSweep#29` versus data `RPGBossLowSweep#22,RPGAttackTracker#28` (`editor_raw.log:2931` and `:2945`). This is observed metadata, not proof of a timing cause. C-862's source prerequisite test and O3 instrumentation were accepted and BUILD-221 passed 463/463 (C-864). The Lead-owned `_t1` A4/P06 reruns now supply the matched start-state and boundary histories documented above; component ordering remains different while the explicit tracker prerequisite makes the tracker tick first.

## Q06–Q10 evidence reconciliation (2026-11-05, C-848)

This triage preserves the BUILD-219/BUILD-220 findings below as historical captures. Q001–Q005's receipt refresh reports six pair results: A4 `_r2` FAIL (two S9 observations), dormant-wake PASS, damage-path PASS, player-death-reset FAIL (four health checks), telegraph FAIL (checks 0010/0013/0020/0023), and boss-HUD FAIL (28/29). Exact pair identity, terminal, and check outcomes are in `Docs/BossCombatReview/Execution/Codex/Q001_Q005_2026-11-05/Q01_Q05_STATUS.md`; source-log hashes were verified there. Do not merge these pre-D2/pre-H4/H5 outcomes with Claude's fresh BUILD-220+D2 reruns, which are still pending per C-848.

The death-reset mismatch's source cause was the saved boss draft at 1500 versus legacy 2000. Claude's C-840 D2 update changed the draft to 2000 and refreshed the manifest/selection hash; C-847 confirms the post-update and live manifest hashes validate. This is a scoped correction, but the fresh death-reset/HUD pair is the regression witness and remains pending. No repeatable S9 root cause has been established. H4 now captures diagnostics; it does not establish or fix the cause. H5 enables typed timing comparison, but the old telegraph pair predates H5 and cannot validate that behavior.

Q006/Q007 disposition: the existing hash-verified comparisons and the findings below supply the historical per-pair results and source-based causes. Q008 is partial: health was corrected, with regression evidence pending; no S9 production change is justified. Q009/Q010 are refreshed in `P15_A7_PARITY_SUMMARY_DRAFT.md` and `J049_OWNER_DECISION_PACKET.md`; A7 stays open with legacy startup as the safe default. See `Documentation/Boss/Q06_Q10_PARITY_DISPOSITION.md`.

Status: BUILD-219 A5 pairs completed by Claude (C-839); receipts were finalized from the closed telegraph logs after T1 and all six pairs were locally compared with source-log hash verification (Q006). Parity is not met. Lead review of the new receipt/comparison results is pending. This source triage identifies the concrete data/component causes and separates the unresolved timing observation from proven causality. See `P14_PARITY_PRODUCTION_CHANGE_PROPOSAL.md` for the flagged test-first proposal.

| Finding | Captured result | Source-backed cause | Disposition |
|---|---|---|---|
| P10 A4 S6 backward roll at 0.50 s | BUILD-218 selected 13/14; legacy 14/14. BUILD-219 `_r2` repeated 14/14 both arms; mismatch did not reproduce. | No stable cause established; the earlier run's `BP_ToughSword_C_0` blocker occurred in both arms. | NOT REPRODUCED in BUILD-219 `_r2`; retain both histories, do not count as current parity defect. |
| P10 A4 S9 jump at 0.05 s | Across two pairs/four arms: legacy 0/3 hits, data 2/3. | Source confirms `RPGBossLowSweep` is present in the BossCore plan; `RPGTraceGuard` is absent from that plan and is only attached by the legacy branch. TraceGuard governs the pack weapon trace, but current source does not prove it causes this early-jump difference. I-frame monitoring is on the player and ticks at `TG_PostUpdateWork`; LowSweep uses its default tick group. Registration/tick ordering remains a hypothesis pending instrumentation/re-run. | Reproduced mismatch; root cause unproven. Do not attribute it to TraceGuard or tick order yet. |
| P10 A4 S9 roll at 0.40 s | Across two pairs/four arms: legacy invulnerable 1 and 2; data 0 and 0. | Same uncertainty as the jump boundary: current source shows different boss attach sets, but does not establish a causal path into the player's i-frame window. | Reproduced mismatch; root cause unproven. Use a test/instrumentation change before gameplay tuning. |
| P11 player death/reset boss max health | Four checks: legacy 2000/2000; data 1500/1500. | `Saved/G044/encounter_manifest.json:1764` captures selected `stats.max_health: 1500.0`; `RPGEncounterBinding.cpp:43-49` validates and preserves authored stats; `RPGBossEncounterClusterAdapters.cpp:72` assigns `Config.Stats.MaxHealth` to `BossMaxHealth`; `RPGBossEncounter.cpp:114-130` applies that selected value. The legacy component default is 2000 (`RPGBossEncounter.h:42`). | Confirmed data-value mismatch. Recommended parity value: set the selected boss definition's `Stats.MaxHealth` to 2000.0; Claude owns the existing asset edit and live rerun. |
| P11 damage path | Legacy 17/17; selected 0/1 (`[Dmg] FAIL tick raised`), inconclusive. | The driver obtains `RPGDamageResolver` at `pie_damage_path.py:48-50`, then directly dereferences it at `:93` and subsequent test steps. Legacy `AttachLegacyBossBundle` calls `URPGDamageResolver::FindOrAdd` (`RPGPlayerMovesSubsystem.cpp:726-729`); selected BossCore plan creation has no resolver plan (`RPGBossHydrationPreflight.cpp:79-97`), and the selected startup path attaches diagnostics/player components only (`RPGPlayerMovesSubsystem.cpp:188-198`). Missing resolver is the leading source-based explanation, not a confirmed captured exception. | Inconclusive pending traceback and rerun. Driver now includes exception detail in the failing check; see P14 proposal. |
| P11 boss HUD | Legacy 29/29; selected 1/12; HUD component existence failed before downstream raises. | `RPGBossHud` is attached only in legacy bundle (`RPGPlayerMovesSubsystem.cpp:734-738`) and absent from the 13 selected BossCore plans (`RPGBossHydrationPreflight.cpp:79-97`). | Confirmed missing component parity; P14 proposes test-first selected attach-set parity. |
| P11 telegraph checks | Both arms pass 26/26, but strict comparator reports check-0007, 0013, 0014, 0020 value differences: A3a windup 0.408 vs 0.418 s; A1b pre-active rate 0.398 vs 0.396 and windup 0.368 vs 0.366 s; A2 windup 1.937 vs 1.932 s. | `pie_telegraph.py` checks A3a 0.40 ±0.06 s, A1b 0.35 ±0.06 s, and A2 1.93 ±0.12 s; both arms satisfy each declared range. Comparator compares each `{status,message}` exactly (`compare_encounter_parity.py` value equality), so formatted in-tolerance measurement deltas still report mismatch. | Exact-observable mismatch, but no threshold failure or demonstrated gameplay defect. Keep A7 open; Lead must decide whether these telemetry values require equality or should be represented as normalized/range-checked observations. Do not silently waive the comparator result. |
| Boss attach component census | Selected boss lacks `RPGBossHud`, `RPGBossLegend`, `RPGBossMusic`, `RPGFootsteps`, `RPGTraceGuard`; dormant-wake census also lacks `RPGDamageResolver`, though the A4 snapshot later sees it. | Legacy prelude creates/configures Footsteps and Music (`RPGPlayerMovesSubsystem.cpp:618-659`); legacy bundle creates TraceGuard, HUD, and Legend (`:726-742`). Selected BossCore plans are exactly the thirteen factories named at `RPGBossHydrationPreflight.cpp:76-97`; those five have no plan. Selected startup applies diagnostics at `RPGPlayerMovesSubsystem.cpp:188-198`, which are separate from these five. | Five-component gap confirmed. Resolver timing differs by snapshot; determine its later creation path before asserting it is permanently absent. |

## Component purpose classification

- `RPGTraceGuard`: gameplay safety for the pack's weapon trace (interrupt closure, per-instance hit set, and wall occlusion; attach comment at `RPGPlayerMovesSubsystem.cpp:731`).
- `RPGFootsteps`: presentation/audio feedback. Legacy boss settings are intentionally distinct from player footsteps (`:624-638`).
- `RPGBossMusic`: presentation/audio and phase track switching (`:647-658`).
- `RPGBossHud`: player-facing boss bar/banner/victory presentation (`UI/RPGBossHud.h:130-133`).
- `RPGBossLegend`: optional hit-stop, slow-motion and camera-shake presentation, inert while `rpg.Legend` is zero (`Player/RPGLegend.h:128-131`).

These classifications describe the components' documented responsibilities; they do not establish that any one omitted component caused the S9 i-frame timing mismatch.

## Evidence limits

The current locally verified comparator outcomes are: A4 `_r2` FAIL (two S9 informational rows), dormant-wake PASS, telegraph FAIL (four in-tolerance message-value differences), death-reset FAIL (four health rows), damage-path INCONCLUSIVE (0/17 selected), and boss-HUD INCONCLUSIVE (1/12 selected). The telegraph receipts were generated from the existing closed logs after T1; their raw-log hashes verify. No new live evidence is claimed by this source triage. Claude accepted C-862 after fixing the compile include and probe-class spelling; BUILD-221 passed 463/463 including the prerequisite test. Paired A4/P06 reruns remain Lead-owned and in progress, so S9's cause is still unproven. See `Documentation/Boss/T1_TICK_ORDER_AND_O3_INSTRUMENTATION.md`.

## C-862 T1/O3 follow-up — hypothesis, implementation, and remaining proof

LowSweep reads tracker move/window/instance/yaw/timing/position in its tick
(`Source/OneBossFight/Player/RPGBossLowSweep.cpp:197-212,227`). The closed A4
D2 diagnostic reports legacy tracker-before-sweep order at
`pie_a4_low_sweep_d2/legacy/editor_raw.log:2931` and data sweep-before-tracker
at `.../data/editor_raw.log:2945`. Both classes inherit the default
`TG_PrePhysics` group, making the reversed registration order a credible
one-frame hazard. This evidence does not prove that it caused S9/S6.

The shared prerequisite is now wired for LowSweep, Shockwave, HealPunish,
TraceGuard, CombatDebug, Legend, and TraceAudit. A consumer-first transient
world automation test asserts same-frame tracker visibility. O2's captured
`component_registered_order` includes only the tracker, LowSweep, and the
i-frame monitor; registration order for other readers is therefore not
claimed. `CloseClipSwap` and `RPGBossHud` tick without tracker reads.

O3 adds a monotonic marker immediately before `editor_request_begin_play()`
and structured start-state rows after A4 and P06 placement. The measured
elapsed interval starts at the driver begin-play request, so its small
request-to-world-start offset remains. Both driver scripts pass AST parsing;
the automation, Lead build, and fresh paired captures remain pending.
