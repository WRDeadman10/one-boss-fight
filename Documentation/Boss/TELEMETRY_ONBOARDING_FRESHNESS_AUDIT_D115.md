# Telemetry onboarding freshness audit — D115

**Scope:** resolve the `parry_stamina` example's linked artifacts, line references, and event format. Static cross-reference only; no validator/test execution.

All linked source, tool, glossary, expected-sheet, and raw-log paths exist. The three cited native emitter lines still emit ordered `before`, `after`, `parried` fields; the two retained log lines still contain `before=100 after=80 parried=0` and `before=80 after=70 parried=1`. The glossary semantic row and emitter-index entry remain present, and the expected sheet still distinguishes a paid whiff from refusal/rollback while preserving the unproven low-stamina branch (`RPGPlayerParry.cpp:86,91,175`; `LOG_TOKENS.md:71,170,374`; `PARRY_STAMINA_EXPECTED.md:17-18`; retained log `:1771,:2155`).

Two guide references were stale: it named the validator under `Scripts/Tools` and cited line 200, but the file is `Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py` and the schema is now at line 202. The guide was corrected. The validator regex at line 202 exactly requires `before=<number> after=<number> parried=0|1`; the referenced checker path and lines 110-132 exist. No behavioral or low-stamina refusal claim is upgraded by these format/path checks.

**Acceptance result:** after the two reference corrections, all sampled paths and line targets resolve and the event literals agree with the schema and retained records. Static only; checker not run.
