# AN-C06–C10: First Dodge After Draw Audit

Date: 2026-11-08  
Scope: offline source, retained Lead logs, pack text exports, deterministic rules tests, and the Lead-only PIE probe. No Unreal Editor, build, or PIE was run by Codex.

## AN-C06: input and map-write order

- `RPGDodgeTiming::BeginPlay` loads and holds `BackstepMontage` before calling `TryBind`. `TryBind` binds `IA_Dodge` to `ETriggerEvent::Started` and `OnDodgePressed` (see `Source/OneBossFight/Player/RPGDodgeTiming.cpp`).
- `OnDodgePressed` finds the pack ability, checks whether it is active, synchronously resolves quick/full clips, chooses the standing backstep, calls `ApplyClip`, logs the result, and returns. `ApplyClip` writes montage and play rate to each existing `DodgeMontage` map entry; it does not add entries or activate the ability.
- This order proves the project callback mutates a montage map on the input event. It does not prove whether the pack's own input activation handler runs before or after this callback, nor whether it reads the map at activation, on a later tick, or from another copy.
- In both retained C-1061 runs, `FlushAsyncLoading(413)` is immediately followed by the first project dodge log (`showcase_def1.log` lines 1895–1896; `showcase_mix2.log` lines 1640–1641). The first attempt has no montage and zero displacement in the corresponding showcase output; later attempts move. This temporal adjacency is evidence for a load/input-order hypothesis, not causal proof.
- `showcase_def1.log` also has `Attempted to swap elements in empty array StoredInputTags!` at lines 1881–1882 before `draw ready=True` at 1883. That is a pack input-buffer warning during the draw transition. It is a separate plausible clue; the log does not show it causing dodge rejection.

## AN-C07: pack ability evidence boundary

- The retained `PR2_CDO_GA_Player_Dodge.t3d` export shows a default `DodgeMontage` entry keyed by the forward enumerator and `Dodge_To_Idle_Montage`. It describes the CDO/default map only; it is not the live per-player ability instance at first press.
- The retained `PR2_GA_Player_Dodge.t3d` export serializes Blueprint graph object declarations but does not provide a readable execution-order trace sufficient to establish live input activation ordering or the meaning of `StoredInputTags` in this failing case.
- Existing `RPGAutomationTests.cpp` checks that the Blueprint and `DodgeMontage` property exist. `RPGDodgeInputRulesTests.cpp` covers standing/directional choice, empty fallback, and repeatable pure decisions. Neither exercises a live ability activation or the instance map at the first input event.
- No pack asset was edited. The runtime state needed to identify the root cause is unavailable in these offline artifacts.

## AN-C08/C09: deterministic coverage and probe review

- Kept the native pure-rule tests as-is; they already cover standing backstep selection, empty-clip fallback, directional roll, and repeated decisions. Added focused Python contract checks that distinguish those pure rules from an integration/activation test.
- The Lead probe uses the actual R2 draw key and now considers draw complete only when combat is enabled and the player's montage is idle. It then issues the first no-assignment standing dodge immediately, records the montage, displacement, stage and counters, and runs two separated repeat controls.
- Probe cleanup releases any held keys, unregisters the Slate tick callback, and calls the shared `plc.end_play()` helper on success and exception paths. It does not assign a montage through editor properties.
- This is a proposed Lead measurement. It has not been executed in PIE by Codex.

## AN-C10: conclusion and evidence needed

Root cause remains OPEN. The first-use BeginPlay preload is a plausible low-risk mitigation for synchronous asset loading, but the adjacent `FlushAsyncLoading` entries do not show that this is the cause. A speculative pre-input ability-map priming change was removed: no evidence justified priming every discovered ability, and that could change the first moving-dodge route.

### C-1063 Lead rerun update

Claude reports BUILD-261 passed 485/485 and logs show the earlier preload/map-prime activity, but the first press still moved 0.0 cm while presses 2/3 moved 96.6/97.8 cm. Thus preload/map priming did not fix the bug and the montage map is not the cause. The Codex first-dodge probe aborted because its warm-up/draw cadence differed from the Lead showcase. The activation-dispatch hypothesis is now prioritized, pending first-press `Can Activate Ability?`, ability active/tag, stamina, and input-buffer evidence; no root cause is yet proven.

Next Lead run: build current Source and run `Scripts/Editor/probe_first_dodge_after_draw.py` under `ENGINE_LOCK`, with no runtime montage assignment. If the first press still fails, capture `DodgeMontage` contents and `IsAbilityActive` immediately before/after the project callback and pack activation; inspect the StoredInputTags warning's input-buffer state through the draw-to-dodge boundary. Compare first press against two repeat controls. Keep KI-199 OPEN until the first backstep montage and capsule displacement are both observed without snap.

## Validation performed

- `Scripts/Tools/test_first_dodge_after_draw_contract.py`: 2/2 passed after correcting a probe-order assertion to anchor on the runtime `draw_ready` log rather than the helper definition.
- Probe Python syntax check: passed (`python -m py_compile Scripts/Editor/probe_first_dodge_after_draw.py`).
- `Scripts/Tools/check_doc_links.py .`: `broken_links=0`; `git diff --check`: clean (only existing line-ending conversion notices).
- Full offline suite, Unreal build, Editor, PIE, and native automation: not run by Codex.
