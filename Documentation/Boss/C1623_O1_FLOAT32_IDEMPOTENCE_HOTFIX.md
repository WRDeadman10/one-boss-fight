# C-1623 O1 float32 and rerun hotfix

## Change

- Added a finite absolute `1e-4` comparator for O1 numeric fields read back through Unreal's reflected float properties. Both the Phase_1 author and framework encounter author use it for O1 float checks; discrete names and identifiers continue to use exact equality.
- Made the Phase_1 write stage idempotent. If all approved Stats and Phase_1 values already match within tolerance, it emits `RESULT ALREADY_CURRENT` and returns without saving. Missing or differing values still follow the existing explicit-write path.
- Extended the O1 source contract with float32 (`0.6000000238418579` vs `0.6`), in/out-of-tolerance, non-finite, and malformed input cases.

## Verification

- `python Scripts/Tools/test_sevarog_o1_source_contract.py`: 5/5.
- `python -m py_compile` on both authoring scripts, the source loader, and the contract: pass.
- Scoped `git diff --check`: pass.
- No Editor, build, PIE, asset, or map operation was performed. Claude owns the engine lock and will rerun the O1 runner after this source hotfix.

## Handoff

Claude should rerun the five-stage C-1619 runner. The phase write stage is safe to rerun when the already-authored draft values match. Encounter write/readback remains gated on its dry stage passing.
