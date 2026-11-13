# BL-76..80: guard tests, batch 16 (PackParry, ParryCost, ParryGrade)

Lane BL, batch 16 of 20. I continued per X-2193 ("continue after the batch"); the headers follow the BL-01..05 queue. C (implementer), 2026-11-12.

**Three new test files only.** No production source edits, and no Unreal, build, PIE, commit or push.
- **Not compiled or run:** the engine-lock acceptance build is pending with the lead.
- **Checked by hand:** every assertion was traced against the header source.

## BL-79: re-verification and observability (by hand)

| Header | Audit gap (line) | Existing coverage, not repeated | Discriminates? |
|---|---|---|---|
| `RPGPackParryRules.h:24-41` | after the wait, a negative or non-finite `RequiredSeconds` or `LossTolerance` → Rejected (`:35-36`); the exact tolerance boundary confirms (`:40`) | `RPGPackParryContactTests.cpp:23-35`: pending at 0.099, confirmed at 0.1, gain confirmed, loss rejected, unknown health, NaN health or elapsed | **Yes, all:** without the guard each would be Confirmed. A negative tolerance is shown with a health **gain** (102 from 100), since `102 < 101` is false. |
| `RPGParryCostRules.h:17` | `StaminaAfter` with a negative stamina or cost → 0 | `RPGParryCostTests.cpp:21-26` (refund, whiff, floor, NaN stamina, Inf cost); property; infinite `CanPress` operands | **Negative cost: yes** (it would give 14). **Negative stamina: no, equivalent**, because `Max(0, neg - cost>=0)` is already 0 |
| `RPGParryGradeRules.h:23` | an infinite offset or window → None | `RPGParryGradeTests.cpp:13-23` (boundaries, closing edge, negative, zero window, NaN); the 40 and 80 % adjacent cases; the property test | **+Inf window: yes** (offset/Inf = 0 would grade Perfect). **±Inf offset and -Inf window: no, equivalent** (already refused by `>= Window`, `< 0` and `<= 0`) |

**Excluded:** `ParryRefund` with stamina above max returns the max, which lowers stamina. The audit marks this as a product-decision item, so no test asserts it as a gap.

## BL-76..78: tests

| Task | File | Automation test | Cases |
|---|---|---|---|
| BL-76 | `Source/OneBossFight/Tests/RPGPackParryGuardTests.cpp` | `OneBossFight.Parry.PackParryGuards` | **Control:** confirmed. **Rejected:** Required -1; Required NaN; tolerance -1 with a gain; tolerance NaN; tolerance +Inf. **Boundary:** a loss of exactly 0.5 with tolerance 0.5 confirms (99.5); a loss of 0.75 rejects (99.25). |
| BL-77 | `.../RPGParryCostGuardTests.cpp` | `OneBossFight.Framework.ParryCost.Guards` | **Control:** a whiff gives 6. A cost of -4 gives 0, whiffed or parried (**discriminates**). A stamina of -1 gives 0 (**equivalent**, documented). |
| BL-78 | `.../RPGParryGradeGuardTests.cpp` | `OneBossFight.Framework.ParryGrade.Guards` | **Control:** 0.05 of 0.25 is Perfect. A +Inf window gives None (**discriminates**). ±Inf offset and -Inf window give None (**equivalent**). |

## BL-80: status

- **Names:** the new names are unique (each found in exactly one file).
- **Defects:** none indicated.
- **Pending:** the engine-lock build.
