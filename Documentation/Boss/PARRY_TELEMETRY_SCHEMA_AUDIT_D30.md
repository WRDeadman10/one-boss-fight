# Parry telemetry schema-to-emitter audit (Queue D30)

Scope: compare the six parry telemetry tokens and adjacent guard token with maintained C++ emitters, validator schemas, unit-test samples, glossary rows, and retained PIE logs. Read-only; no validator/tests/build/Editor run.

## Token map

| Token | Emitter and exact format | Validator schema | Samples / status |
|---|---|---|---|
| `parry_press` | `RPGPlayerParry.cpp:107`: `n=%d t=%.4f opened=%d windowSeconds=%g` | validator line 195: integer `n`, generic non-space `t`/`windowSeconds`, binary `opened` | Literal valid and malformed sample in `test_validate_framework_proof_logs.py:857,894`; retained PIE lines in `B_CODEX_W1/pie_grade/editor_raw.log:1668` and `B_PARRY_STAMINA/pie_stamina_overlay_run1/editor_raw.log:1705`. |
| `parry_reaction` | `RPGFrameworkBossCharacter.cpp:240`: `posture=%g` | line 196: generic non-space value | Unit sample at test line 858; retained sample in `B_CODEX_W1/pie_grade/editor_raw.log:1904`. |
| `parry_grade` | `RPGFrameworkMoveExecutor.cpp:44`: `grade=%s scale=%g` | line 199: enumerated grade, generic non-space scale | Unit sample at test line 859; retained sample in `B_CODEX_W1/pie_grade/editor_raw.log:1900`. |
| `parry_stamina` | `RPGPlayerParry.cpp:86,91,175`: `before=%g after=%g parried=%d` | line 200: generic non-space before/after, binary `parried` | Unit sample at test line 860; retained whiff/parry samples in `B_PARRY_STAMINA/pie_stamina_overlay_run1/editor_raw.log:1771,2155`. |
| `parry_recovery` | `RPGFrameworkBossCharacter.cpp:594`: `grade=%d extra=%g` | line 202: integer grade and decimal/exponent numeric form | Unit sample at test line 862; retained sample exists in `B_PARRY_RECOVERY` PIE logs. |
| `parry_tag` | `RPGPlayerParry.cpp:200`: state `added|removed`, call `ok|failed`, reason string | line 210: exact state/call enums and non-space reason | Unit sample at test line 870; retained add/remove samples in `B_CODEX_W1/pie_grade/editor_raw.log:1667,1706`. |
| `guard_state` (adjacent parry result) | `RPGFrameworkMoveExecutor.cpp:294`: instance, window, guard, enum outcome | line 194: integer instance, non-space window, `None|Guarded|Parried`, typed resolver outcome | Both representative Parried and Accepted unit samples at test lines 855-856; retained parry run sample is documented in TEST_PLAN BUILD-147. |

`Documentation/Boss/LOG_TOKENS.md:69-71,166-171,351-374` lists the token fields, validator links, emitter files, and source inventory. Its glossary and emitter index agree with the reviewed C++ sites for this token set. Unit tests include valid examples for every listed token; retained logs provide real samples for all six parry-specific tokens, and guard/parry result evidence is recorded in BUILD-147/154/152/150 notes in `Documentation/TEST_PLAN.md`.

## Finding: permissive numeric fields

The prior schemas for `parry_press.t`, `parry_press.windowSeconds`, `parry_reaction.posture`, `parry_grade.scale`, and `parry_stamina.before/after` used non-whitespace matching and accepted arbitrary strings despite `%g`/`%.4f` emitters. C-748 ordered this tooling-only hotfix: the validator now uses a shared signed decimal/exponent numeric grammar for those five field groups; tests keep valid signed/exponent examples and reject `oops`, `NaN`, `Infinity`, `inf`, and `-Infinity` on representative fields. `test_validate_framework_proof_logs.py` passed 34/34 tests. No Source tree change; this verifies parser unit/repository tests, not live emitter values or engine behavior.

## Limits

This audit confirms token format alignment and sample presence, not that every runtime branch emits each token or that every historical run log was validated. Retained samples establish observed emissions only in their named evidence runs.
