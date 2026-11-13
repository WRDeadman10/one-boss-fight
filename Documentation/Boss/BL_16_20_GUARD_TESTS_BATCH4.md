# BL-16..20: guard tests, batch 4 (ChannelDrain, ComboAbort, Combo)

Lane BL, batch 4 of 20. I continued straight from batch 3 per X-2165 ("continue into the next batch after this one"); the headers follow the BL-01..05 queue. C (implementer), 2026-11-12.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build and automation run are pending with the lead.
- **Checked by hand:** every assertion was traced against the header source, and each file has a positive control.

## BL-19: re-verification (by hand, against header and existing tests)

| Header | Confirmed gap (header line) | Existing coverage, so not repeated |
|---|---|---|
| `RPGBossChannelDrainRules.h` | `TickCount` returns the 65 cap (`:12`); `Start<0`, `End<=Start`, a negative interval and non-finite inputs give 0 (`:10`); `CappedHeal` gives 0 for `HealFraction>1` or `<=0`, `BossHealth<0`, `BossMaxHealth<=0`, non-finite inputs, negative accepted HP, and health above max (`:19-20`) | `RPGBossMoveCardTests.cpp:169-185`: the normal cap and heal cases, zero accepted HP, a full boss, a zero interval, and float endpoint rounding |
| `RPGBossComboAbortRules.h` | a negative `AcceptedHits` never aborts (`:10`, `==0`) | `RPGBossComboAbortRulesTests.cpp`: hits 0..19 and the flag cases |
| `RPGBossComboRules.h` | `EdgeDomain` for a negative `MinRangeCm`, a negative `MaxAbsYawDegrees`, and infinite min, max, yaw or tempo (`:62-64`); a `NAME_None` node id gives `DuplicateNode` (`:56`); the gate id is consumed **before** the Target check (`:80-81`); an infinite gate yaw gives `Combo.Target` (`:81`) | `RPGBossComboTests.cpp:33-45, 77, 105-106`: duplicate id, reversed band, yaw above 180, NaN range or tempo, a duplicate gate, an invalid target, a NaN range gate |

## BL-16..18: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-16 | `Source/OneBossFight/Tests/RPGBossChannelDrainGuardTests.cpp` | `OneBossFight.Framework.ChannelDrain.Guards` | **Controls:** 4 ticks; a heal of 7. **TickCount:** a ratio of exactly 65 and of 1000 both give 65; 7 fail-closed inputs give 0. **CappedHeal:** 12 fail-closed cases give 0. |
| BL-17 | `.../RPGBossComboAbortGuardTests.cpp` | `OneBossFight.Framework.ComboAbort.Guards` | **Control:** `(true, 0, true)` aborts. `AcceptedHits` of -1 and of `MIN_int32` do not abort. |
| BL-18 | `.../RPGBossComboGuardTests.cpp` | `OneBossFight.Framework.Combo.Guards` | A self-contained fixture: A → B, valid (control). **EdgeDomain:** a negative min range, a negative yaw, and infinite min, max, yaw or tempo. **`NAME_None`** id → `DuplicateNode`. **Gate consumption:** a gate with an invalid target returns `Combo.Target` yet sets `LastGateId=7`, and the node is unchanged; replaying id 7 (now with a valid target) is `Ignored`/`GateConsumed`. **Yaw:** +Inf or -Inf gives `Combo.Target` (control: a finite yaw continues). |

## BL-20: status

- **Names:** the new automation names are unique; the existing tests are `…ChannelDrain`, a MoveCard test, `…ComboAbort.Rules` and `…Combo.Validate`/`Step`.
- **Portability:** `uint64` is compared with `TestTrue(==)` rather than relying on a `uint64` `TestEqual` overload.
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
