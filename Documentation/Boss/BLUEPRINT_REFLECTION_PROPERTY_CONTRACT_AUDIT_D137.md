# Queue D137 — Blueprint reflection property contract audit

Date: 2026-11-03  
Method: source-only inventory of literal reflected field lookups; no live Blueprint/UFunction inspection.

## Literal properties and expected reflection kinds

| Literal | Source expectation / use | What is not proven by source |
|---|---|---|
| `CreatedAbilities` | `FArrayProperty`; inner must cast to `FObjectProperty`; iterated as ability UObject references | Actual ASC property exists, exact container/inner types and live contents |
| `AbilityTags` | `FStructProperty` assigned an `FGameplayTagContainer` | Actual function parameter struct type and whether the target function has it |
| `AttributeTag` | `FStructProperty` assigned an `FGameplayTag` on attribute calls | Actual parameter's struct type, name, direction, and function signature |
| `Value` | `FNumericProperty`, read via numeric getter or written via floating-point setter | Actual output/input direction, numeric subtype, units, and compatibility across Get/Set variants |
| `bForceActivation` | `FBoolProperty`, set true only when caller asks for forced activation | Actual parameter exists/is input and semantics match source comment |

The helper uses `FindFunction` for named Blueprint functions and `FindPropertyByName`/`FindFProperty` for fields. `SetTag`, `ReadNumber`, and guarded `CastField` operations fail softly when the expected reflected type is absent; the outer call can still return success if the function itself was found, so a type/name mismatch may leave zero/default parameters or output rather than a named schema error. This makes runtime reflection evidence important.

## Contract boundary

These are the names/types the C++ caller expects. They are not claims that the current pack Blueprint assets expose those exact signatures. Do not treat this inventory as a successful live reflection check; actual target class, property owner, property flags, type, and function parameter layout remain UNKNOWN until queried in the intended project build/editor.
