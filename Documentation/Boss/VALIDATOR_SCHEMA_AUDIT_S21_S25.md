# FrameworkProof validator/schema audit (Queue C S21–S25)

Offline audit of token extraction, schema/documentation mapping, retained-log sample coverage, and regex shape permissiveness.

## S21: checker edge cases

`Scripts/Tools/check_validator_tokens.py` uses a DOTALL UE_LOG/TEXT pattern and returns a set, so multi-line `TEXT` invocations are found and repeated tokens collapse to one inventory entry. The scan previously read comments as code; added `strip_cpp_comments`, preserving quoted strings, escapes, and newlines while blanking `//` and `/*...*/` comments. Added synthetic fixtures for multi-line calls, repeated tokens, a token nested alongside `FString(TEXT(...))`, comments, and comment-like characters inside strings.

## S22: source/schema/index map

Added `Scripts/Tools/audit_framework_schemas.py`. It reports each emitted token's C++ source locations, validator schema line, presence in the semantic index, presence in the emission-source index, and first valid retained log sample. Current report: 138 emitted tokens map to 138 schemas; each is present in both documentation indexes. This is a structural mapping, not proof that a token's behavior was exercised in a particular feature lane.

## S23: duplicate schema detection

The audit parses the `SCHEMAS` dictionary AST so Python's dictionary overwrite behavior cannot hide repeated literal keys. It labels same-pattern duplicates separately from conflicting patterns and reports both source lines. Current validator source has no duplicate keys. Added fixtures for both duplicate kinds.

## S24: retained sample coverage

The audit scans retained `Docs/**/*.log` lines and records only tokens that pass the current validator. 132 of 138 schemas have a valid retained sample. No valid sample was found for `attack_row_refused`, `fatigue`, `pending_hit_refused`, `strafe_budget_exhausted`, `strafe_budget_restarted`, or `strafe_stuck`. Lack of sample is an evidence gap, not a schema defect; the validator may be ready before a feature has a live witness.

## S25: regex permissiveness examples

For each token with a valid retained sample, the audit replaces one numeric-looking field with `NOT_A_NUMBER` and checks whether the payload regex still accepts it. This tests shape permissiveness only; it does not claim those values are accepted by runtime logic. The current `[^\s]+` patterns allow examples including:

- `boss_health max=NOT_A_NUMBER playerHitDamage=100 label=F5_fixture`
- `decision attack=1 chosen=Move_Sevarog_HeavySlam_F7 score=NOT_A_NUMBER range=129.533 phase=Phase_1`
- `walk start=X=500.000 Y=NOT_A_NUMBER Z=167.150 ...`

This is consistent with the validator's current role as a field/payload-shape checker for many numeric fields; semantic checks are selective. If numeric-domain guarantees are required, add explicit numeric/finite semantic validation and mutation fixtures for the selected fields. No schema regex or runtime rule was changed in this task.

## Validation

- `python Scripts/Tools/test_check_validator_tokens.py`: 4 tests passed.
- `python Scripts/Tools/test_audit_framework_schemas.py`: 4 tests passed.
- `python Scripts/Tools/check_validator_tokens.py --root .`: PASS, 138 emitted tokens / schemas / complete indexes.
- `python Scripts/Tools/audit_framework_schemas.py --root .`: no duplicate keys; 132 valid samples; six tokens above have no valid retained sample.

These are small Python tooling checks only; no Unreal build, automation suite, or editor/PIE run was performed.
