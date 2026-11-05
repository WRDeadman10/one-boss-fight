# Validator drift and timeline audit (Queue C S26–S30)

Offline review of FrameworkProof source emissions, registered schemas, the two `LOG_TOKENS.md` indexes, validator mutation tests, and timeline grouping. No schema or runtime behavior was changed.

## S26: literal field drift

`python Scripts/Tools/audit_framework_schemas.py` maps emitted formats to schema keys and reports field differences with source locations. Current candidates:

| Token | Source evidence | Schema | Finding |
|---|---|---|---|
| `combo_end` | `RPGFrameworkBossCharacter.cpp:813` emits `reason=NextCardRefused detail=%s`; other sites emit `reason` only. | `validate_framework_proof_logs.py:181` accepts only `reason=...`. | `detail` is emitted but rejected by the schema. Preserve both forms or define a shared accepted form. |
| `phase_anim` | `RPGFrameworkBossCharacter.cpp:707` emits `state=Aborted reason=StanceBreak phase=...`; other sites emit triggered/finished forms. | `validate_framework_proof_logs.py:174` accepts only `Triggered` with sequence fields or `Finished phase=...`. | The interrupted transition form is emitted but not accepted; its `reason` also has no schema branch. |

`ERROR` carries an intentionally open free-form detail and `overlay` uses a dynamic formatter, so static literal-key comparison skips them. The scan found no other literal drift candidates. These schema files already contain work by Lead; findings are reported for review, not patched here.

## S27–S28: index parity

The audit compares schema token names with the semantic and emission-source tables in `Documentation/Boss/LOG_TOKENS.md`. Current indexes have no duplicate or missing schema tokens; all 138 emitted tokens map to a schema and both indexes. Exit status is now nonzero on a duplicate or missing index row. Source locations remain printed per token.

## S29: validator mutation-test limits

The test named `test_99_token_mutation_suite` is stale: its docstring still says 99/99, while the fixture asserts 112 real samples at `test_validate_framework_proof_logs.py:218` and mutates one key per sample at lines 223–237. This does not prove every required field can be removed for every schema. A dedicated missing-field rejection is explicit for `warp_step` at lines 758–774; other malformed-value cases are selective. Full per-schema missing-field coverage remains a documented gap.

## S30: timeline grouping

`plot_framework_timeline.py` carries encounter and generation context forward and adds the active instance when present. `test_plot_framework_timeline.py` verifies stable groups across ordinary event lines and a generation reset while retaining original log line numbers (including a non-event line). Its fixture passes.

## Validation

- `python Scripts/Tools/audit_framework_schemas.py`: 138 schemas / 138 emitted tokens; no schema duplicates; both indexes have no duplicates or missing tokens; 132 retained valid samples, six schemas lack a retained sample; two telemetry drift candidates above.
- Python offline tests for the schema audit, comment-aware token scan, and timeline grouping pass.
- `python Scripts/Tools/check_doc_links.py .`: 0 broken links.
- No Unreal editor, build, or project automation suite run.
