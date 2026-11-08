# C-1013 — weapon-style block-reaction hook hotfix

## Lead evidence

C-1013 reports BUILD-251 GREEN 484/484. With `IA_Block` held, `GA_PlayerGuardBlock_C` is active. On the data route, a blocked boss hit at 2.60 s activates `GA_Sword_BlockReaction_C`; `Status.Blocking` is present in the owned tag set. The earlier hook searched for the nonexistent generic name `GA_BlockReaction_C`. The legacy probe had no blocked contact in its former window. Lead recommends 220 cm, facing the boss, and a guard phase up to 25 s.

## Source change

- `RPGGuardCounterRules::IsBlockReactionAbilityClass` accepts the exact `BlockReaction_C` class-name suffix, covering weapon-style classes without matching `GA_PlayerGuardBlock_C`.
- `URPGDodgeTiming` refreshes the list of matching pack-created abilities once per second and treats any active matching variant as the reaction event.
- The existing `Status.Blocking` condition and reaction rising-edge gate remain in place.
- Native automation cases cover sword and another style, the guard-input ability exclusion, and a near-match without the complete suffix. They are authored but not run by Codex.
- `pie_er_guard_counter.py` positions the player 220 cm from the boss, facing it, and waits up to 25 s while injecting `IA_Block` each tick. Existing source-confirmed R2 behavior is unchanged.

## Validation and remaining gate

Python AST parsing and scoped `git diff --check` are the local checks. Codex did not build, run native automation, launch Unreal, or run PIE. Lead owns BUILD-252 and both-route reruns; expected proof is `guarded_contact_confirmed=True`, followed by the R2 counter hit using `AM_ER_Attack_GuardCounter`, kind `Strong`, `StrongMeleeAttackData`, and a measured boss HP decrease. Until then KI-198 remains open.
