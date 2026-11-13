# BL-11..15: guard tests, batch 3 (ArenaEdge, BakeFreshness, BlockChip)

Assigned by X-2165 and X-2168 (lead Codex) to C (implementer), 2026-11-12. This is lane BL, batch 3 of 20.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build and automation run are pending with the lead.
- **Positive controls:** each file has one, so a guard cannot pass vacuously.
- **Scope:** limited to the confirmed gaps. Existing coverage is not repeated: separate zero fingerprints, the centre case, a zero margin, and NaN or infinite damage and fraction (X-2168).

## BL-14: re-verification (by hand, against header and existing tests)

| Header | Guard line | Confirmed gap | Already covered (not repeated) |
|---|---|---|---|
| `RPGBossArenaEdgeRules.h` | `:12` `Boss.ContainsNaN()\|\|Center.ContainsNaN()\|\|…ArenaRadiusCm<=0.\|\|MarginCm<=0.` | NaN Boss or Center; negative radius; negative margin | centre point (distance at or below `SMALL_NUMBER`) and a zero margin are in `RPGBossArenaEdgeRulesTests.cpp` |
| `RPGBossBakeFreshnessRules.h` | `:10` `Current!=0&&Baked!=0&&Current==Baked` | **both** fingerprints zero: equal, yet not fresh | a single zero fingerprint is in `RPGBossBakeFreshnessRulesTests.cpp` |
| `RPGBossBlockChipRules.h` | `:10` `…ChipFraction<0.…` | a negative finite `ChipFraction` → 0 | NaN or infinite damage and fraction, and fraction above 1, are in `RPGBossBlockChipRulesTests.cpp` |

## BL-11..13: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-11 | `Source/OneBossFight/Tests/RPGBossArenaEdgeGuardTests.cpp` | `OneBossFight.Framework.ArenaEdge.Guards` | **Control:** a boss at 950 cm in a 1000 cm arena with a 200 cm margin gets pressure > 0 (0.75) and an inward heading of (-1, 0). Then NaN in Boss X, Boss Y, Center X or Center Y, a negative radius, or a negative margin each give zero pressure **and** a zero heading. |
| BL-12 | `.../RPGBossBakeFreshnessGuardTests.cpp` | `OneBossFight.Framework.BakeFreshness.Guards` | **Control:** equal non-zero fingerprints are fresh. `IsFresh(0, 0)` is false. |
| BL-13 | `.../RPGBossBlockChipGuardTests.cpp` | `OneBossFight.Framework.BlockChip.Guards` | **Control:** `GuardedDamage(100, .25) == 25`. A fraction of `-.25` and of `-1e-9` each give 0. |

## BL-15: status

- **Names:** the automation names are new; the existing tests for these headers are named `…ArenaEdge.Rules`, `…BakeFreshness.Rules` and `…BlockChip.Rules`.
- **Defects:** none indicated. The source was not touched.
- **Pending:** the engine-lock acceptance build.
