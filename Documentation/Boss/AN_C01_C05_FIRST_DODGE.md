# Queue AN C01-C05 — first standing dodge after draw

## Evidence and diagnosis

Lead C-1061 reproduced the first-standing-dodge failure in two no-assignment data-route runs. In `Docs/BossCombatReview/Execution/Claude/P_SHOWCASE/showcase_def1.log:1895-1896`, `FlushAsyncLoading(413)` immediately precedes press 1; the handler reports `applied 1, dodge running 0`. At `:1897-1899` the first observation starts with no movement, and `:3003` records press 2. `showcase_mix2.log:1640-1642` independently shows the same first-press flush and result. Lead reports reps 2/3 move 84/88 cm.

The C-1061 receipts initially made streaming/callback order and draw/equip input state plausible hypotheses. C-1063 later reports BUILD-261 with preload/map-prime logs, yet the first press still moved 0 cm while presses 2/3 moved 96.6/97.8 cm. This shows preload/map priming did not fix the bug; first-press ability activation/dispatch is now the leading question, not an established cause. The retained logs still lack the live `Can Activate Ability?` result and input-buffer state at dispatch.

## Source change

`URPGDodgeTiming::BeginPlay` synchronously loads the default soft `BackstepMontage` into a transient strong reference; `OnDodgePressed` uses the resident montage. The speculative map-prime code described in X-1478/X-1480 was removed after review. C-1063's BUILD-261 evidence shows the preload/map-prime build still failed the first press. The preload remains but is not a root-cause fix; KI-199 remains open.

## Test-first and probe

- `Scripts/Tools/test_first_dodge_after_draw_contract.py` was authored before the source change. Its first run failed because BeginPlay lacked the preload; after implementation it passed 1/1.
- `Scripts/Editor/probe_first_dodge_after_draw.py` is Lead-run only. It now matches the Lead showcase's 2.2 s setup delay, combat entry, 0.7 s actual R2 draw, and combat-enabled polling. Separate fresh runs select standing or moving as the immediate first dodge and then perform two repeat controls. It logs montage presence, displacement, movement input, stage, press count and backstep count. Run under `ENGINE_LOCK`; no runtime assignment or Content write is intended.
- Python syntax compilation passed. `git diff --check` passed. C++ build/native suite and PIE are pending Lead; no Unreal process was started by Codex.

## Acceptance still required

Lead rebuilds the first-press diagnostics and runs both probe modes on both routes. Standing pass requires `AM_ER_Backstep_Mixamo_V2`; moving pass requires `Dodge_Small_Forward_Roll_Montage` with nonzero press-time input/speed. Both require displacement and working repeats. Inspect the first press's `Can Activate Ability?`, CreatedAbilities active flags, owned tags, stamina and next-tick active state. The pack's `TryActivateAbilityByClass` return is not directly exposed by this callback; do not infer it from `ApplyClip`.
