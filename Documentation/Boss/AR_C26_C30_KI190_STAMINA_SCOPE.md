# AR-C26–C30 — KI-190 Strength stamina scope

Status: static policy/evidence audit complete. No stamina cost, loadout, Source row, or runtime setting was changed. KI-190 remains open for owner scope clarification; no owner decision is inferred here.

## C26 — Freeze wording and implementation boundary

Freeze v1.2 §20.1 (`Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md:850–859`) specifies Strength light posture 18, jumping-heavy posture 38, and **jumping-heavy stamina cost 35**. It does not say 35 for every Strength swing.

`RPGWeaponAttackTable::FillDefaults` currently sets Strength Light and JumpLight costs to `-1` (`RPGWeaponAttackTable.cpp:41–57`), which means no project-added cost. It assigns 35 to Strong, Charged, JumpHeavy and Knockdown for the Claymore style; Sword starter rows retain `-1`. Strong/Charged/Knockdown are tagged as proposals in the rows, while JumpHeavy is the Freeze-backed 35 row. `RPGSwingTracker.cpp:264–275` applies only the difference between a nonnegative table/override value and the pack's already-paid 15; `-1` leaves the pack payment alone. Thus current Strength Light/JumpLight cost is 15, and a 35 row adds 20 when enough stamina remains.

The phrase “35 per swing” in current issue/design summaries overstates the literal Freeze line. Whether to extend the authored JumpHeavy cost across other heavy categories or every category is a product-policy question, not determined by §20.1.

## C27 — What existing tests actually exercise

| Evidence | What it checks | Limit |
|---|---|---|
| `OneBossFight.Hit.WeaponTable` in `RPGAutomationTests.cpp:480–505` | Fresh table values including Strength Light posture, Strength JumpHeavy posture 38/cost 35, Dexterity values, and starter fallback. | It does not assert Strength Light `StaminaCost` at the line where Light is looked up. It is not a live stamina deduction test. |
| `pie_stamina_cost.py` header and lines 152–184; `TEST_PLAN.md:433` | Real press path for the Starter sword; base 15 when the row is `-1`; its 35/10 examples set `set_cost_override_for_test`. | Its 35-cost result is a test override, not evidence of the Strength table row/loadout. |
| `pie_builds.py:28–31,193–206,250–271`; `TEST_PLAN.md:441` BUILD-02 | Selects the actual Strength loadout, clears cost overrides, and compares real swing/stamina/posture/bleed observations to its row table; the recorded Gate 3 run says 103/103. Its table expects Strength Light/JumpLight 15 and Strong/Charged/JumpHeavy 35. | The result is a historical Lead PIE receipt, not package proof or a policy decision. Its comment attributes more of that matrix to Freeze than §20.1 literally specifies. |
| C-467 raw Strength log, `Docs/BossCombatReview/Execution/Claude/KI151/real_builds/strength/editor_raw.log:1729,1753,1905,1959,2016,2018` | Real Claymore row readback shows Light `stamina -1` / extra `+0.0`; Strong and Charged show row `35` / extra `+20.0` with 100 stamina at the first such heavy. Build choice is `Strength`/`ClaymoreCombatStyle` at `:1574–1583`. | This retained run is scoped to its logged cases and editor route; it does not establish owner policy, every category, both routes, package behavior, or a new run after current source changes. |

## C28 — Neutral alternatives (none selected)

| Option | Stated policy | Practical effect versus pack base 15 | Change required |
|---|---|---|---|
| A — 35 all swings | Every supported Strength swing category costs 35. | Adds 20 stamina beyond the pack's 15 on Light, JumpLight, Strong, Charged, JumpHeavy and any included Knockdown category. | Set explicit row costs to 35 for every in-scope category; update pure row contracts and live measurements. |
| B — 35 heavy categories | Keep Light/JumpLight at pack 15; charge 35 for the agreed heavy categories. | Adds 20 beyond the pack base for each in-scope heavy; preserves pack cost for light attacks. Current Claymore rows already use this general split, but the owner must define which categories count as “heavy.” | No broad policy rewrite if the present category set is approved; tighten row tests/docs and measure all covered categories. |
| C — pack base | Keep the pack's 15 for every Strength category. | No project-added stamina surcharge; JumpHeavy no longer matches the Freeze's 35 starting value. | Use `-1`/no extra for the supported rows and update tests/feel targets; this departs from Freeze §20.1's JumpHeavy starting value. |

No option is recommended or applied. If preserving the literal Freeze without extrapolation is preferred, the owner can specify 35 only for JumpHeavy and retain current/base costs for other categories; this would be a distinct narrower variant to record explicitly.

## C29 — Lead validation after policy selection

For the chosen policy, run the real `rpg.Build Strength` / Claymore loadout in fresh PIE sessions on legacy and selected-data routes (if both remain part of the test matrix), with package/source build identity recorded. Do not use `set_cost_override_for_test`, editor-property assignment, or test-only stamina hooks. Confirm the actual style is `ClaymoreCombatStyle`, the loadout is Idle, and the swing row reports the expected category/value. Start each trial at 100/100 stamina; capture before and at 0.4 s after the swing (before the pack's documented regeneration window) and retain the swing and hit-intake logs. Repeat five times for each supported policy category, restoring stamina between trials with the same declared Lead test setup. The matrix should include Light, JumpLight, Strong, Charged, and JumpHeavy; include Knockdown only if the owner includes it in “swing.” Return route, configuration/build identity, category, row value, before/after stamina, pack base, added cost, and montage/hit receipt. First update/compile and native/table contracts if policy changes Source; Lead owns build and PIE. These runs verify applied cost only; owner reviews feel separately.

## C30 — Bounded owner question

**For the Strength build, which stamina policy should the project implement: (A) 35 for every supported swing, (B) 35 for specified heavy categories while light attacks keep the pack's 15, or (C) the pack's 15 for all categories? If B, which attack categories count as heavy?**

The Freeze's explicit starting point is JumpHeavy = 35. The current Claymore table is a broader heavy-category implementation, and retained Lead evidence supports only its logged cases. No decision, implementation, or feel acceptance is recorded by this audit. The question is prepared for Claude's owner-facing review; Codex did not message the owner directly.
