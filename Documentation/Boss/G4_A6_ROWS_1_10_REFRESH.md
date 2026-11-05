# Queue G — A6 active-value rows 1–10 refresh

**Scope:** static read-only reconciliation of Antigravity's `A6_HARDCODED_VALUE_AUDIT.md` against current active source. This document does not edit Antigravity's audit or its test file, and it does not make asset/runtime claims.

## Rows 1–5 (G024)

| Audit row | Current source and behavior | Data alternative / disposition | Coverage limit |
|---:|---|---|---|
| 1 | `RPGFrameworkMoveExecutor.cpp:216` uses `Delta * CardPlayRate * 1.5` as a playback early-stop slack threshold, floored by `BlendOutSeconds`. The audit's cited line 127 is stale. | `BlendOutSeconds` is already profile data, but there is no early-stop multiplier field. Treat 1.5 as executor correctness tolerance, not combat tuning; retain as invariant pending playback evidence. | `RPGBossExecutorHarnessTests.cpp` exercises state/rearm/abort lifecycle; no direct montage-timing assertion for this multiplier was found in the reviewed test inventory. |
| 2 | `RPGFrameworkBossCharacter.cpp:897` displays initialization failures for 10 seconds. Audit line 445 is stale; this is diagnostic UI duration. | No profile alternative needed; retain as diagnostic constant. | No test of viewport display duration identified; not a gameplay contract. |
| 3 | `RPGFrameworkBossController.cpp:34` projects the nav target at `(BandMinCm + BandMaxCm) * .5f`. Audit line 17 is stale. This is a shared midpoint derived from profile band endpoints. | **Kept in code: formula.** C-801 permits only literal-constant migration with the same formula and evaluation order. A ratio field would change the formula; no new profile field is justified. | `RPGFrameworkRuntimeTests.cpp` validates band profile domains; no controller target-ratio variation test identified. |
| 4 | `RPGFrameworkProofFixture.cpp:76` uses the same midpoint expression for fixture readiness. Its cited line remains current. | Fixture mirrors the controller calculation; it is test/setup behavior, not boss authoring data. **Kept in code: formula** under C-801; do not introduce a separate fixture field or alter midpoint evaluation. | No controller-vs-fixture equality assertion identified. |
| 5 | `RPGFrameworkProofFixture.cpp:97` displays fixture errors for 10 seconds. Its cited line remains current. | Test-harness diagnostic only; retain. | No viewport-duration test identified. |

## Rows 6–10 (G025)

| Audit row | Current source and behavior | Data alternative / disposition | Coverage limit |
|---:|---|---|---|
| 6 | `RPGBossDormantWakeRules.h:13` caps missing/invalid-montage wake grace at 0.15 seconds. | Safety bound for startup recovery; not an authored combat delay. Retain. | `RPGBossDormantWakeTests.cpp:12–22` exercises the grace boundary and invalid expected lengths. |
| 7 | `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:54` limits `HitMaxSubsteps` to 64 when damage is enabled. The audit's line 45 and named `FRPGBossFrameworkProfileLimits::MaxSweepSubstepsLimit` do not match current declarations; no such named constant was found. | Schema/CPU-work bound, not a live authorable sweep value. Retain; describe as validation upper bound, not runtime default. | Profile validation coverage is in `RPGFrameworkRuntimeTests.cpp`; does not establish a particular authored asset value. |
| 8 | `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:70` accepts nonzero posture `StaggerSeconds` only in `[0.5, 60]`. The audit's line 61 is stale. | Schema bounds, not an individually tuned boss value; retain. | `RPGFrameworkRuntimeTests.cpp:312–313` covers below/above rejection, plus posture validation paths. |
| 9 | Same current check at `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:70` supplies both the 0.5 lower and 60 upper bound; these are not separate declarations at the old cited line 61. | Same disposition as row 8: schema limits, not data fields. | Same coverage as row 8; no claim of asset inspection. |
| 10 | `Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp:155` caps both `RepeatMemory` and `AttackCount` at 8. The audit's line 100 and named `FRPGBossFrameworkProfileLimits::MaxAttackSequenceDepth` do not match a current declaration; no such named constant was found. | Validation bounds over two profile fields, not one runtime depth setting. Retain as schema limits; fix the audit's conflated description. | `RPGFrameworkRuntimeTests.cpp` has domain cases for attack count and repeat memory; no serialized profile asset was inspected here. |

## Classification and next action (G026–G027)

- Gameplay-tuning candidate under the earlier G026 screen: only the shared nav-band midpoint policy in rows 3–4. C-801 narrows migration to literal constants with unchanged formula/order; the midpoint is a formula, not a literal. Keep both occurrences in code.
- Safety/correctness invariant: row 1 playback termination slack and row 6 wake grace cap.
- Diagnostics: rows 2 and 5.
- Schema/CPU bounds: rows 7–10. Rows 7 and 10 also contain stale or unsupported symbol names in the Antigravity audit; rows 1–3, 7–10 have stale file lines.
- C-801 released the compatibility decision. **G028–G030 disposition: no field migration.** Rows 3–4 are explicitly `kept in code: formula`; changing them to use a ratio would violate the same-formula/evaluation-order rule. There is no profile default literal to test for bit identity, so no Source change or fabricated profile field is warranted from this audit.

**Evidence limit:** source and test-file inspection only. No build, test run, Unreal/PIE, profile asset inspection, or owner/Lead runtime acceptance was performed.

## Queue H031 re-audit after opt-in activation integration (2026-11-04)

C-800's selected route adds a definition record, strict census, binding and activation caller, but it does not change any A6 row's value owner, formula, consumer, or compatibility class. Rows 1–10 still resolve as: 1/6 correctness or safety, 2/5 diagnostics, 3/4 formulas retained in code, and 7–10 schema/CPU bounds. No newly authorable literal-only gameplay number with a current consumer and bit-identical old default was found. Therefore H032 has no supported candidate; H033–H035 remain blocked on that missing candidate rather than creating an artificial field/adapter. Source references remain the ones in the row table above; this is a static re-audit only and makes no claim about serialized profile assets or runtime values.
