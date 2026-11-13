# BM-31..35: parry lifecycle and selector underflow (lane BM, batch 7 of 10; KI-175 / KI-176 / KI-181)

C (implementer), 2026-11-12.

New file: `Scripts/Tools/test_parry_selector_static_pins.py`. **No source change. Nothing compiled or run.**

**Scope correction (honest):** the plan said "native tests". Re-reading the KIs:
- KI-175 needs live same-pawn reuse evidence, and KI-176 needs an actual stamina-maximum read failure. Both say there is **no deterministic offline repro**.
- A KI-181 native test would need compiled move cards and a model through the selector's fixture, which lives in another translation unit. Writing that uncompiled would be speculative.

So this batch **re-verifies the KIs against the current code and pins the exact source facts** in a static test. Any change to those facts fails the test and forces re-triage.

## Re-verification (current code)

| KI | Fact (current line) | Status |
|---|---|---|
| KI-175 | `RPGParry::FState State;` is now at `RPGPlayerParry.h:83` (the KI cites `:65`). The component has **no** whole-state reset (`State = FState()` or `= {…}`). | **Open, unchanged.** It needs live lifecycle evidence; the cite moves to `:83`. |
| KI-176 | `RPGPlayerParry.cpp:222-223`: the refund is capped by `ParryRefund(After, Max, Paid)` only when the max is readable and finite; otherwise `After += PaidStaminaCost * .5` (uncapped). The KI cites `:159-170`. | **Open, unchanged.** It needs an attribute-failure fixture; the cite moves to `:222-223`. |
| KI-181 | `RPGBossMoveSelector.cpp:66`: `T.Score = float(C.Weight*RangeFactor*Repeat*Pattern)`. The factors are `float` (`.h:19-23`), and `RangeFactor`, `Repeat` and `Pattern` are `double`, so **the product is computed in double and only the narrowing to `float` can flush it to zero.** | **Open, analysis refined** (below) |

## KI-181 refinement (traced by hand and checked arithmetically)

- **The product itself doesn't underflow:** `1e-40f` is a positive subnormal float, `1e-40 × 1e-40 = 1e-80` is fine in double, and the narrowing gives `0.0f`. The test checks this with an IEEE single-precision round trip.
- **Selection effect** (`:67`): the candidate stays `bEligible` with `Score = 0`. It is chosen only if it is the **first** eligible card and no later card scores above 0; any positive-scoring later card replaces it.
- **Reachability:** authored factors are documented as `(0, 1e6]`, but nothing rejects subnormals. No authored profile uses them, which is consistent with the KI text.

## Tests

`python -m unittest discover -s Scripts/Tools -p test_parry_selector_static_pins.py -v` → **`Ran 5 tests ... OK`**.

| Test | Pins |
|---|---|
| `Ki175ParryStateHasNoReset` | the state member is present; no whole-state reset |
| `Ki176UncappedRefundBranch` | the capped branch and the uncapped `else` |
| `Ki181SubnormalScoreUnderflow` | the score expression; all five factors are `float`; the double-product, float-narrowing underflow arithmetic |

## Limits

- These are static text pins, not behavior tests: they detect change, not correctness.
- The KI-175/176 runtime behavior and the KI-181 in-engine selection stay **engine-gated**, and any change to them is owner- or lead-gated, as the KI rows say.
- **Proposed KNOWN_ISSUES cite updates:** KI-175 → `.h:83`; KI-176 → `.cpp:222-223`.
