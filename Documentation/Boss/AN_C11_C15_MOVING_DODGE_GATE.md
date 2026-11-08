# AN-C11–C15: First Dodge Activation and Moving-Dodge Gate

Status: offline prep complete; KI-199/KI-196 Lead build and PIE evidence pending.  
Lead owns `ENGINE_LOCK`, build, Editor, and PIE. Codex did not run Unreal.

## C-1099 route-provenance correction

The nominal legacy arms in C-1063/C-1067 did not enable `RPG_LEGACY_STARTUP=1`; treat those observations as DATA-default. They establish the tested DATA-default workaround only and do not establish legacy parity. Per C-1104, legacy is a parity control only and no new true-legacy first-dodge rerun is queued. The current acceptance scope is DATA-default, with same-run `[EncounterActivation] route=data` evidence. Keep prior raw logs unchanged.

## Findings and corrections

- C-980's `P_C980_BACKSTEP` moving cases are runtime-assigned and report press-time movement (legacy 486.8 cm/s; data 474.2 cm/s) followed by the quick roll. They prove the movement classification in that assigned setup only. They do not prove the current Source default or first-dodge activation.
- `Scripts/Editor/pie_er_default_wiring_dodge.py` has no runtime montage assignment. Its standing success predicate had retained the rejected `AM_ER_Backstep_Back` name. Updated it to require owner-approved `AM_ER_Backstep_Mixamo_V2`; the moving predicate continues to require `Dodge_Small_Forward_Roll_Montage`, press-time input >= 0.1, and speed >= 50 cm/s.
- C-1063 BUILD-261 reports 485/485 but first press still moves 0 cm; later presses move 96.6/97.8 cm. Preload/map priming did not fix the first press. KI-199 remains open and KI-196's default-wired moving acceptance remains unproven.
- `RPGDodgeTiming` now emits a first-press Development trace with the `Can Activate Ability?` return, all CreatedAbilities active flags and owned tags, stamina, and a next-component-tick ability active snapshot. It intentionally does not invoke a second `TryActivateAbilityByClass`; doing so would alter the input-path result. The pack-owned try-activate return is not directly observable from this project callback.
- The probe matches the Lead showcase's 2.2 s settle, `enter_combat`, R2 down for 0.7 s, and up-to-5 s combat-enabled polling. `FIRST_DODGE_CASE=standing` or `moving` selects the first input in a fresh process. Both scenarios run without runtime montage assignment and include two later control presses.

## Lead run matrix

Run four fresh Editor processes under the Lead's lock, preserving a separate output directory for each cell:

| Encounter route | `FIRST_DODGE_CASE` | Required first press |
|---|---|---|
| data | `standing` | zero direction input; `AM_ER_Backstep_Mixamo_V2`; backward capsule travel, no snap |
| data | `moving` | nonzero press-time input and >=50 cm/s; `Dodge_Small_Forward_Roll_Montage`; forward travel |

For each DATA-default fresh run, inspect the activation route witness first, then `draw_ready`, scenario/expected montage, first-press `Can Activate Ability?` query, `CreatedAbilities` active flags, owned tags, stamina, `first_dodge_activation_trace` before/after, montage, and capsule displacement. The two repeats are controls, not substitutes for the first press. Preserve the exact log when a query is unavailable; `CanActivate` and next-tick active state are not the hidden pack `TryActivate` boolean.

## Minimum Lead return fields (AS-C24)

Return one row per DATA-default scenario/process with: build ID and configuration; runner command and startup route selection; activation witness; raw-log path and SHA-256; draw-ready state/attempt; standing or moving scenario and expected montage; first input timestamp/press-time movement; first-press CanActivate and reachable activation-trace fields; ability-active/tags/stamina; montage and capsule travel; repeat control results; full process exit/completion status. Mark unavailable fields explicitly rather than inferring them. Route status is decided by the activation witness. This schema does not require a new run count or claim root-cause proof.

Example invocation (the Lead runner owns lock; this acceptance run selects DATA-default only):

```powershell
$env:FIRST_DODGE_CASE = 'standing'
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/probe_first_dodge_after_draw.py -Routes @('data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_AN_C11_C15_STANDING
$env:FIRST_DODGE_CASE = 'moving'
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/probe_first_dodge_after_draw.py -Routes @('data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_AN_C11_C15_MOVING
Remove-Item Env:FIRST_DODGE_CASE
```

## Validation

- `test_first_dodge_after_draw_contract.py`: 2/2.
- `test_dodge_activation_diagnostics_contract.py`: 3/3.
- `test_first_dodge_probe_fakes.py`: 2/2; fake standing and moving paths confirm draw-before-press ordering and press-time movement observables without importing Unreal.
- `py_compile` passed for both edited Editor probes. Document-link and diff checks are recorded in the current batch receipt.
- No full suite, native build, Unreal Editor, or PIE was run by Codex.
