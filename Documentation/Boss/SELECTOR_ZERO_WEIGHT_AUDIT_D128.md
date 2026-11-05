# Queue D128 — selector zero-weight candidate audit

Date: 2026-11-03  
Method: static comparison of selector initialization/selection and current tests; no tests run.

## Behavior

`FRPGBossMoveSelector::Initialize` rejects any candidate whose weight is nonfinite, `<= 0`, or `> 1e6` with `Selector.Domain`. Therefore a literal zero-weight candidate cannot become initialized/eligible through the public selector path. This is separately distinct from candidates with positive weights that later fail model/cooldown hard filters.

When initialized, `Select` marks a candidate eligible only after hard filters pass, then scores it. If no candidate passes, selection still returns true with `ChosenIndex == INDEX_NONE`; the candidate traces retain refusal tokens. If eligible candidates exist, highest score wins, with lowest index retained on exact ties when no tie tier changes the selection. There is no zero-weight fallback path.

## Existing tests

`RPGBossMoveSelectorTests.cpp` explicitly rejects weight zero with `Selector.Domain`; tests a no-candidate initialization refusal; tests no eligible candidate as a successful Select call with INDEX_NONE and named per-card refusals; and tests ordinary deterministic ties. These match the intended current contract.

## Limits

The D127 report separately records positive subnormal products that may cast to score zero after successful initialization; that is not equivalent to an authored zero-weight input and could still be selected. No defect found for literal zero-weight handling. Static only; no tests run.
