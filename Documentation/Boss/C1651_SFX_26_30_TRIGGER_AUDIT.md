# C-1651 SFX-26..30 Native Trigger Audit

**Status:** Source-only lead audit; no cue wiring or runtime verification.
**Scope:** Independent of Antigravity's candidate-package matrix. Candidate choices remain subject to Owner selection.

## Findings

| SFX | Proposed event | Native seam and evidence | Lead assessment |
|---|---|---|---|
| 26 | Boss posture warning below 25% | `Source/OneBossFight/Player/RPGBossPosture.cpp:98-130` applies posture damage and requests a break only at zero. `:133-139` queues parry posture damage. No sub-25% transition/event is exposed in this component. | A warning cue needs a threshold-crossing event with one-shot/re-arm semantics; polling below threshold risks repeated playback. Current native path has no such event. |
| 27 | Boss stagger breathing/groan loop | `Source/OneBossFight/Player/RPGBossStagger.cpp:398-446` enters Down, cancels offense, holds behavior, stops movement and starts a fall montage. The component's state and montage controls are native; no sound dispatch appears in this path. | `StartStagger` is a plausible loop start seam. Stop must cover every `EndStagger` path, including abort/reset/death, and avoid duplicate loop instances. Candidate loop assets are not verified as loops. |
| 28 | Critical execution/riposte impact | `Source/OneBossFight/Player/RPGBossStagger.cpp:554-573` accepts the riposte; `:742-763` applies the synchronized execution's single impact at `ApplyRiposteImpact`. `Source/OneBossFight/Player/RPGRiposteInput.cpp:51-71` routes the light-attack press into `TryRiposte`. | `ApplyRiposteImpact` is the most deterministic native contact seam for the paired-clip path. The fallback armed-riposte path has no native impact callback in these files; it would need a confirmed hit event to avoid playing on press. No SoundBase dispatch is present in the inspected paths. |
| 29 | Boss stagger recovery | `Source/OneBossFight/Player/RPGBossStagger.cpp:448-510` sets Phase Idle, refills posture, hands queued phase transitions off or resumes behavior, then logs completion. | `EndStagger` is shared by ordinary recovery and non-audio lifecycle exits. A cue must distinguish normal timeout recovery from abort, reset, death, or transition handoff; firing on every call can be false/duplicate. No native sound dispatch appears here. |
| 30 | Player guard-break | The inspected project components expose pack block observation in `Source/OneBossFight/Player/RPGDodgeTiming.cpp:88-131`, and attack/parry stamina writes in `RPGPlayerParry.cpp:80-96, 202-224` and `RPGSwingTracker.cpp:221-225, 270-273`. These paths do not establish a player posture/guard-break transition. | No confirmed native guard-break event seam was found in the inspected source. Candidate trigger and pack Blueprint behavior need readback before proposing wiring. Keep player cues non-vocal as the spec requires. |

## Cross-cutting notes

- The inspected posture, stagger, riposte, hit-intake and guard-monitor paths contain no `PlaySound`/`SpawnSound` dispatch for these events. Existing music/footstep setup is separate and may create overlap only if reused carelessly.
- SFX-29 must not trigger from every `EndStagger` invocation without an explicit normal-recovery reason.
- SFX-28 must distinguish paired execution impact from fallback riposte; press acceptance is not proof of a hit.
- Native source review cannot establish serialized Blueprint, montage-notify, or pack ability behavior. No project source/assets/config were changed, no audio was exported, and no Editor/build/test/runtime command was run.

## Next

Antigravity continues BT-132..BT-136 package-only audit without waiting for this source report. Audio export/reels and all wiring remain held for Owner selections and the documented C-1155 gate.
