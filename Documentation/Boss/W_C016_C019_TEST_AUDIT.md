# Queue W-C016–W-C019 — visual rules, parity regressions, timing guards

## W-C016 — mutation-style audit

The pure rule tests cover these high-value mutations already: invert the Development-build gate, treat zero as enabled, allow authored Tier 1 effects to be replaced, let preview fallback leak into a disabled build, accept empty paths, and weaken exact montage equality to case-insensitive/prefix matching. The remaining test additions should target combinations across rule boundaries (authored effect plus preview off, non-Development plus nonzero CVar) and keep the exact expected path source-cited. No production rule change is warranted by this audit.

## W-C017 — optional montage path properties

`RPGPresentationRulesTests.cpp` flips every character in the retained Boss01 montage path and checks that each mutation fails exact matching. Review C-933 caught that Unreal `FString` equality is case-insensitive, so the case-only variant correctly asserts a match (the helper uses the same `==`); suffix extension still must fail. The path comes from the existing authored test value; no new loaded-by-path asset literal was introduced.

## W-C018 — comparator regression coverage

Added regressions for semantic health tokens and L1d camera sample noise using values from retained BUILD-231 evidence (`pie_riposte_lethal_d5` lines 1735/1743 and `pie_legend_t1/compare.txt`). Existing tests cover typed L8 bounds (including retained 0.3670568 s fixture) and token-count/text comparisons; the iframe full-roll fixture in `test_a5_parity_driver_registration.py` asserts the real 30/60/120 FPS values (0.3666667/0.35/0.35 s) are inside run-independent authored bounds. These checks exercise the four noted comparator failures without embedding whole volatile receipts.

## W-C019 — timing interval independence

`test_timing_range_independence.py` parses each `Scripts/Editor/pie_*.py` driver and rejects timing `range_seconds` expressions that directly or transitively reference measured-duration/rate/sample names. The `duration` mutation self-test verifies arithmetic aliases do not bypass the scan. Known authored expressions such as `bounds`, `expected`, `tolerance`, and the authored clip `values` remain valid.

No Unreal or C++ build was run. C++ automation compilation remains with Claude.
