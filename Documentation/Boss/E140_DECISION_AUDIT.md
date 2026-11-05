# E140 — selector tie-order compatibility

**Decision:** No order-independent compatibility promise is established. **Authority:** project owner if replay compatibility must survive candidate reordering or content edits.

With `TieBand == 0`, strict-greater replacement leaves the first input candidate as the exact-tie winner; with nonzero tie band, candidate indices are collected in input order and the seeded stream chooses an index (`RPGBossMoveSelector.cpp:64-81`). Tests now cover zero-band first-input behavior and same-seed permutation behavior: same index is picked but identity follows the permuted order (`RPGBossMoveSelectorTests.cpp`, `FBossMoveSelectorZeroBandPermutation` and `FBossMoveSelectorSeededTieOrderPermutation`). Therefore repeatability is scoped to the same ordered candidate set, selector state, and seed. No cross-order identity guarantee is documented or needed unless the owner requests replay compatibility across authored-order changes.

Static source/doc audit only; no build/tests run by Codex.
