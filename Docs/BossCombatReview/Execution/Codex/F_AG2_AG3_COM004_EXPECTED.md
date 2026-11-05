# F-AG2 / F-AG3 — BOSS-COM-004 distinct live outcome follow-ups

## Setup

The existing framework B_GUARD and B_PARRY logs both show `Continue next=B`; they establish Guarded and Parried inputs, but do not prove different follow-ups. `create_distinct_outcome_content.py` creates a fresh framework profile/map only. Its graph at node A maps Hit->B, Whiff->C, Guarded->D, and Parried->E. D and E have distinct node IDs and both use an already-authored profile card. It refuses existing destinations and uses `LevelEditorSubsystem.new_level` plus `EditorLoadingAndSavingUtils.save_map` for the new map; it never duplicates or loads a map in the setup script. It asserts the profile card MoveIds are distinct and every graph MoveId resolves to one of them. Boss spawn x=500 versus PlayerStart x=0 is asserted to start at least 80 cm outside the source profile band. Every authored combo edge/node and fixture property has immediate readback assertions.

Lead runs the setup script through the maintained editor-script launcher, then runs each arm from `Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1`:

```powershell
$root = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Codex\F_AG2_AG3_COM004'
$map = '/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofComboOutcomeFAG23'
$f4 = 'C:\UnrealProject\OneBossFight\Docs\BossCombatReview\Execution\Claude\F4\run_pie.ps1'
& $f4 -Map $map -OutDir "$root\control" -Task F-AG23_COM004_control
& $f4 -Map $map -OutDir "$root\guarded" -Task F-AG2_COM004_guarded -Console 'rpg.BossProofPlayerGuard 3;rpg.BossProofPlayerGuardSeconds 12'
& $f4 -Map $map -OutDir "$root\parried" -Task F-AG3_COM004_parried -Console 'rpg.BossProofPlayerGuard 5;rpg.BossProofPlayerGuardSeconds 12'
```

Do not treat the command itself as proof that a state was reached. Retain each command, full raw log, result, and hash. Existing `B_COMBO3/pie_normal` remains the historical Hit/Whiff control; the new no-hook control additionally checks whatever ordinary Hit/Whiff edges it naturally reaches.

## Control

- The new no-hook run must use the generated framework map/profile and show an ordinary Hit or Whiff combo gate, followed by its corresponding B or C step if the corresponding outcome occurs.
- Retain existing B_COMBO3 Hit and Whiff rows as cross-checks, but do not count them as evidence for this new graph's D/E branch.
- The two defense arms must use separate fresh PIE sessions and the same generated map/profile.

## PASS

- Guarded arm: a same-card live `guard_state ... guard=Guarded` feeds a `combo_gate ... outcome=Guarded ... result=Continue next=D`, then a `combo_step node=D move=Move_Sevarog_HeavySlam_F7` proves the distinct follow-up actually started.
- Parried arm: a live parry contact is identified and feeds `combo_gate ... outcome=Parried ... result=Continue next=E`, then `combo_step node=E move=Move_Sevarog_HeavySlam_F7` proves the different follow-up. If the real parry route instead fails to produce a parry state, mark setup inconclusive; do not infer Parried from the console command.
- A no-hook Hit or Whiff control follows only its mapped B or C step. It must not be used to infer defense branch behavior.
- Logs include successful terminal `[FrameworkProof] RESULT` entries and validate with the current framework log validator.

## FAIL

Fail if the graph readback differs from A:{Hit->B, Whiff->C, Guarded->D, Parried->E}, Guarded routes to anything but D, Parried routes to anything but E, the matching distinct `combo_step` is absent, the no-hook control is misrouted, or evidence relies only on `combo_gate next=` without the subsequent step. Missing live input readiness/parry state is inconclusive setup, not a policy failure. Do not modify the witness ledger; Lead/Antigravity reconcile statuses.

## Token checks

- `[FrameworkProof] guard_hook_armed`, `[FrameworkProof] guard_tags`, and `[FrameworkProof] guard_state` for Guarded.
- `[FrameworkProof] parry_press` / `[FrameworkProof] parry_reaction` where emitted, plus `[FrameworkProof] guard_state ... guard=Parried` for Parried.
- `[FrameworkProof] combo_gate` and subsequent `[FrameworkProof] combo_step` with expected node B/C/D/E.
- `[FrameworkProof] RESULT` and the editor runner result for each run.
