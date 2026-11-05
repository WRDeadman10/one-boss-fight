# BUILD-145 independent review and ledger note draft

Read-only review of the uncommitted BUILD-145 changes. No source files were edited and no build or tests were run.

## Critic review

- **No BUG found** in the reviewed paths. Both accepted window contacts and the grab damage path classify the player's guard before calling the damage resolver (`RPGFrameworkMoveExecutor.cpp:249-250`, `367-368`). Guard counters increment only for accepted damage (`:251`, `:369`).
- **No restart/Rearm counter defect found.** The counters are cumulative like the existing accepted-hit counter. Combo gates compare against per-card/root snapshots, and encounter restart clears combo state; accumulated totals do not leak into the next combo's outcome.
- **No shipping hook leak found.** The CVar declarations and hook execution are inside `!UE_BUILD_SHIPPING` guards (`RPGFrameworkBossCharacter.cpp:28-32`, `:257-269`).
- **No behavior change when no guard tag is present found.** `Classify(false, false)` returns `None` (`RPGBossGuardTests.cpp:11`); the observer does not alter damage and the combo outcome falls back to Hit/Whiff.
- **NIT — comment tag mismatch:** `RPGFrameworkMoveExecutor.h:43` says `parry (Ability.Parry)` while classification reads `Status.ParryActive` (`RPGFrameworkMoveExecutor.cpp:249`). The code uses the observed status tag; the header comment should match.

## Replacement note drafts (both statuses remain PARTIAL)

### BOSS-COM-004 — Explicit hit-confirm policy

Live PIE now witnesses the Guarded edge: `Claude/B_GUARD/pie_block6/editor_raw.log:2142` logs `guard_state instance=3 ... guard=Guarded outcome=ERPGDamageOutcome::Accepted`, and `:2322` logs `combo_gate gate=3 node=A outcome=Guarded ... result=Continue next=B`. Hit/Whiff outcomes remain live-witnessed. Guarded and Parried classification is unit-tested in `Source/OneBossFight/Tests/RPGBossGuardTests.cpp:11-14`; the Parried edge still lacks live witness because the shipped player has no `GA_PlayerParry`. `Claude/B_GUARD/pie_abilities8/editor_raw.log:2178` records `hasParryAbility=0` (and `hasGuardAbility=1`); see KI-153. Keep PARTIAL until the Parried branch is witnessed live.

### BOSS-HIT-008 — Central defense order

The damage resolver decision hierarchy remains unit-tested (`Source/OneBossFight/Tests/RPGAutomationTests.cpp:159-179`). BUILD-145 observes guard state before `Resolve` in both accepted-contact paths, and live PIE records a Guarded contact at `Claude/B_GUARD/pie_block6/editor_raw.log:2142`; this is observation only and does not establish that blocking/parrying changes or prevents health damage. Parried is unit-tested only (`Source/OneBossFight/Tests/RPGBossGuardTests.cpp:11-14`), with no live parry witness because the shipped player has no `GA_PlayerParry` (`Claude/B_GUARD/pie_abilities8/editor_raw.log:2178`, `hasParryAbility=0`; KI-153). Keep PARTIAL pending live defense evaluation before health damage, including a live Parried case.

## Citation verification

The quoted Guarded and combo-gate records were checked directly in `pie_block6/editor_raw.log` at lines 2142 and 2322. The `hasParryAbility=0` record was checked directly in `pie_abilities8/editor_raw.log` at line 2178. All cited paths and line numbers refer to the current uncommitted working tree evidence.
