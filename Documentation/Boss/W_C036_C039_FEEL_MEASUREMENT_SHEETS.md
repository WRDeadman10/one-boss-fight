# Queue W Codex batch: W-C036–W-C039 feel measurement sheets

Documentation and source audit only. No Editor, PIE, build, package, game launch, or tuning change was made. Runtime measurements and sensory judgments require Claude's Lead-run evidence.

## W-C036 — input-to-montage run sheet

Driver: `Scripts/Editor/pie_input_montage_latency.py`. It injects attack, dodge, and parry input actions, timestamps immediately before injection, and logs the first observed player montage change (`pie_input_montage_latency.py:11-18,85-110`). It observes on the Slate post-tick callback (`:34-41`), so `observed_ms` includes game-tick observation delay; this is neither hardware-device latency nor a direct measure of input-to-visible-pixel latency. The driver does not set or verify FPS and is not registered in `Scripts/RunDrivers.ps1`; launch it with the supported one-script wrapper `Scripts/RunEditorScript.ps1 -Script Scripts/Editor/pie_input_montage_latency.py -Tag InputLatency` after Lead configures the session.

Run six isolated sessions: legacy and selected-data route at each of 30, 60, and 120 FPS. For data route, set `H019_ENCOUNTER_DEFINITION` to `/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter` before editor start; for legacy, unset it. In each fresh session set the editor/game frame cap to the requested value using the Lead's established launch/profile method, disable sync only if that same method requires it, and record the effective cap and actual observed frame/tick timing in the raw log. Do not claim the cap from the requested setting alone. Preserve each run's full editor log, process/build identity, route-selection line, requested and observed FPS, and SHA-256; do not merge or overwrite runs.

| Route | FPS session | Expected driver samples | Acceptance / interpretation |
|---|---:|---|---|
| Legacy (selector unset) | 30 | attack, dodge, parry | Three `sample` records with `tick_s` consistent with observed frame cadence; any `NO_MONTAGE_CHANGE` is a failed/inconclusive action, not zero latency. |
| Selected data (H019 path set) | 30 | attack, dodge, parry | Same; confirm `route=data selection=...` before interpreting samples. |
| Legacy (selector unset) | 60 | attack, dodge, parry | Same; retain individual measurements, no averaging across actions. |
| Selected data (H019 path set) | 60 | attack, dodge, parry | Same; confirm selected route in log. |
| Legacy (selector unset) | 120 | attack, dodge, parry | Same; retain individual measurements, no averaging across actions. |
| Selected data (H019 path set) | 120 | attack, dodge, parry | Same; confirm selected route in log. |

Report table per sample: route, requested cap, measured cadence (`tick_s`), action, baseline montage, observed montage, `observed_ms`, log path/hash, and status. Compare like action and FPS only. A faster polling cadence can reduce observation quantization without proving lower hardware latency. Re-run a session if the configured cap is not corroborated by observed cadence; retain the failed attempt separately.

## W-C037 — hit-feel implementation inventory

“Hit type” here means the event categories handled by current source. A dash means no source-backed value/trigger was identified in the reviewed native path; it does not prove that no Blueprint or authored asset adds one. `FRPGShakeSettings` is editor-configurable, and the current boss Blueprint's serialized values were not independently read here.

| Event / hit type | Hit stop | Camera shake | Sound / audio | Source-backed finding |
|---|---|---|---|---|
| Ordinary player weapon hit on boss | None identified in `URPGBossLegend` event path | None identified | No hit-result-specific sound found in the reviewed resolver path; generic authored move cues are separate | Legend's hit-stop handler is driven by riposte count, not each ordinary damage event (`RPGLegend.cpp:557-580`). |
| Player riposte hit (nonlethal) | Boss and player request: 0.08 real seconds at 0.05 custom dilation; applied if effects/time subsystem/encounter permit (`RPGLegend.h:192-200`; `.cpp:438-454`) | None assigned by the riposte handler | Optional parry slow-motion SoundMix applies to accepted player parry slow-motion; null by default; it is a mix/duck, not a hit sound (`RPGLegend.h:219-224`; `.cpp:475-515`) | `pie_legend.py` L4 measures duration, but no current fresh Lead receipt is included in this batch. |
| Lethal riposte | Skipped when `bSkipHitStopOnLethal=true`; the kill slow-motion path handles the victory event (`RPGLegend.h:207-212`; `RPGLegend.cpp:438-449,573-580`) | No riposte shake identified | No lethal-hit sound assigned by this handler | Source configuration only; runtime remains Lead-run. |
| Boss A2/A6 slam reaching active | No hit-stop call in the slam handler | Slam shake, once per attack instance; settings supplied by `Slam`; distance-scaled and can be suppressed (`RPGLegend.cpp:386-426,557-563`; `RPGLegend.h:176-186`) | No slam-specific sound in this Legend handler | `FRPGShakeSettings` defaults: duration 0.55 s, blend-in 0.02 s, blend-out 0.45 s; amplitude/frequency fields are configurable (`RPGCameraShakes.h:20-28,30-75`). Actual BP overrides were not audited. |
| Phase-two transition / roar | None identified | Roar shake once per phase-two count (`RPGLegend.cpp:428-435,565-571`; `RPGLegend.h:182-186`) | No roar-specific sound in this Legend handler | The roar settings use the same configurable `FRPGShakeSettings`; runtime evidence/capture remains Lead-run. |
| Confirmed parry | No direct hit-stop from parry handler | No camera shake in the parry handler | Optional SoundMix only during accepted slow-motion; null default (`RPGLegend.cpp:475-515`; `RPGLegend.h:219-224`) | Not a per-hit impact sound. A parry sound asset/value is not established by these source lines. |
| Bleed proc | None identified in this component | None identified | The proc plays `LoadedSound` at location with volume 1.2 and pitch 0.7 (`RPGBossBleed.cpp:106-117`) | Asset identity/configuration was not captured in this audit. |
| Generic authored boss move cue | None in cue executor | Cue visual may spawn a flipbook, not a camera shake | Plays cue `Sound` when audio channel is enabled and a sound is assigned (`RPGFrameworkMoveExecutor.cpp:505-534`) | Generic cue sound is authored per cue and is not mapped here to damage outcome or hit type. |

