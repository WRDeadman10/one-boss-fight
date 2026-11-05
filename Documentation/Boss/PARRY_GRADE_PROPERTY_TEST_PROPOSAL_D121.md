# Queue D121 — parry-grade property test proposal

Date: 2026-11-03  
Scope: deterministic test design from the current pure grade rule; no source/test edits or execution.

## Contract from source

`Source/OneBossFight/Player/RPGParryGradeRules.h` rejects non-finite offset/window, negative offset, nonpositive window, and the half-open closing edge `OffsetSeconds >= WindowSeconds`. For remaining inputs, `Fraction = OffsetSeconds / WindowSeconds`; grade is Perfect when fraction `< .4`, Good when `< .8`, otherwise Late. This proposal uses those source constants; it does not infer new gameplay thresholds.

`Source/OneBossFight/Tests/RPGParryGradeTests.cpp` already checks representative values, exact `.4`/`.8` values for a `.25`-second window, invalid inputs, a 10,001-point monotonic sweep at one fixed window, and decreasing posture scale. The proposal adds varied valid-window generation; it should complement, not duplicate, the existing sweep.

## Proposed bounded property

- Use a fixed `FRandomStream` seed recorded in the test, and generate 128 windows in a finite positive interval such as `[0.01, 2.0]` seconds. These bounds are only a numerical test domain, not product-approved gameplay limits.
- For every generated window, generate bounded offsets from `0` through `Window`, plus explicitly constructed valid offsets strictly below `Window`. Map `Perfect < Good < Late < None` to ranks `0..3`.
- Sort each window's valid offsets ascending and assert rank never decreases. Separately assert every `Offset < Window` is not None, and `Offset == Window` is None.
- For each window, assert source-derived boundaries: `nextafter(.4*Window, -∞)` is Perfect when nonnegative; exact `.4*Window` is Good; `nextafter(.8*Window, -∞)` is Good; exact `.8*Window` is Late. Assert boundaries only where floating-point representability and positive domain make the values valid; test exact source comparisons separately to avoid claiming real-time precision.
- Keep invalid/nonfinite cases as explicit examples (already partially covered). Do not generate unbounded values, assert timing fidelity, or claim caller/runtime wiring from a pure helper test.

## Acceptance / limits

Proposal provides a repeatable seed, bounded case count, and monotonic invariant derived from the current implementation. It does not change the rule or claim tests passed. Property checks cannot replace adjacent representable boundary fixtures, and the proposed test-domain endpoints are harness choices only.
