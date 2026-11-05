# P01–P05 A5 parity plan

Status: prepared for Lead-run verification; Codex has not opened Unreal or run PIE.

The pair must use the same `L_SevarogArena`, build/content revision, input setup, and driver settings. The legacy arm leaves `H019_ENCOUNTER_DEFINITION` unset. The selected arm sets it to `/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter`. Each driver already finds the pack boss by class, so selected-route eligibility is conditional on that same placed actor satisfying the selected definition and the scenario's required components. A run that cannot find the same actor/component set is a refusal/inconclusive parity pair, not evidence of a gameplay mismatch.

| Registered driver | Map/setup | Observables compared | Expected same | Expected to differ |
|---|---|---|---|---|
| `pie_a4_low_sweep` | `L_SevarogArena`; fixed pack boss and player; A4 trials, reset/death cases | A4 tracker start/instance, commit and active positions, yaw drift, sweep/hit/jump/i-frame counters, player health loss, reset/death cancellation | All listed combat results and measured timings within the driver's existing tolerances | Snapshot route/selection, data activation/binding, component provenance/ownership census, generation and selected-route lifecycle diagnostics |
| `pie_dormant_wake` | `L_SevarogArena`; driver enables `rpg.WakeClip 1`; dormant/wake/reset/death sequence | dormant and wake stage, montage identity, wake duration, direct-start veto, reset cancellation, death state | Wake/stage outcomes, montage, direct-start rejection, reset/death behavior and timing | Snapshot route/selection and activation/binding/lifecycle fields; component provenance/ownership census |
| `pie_damage_path` | `L_SevarogArena`; same test boss/player; resolver direct-test scenarios and A4/A5/A6 real-move group | resolver outcomes/audit ordering, health deltas, duplicate/stale/dead/lethal rejection, component presence, move hit outcomes | Damage amounts, acceptance/refusal tokens, health, audit sequence, component presence, generation-sensitive stale-hit behavior | Snapshot route/selection and activation/binding/lifecycle fields; component provenance/ownership census |
| `pie_player_death_reset` (P06 candidate) | `L_SevarogArena`; death/respawn and reset-broadcast scenario | death, respawn latency, reset/rebind events, generation/count | Player-facing reset sequence and timing | Selected route, definition and binding/rebind diagnostics |
| `pie_telegraph` (P07 candidate) | `L_SevarogArena`; authored telegraph scenarios | telegraph phases, cue timing, attack start/contact, player outcome | Combat cue and attack timing/outcome | Route/selection/activation and provenance diagnostics |
| `pie_boss_hud` (P08 candidate) | `L_SevarogArena`; HUD setup and lifecycle changes | HUD text/state for health, phase, posture and combat | Player-visible values and update order | Route/selection/activation diagnostics only if surfaced by the HUD (not currently asserted) |

The three P03–P05 scripts will read the environment variable before requesting PIE and execute the same `rpg.EncounterDefinition <path>` console command used by the H019 driver only when it is nonempty. Unset execution does not issue that command. Since the selector is process-wide, run the legacy arm first in a fresh editor process (or explicitly clear the CVar before that arm); merely unsetting the environment variable cannot clear a selection left by a previous selected arm. The selected arm is opt-in and must be run in a fresh PIE session; Lead owns both arms and their logs.

## Snapshot bridge

The native `UWorld::GetSubsystemBase` API is not a reflected `UFUNCTION`, so Python cannot safely assume it is exposed. The minimal supported bridge is a read-only, reflected static accessor on `URPGPlayerMovesSubsystem` that accepts a world context and returns that world's subsystem. The probe uses `UnrealEditorSubsystem.get_game_world()`, calls the accessor, then calls the existing BlueprintCallable `BuildEncounterParitySnapshot()` and logs the returned JSON unchanged. It does not mutate actors or write a receipt. The probe is useful only after the Lead builds the source change and runs it during selected PIE; the script reports a clear failure if the reflected API or subsystem is absent.

Lead command from the project root, with `L_SevarogArena` open and the selected definition set:

```powershell
$env:H019_ENCOUNTER_DEFINITION = '/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter'
python -I Scripts/run_in_editor.py Scripts/Editor/probe_encounter_parity_snapshot.py
```

The snapshot is diagnostic input, not a complete parity receipt: it omits driver identity, run arguments, terminal outcome, measured observables and raw-log hash. P09 remains necessary for a v2 receipt.