Existing Lead-run checks to attach if available: `Scripts/Editor/pie_legend.py` L1/A2 shake, L2 roar, L3/A6 shake, L4 riposte hit stop, and L6 capture; those checks do not fill absent per-hit sound mappings (`pie_legend.py:1-4,157-160,203-265,397`).

## W-C038 — telegraph target, configured timing, and Lead checks

Freeze targets are design values, tracker fields are configured montage times, and reaction windows require synchronized runtime observation. They are separate columns so configured numbers are not represented as player reaction time. Freeze references below use `Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md:135-142`; tracker comparison and caveats are cross-checked against `V_C041_C045_FEEL_FLOW_AUDIT.md:19-31`.

| Move | Freeze tell / pre-hit target | Current tracker configured timing | What Lead should check and preserve | Current evidence status |
|---|---|---|---|---|
| A1 | 0.35 s telegraph; 0.15 s active | Commit .33 s; active .35 s | Capture montage start, commitment marker/log, first active frame, and player dodge/parry input frame in both routes; check if attack identity and tell onset are visible before active. | Configured only; no measured reaction window. |
| A2 | 1.40 s apex hold plus .25 s before hit | Commit 1.68 s; active 1.93 s | Same capture; include apex hold and active-frame boundary, then verify one slam-shake event in `pie_legend.py` L1/L3. | Configured only; no paired reaction measurement. |
| A3a | 0.40 s | Commit .38 s; active .40 s | Capture first and second branch stages separately; run `pie_telegraph.py` timing checks and preserve its raw log. | Configured only; no player response window. |
| A3b | No separate second-stage Freeze windup number | Commit .13 s; active .15 s | Do not score against A3a's 0.40 s target. Capture branch eligibility, second-stage tell, active frame, and response. | No separate target; runtime unreadability unresolved. |
| A4 | 0.60 s | Commit .40 s; active .60 s | Preserve `pie_telegraph.py` and A4 parry/sweep pair evidence, including exact active frame and input/contact timing. | Configured only; Lead pair/capture required. |
| A5 | 0.40 s before release | No row in `RPGAttackTracker`; separate heal-punish/javelin path | Use `pie_a5_heal_punish.py`; record summon/release, javelin arrival, player input and contact, each route. Do not impute tracker timing. | Driver exists; no current measured reaction window. |
| A6 | 0.90 s ascent (Freeze) | Commit .16 s; active .75 s | Record the authored/stand-in montage and active boundary; run `pie_legend.py` L3 for shake, preserve synchronized footage. | Configured from stand-in; target/runtime difference needs Lead review. |

For each Lead run, capture the game view and a log with a shared clock or identifiable frame markers. Record tell-onset, commit, active/contact, player input, action/outcome, montage/rate, route, FPS, build ID, and evidence hash. A dodge with no damage alone does not prove how much reaction time was available. Classify obscured/unobservable tells as inconclusive; do not tune from configuration-only comparison.

## W-C039 — owner decision: KI-190 Strength Light stamina

**Decision requested:** Should Strength Light retain the pack base cost, be changed to the Freeze's 35 stamina per swing, or receive a new separately authored build-specific rule?

| Option | Proposed disposition | Consequence / evidence needed |
|---|---|---|
| A — Keep pack value (current behavior) | Leave Strength Light at `StaminaCost=-1`, which retains pack base cost 15. Keep KI-190 open. | No tuning change. Runtime loadout evidence remains necessary; Freeze 5/20.1 says 35 per Strength swing while current table comment specifies 35 per heavy swing (`RPGWeaponAttackTable.cpp:41-44`; `V_C046_C049_CAMERA_STAMINA_AUDIT.md:16-23`). |
| B — Match Freeze | Set Strength Light explicitly to 35 if the owner confirms the Freeze wording means every Strength swing. | Resolves the literal “per swing” requirement, but changes the current fallback by +20 stamina per light attack; verify a real Strength loadout's charged cost and regression/balance effects before closing KI-190. |
| C — New build-specific row | Add an explicit Strength Light row with an owner-approved value (15 or 35) and keep pack fallback only for unrelated/unconfigured rows. | Makes intent visible and testable, but adds configuration surface and migration/default-parity work; specify the approved value before implementation. |

No option is selected here and no gameplay value is changed. Source: `RPGWeaponAttackTable.cpp:41-44`; `RPGSwingTracker.cpp` cost fallback (verify in review before implementation); `Scripts/Editor/pie_stamina_cost.py:1-4,150-160`; `V_C046_C049_CAMERA_STAMINA_AUDIT.md:16-23`; KI-190 in `Documentation/KNOWN_ISSUES.md:304`.

## Limits and next evidence

These sheets prepare the next Lead run/owner decision. They do not supply live response-time data, serialized Blueprint shake overrides, per-hit sound mappings, a stamina decision, or runtime approval. The W-C036 driver is currently a direct one-script run, not a `RunDrivers.ps1` entry; adding it to the shared runner is outside this document-only batch.
