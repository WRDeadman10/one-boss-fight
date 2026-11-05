# Framework validator token index cross-check (Queue D D52)

## Current offline audit

Ran the two documented read-only scans:

- `python Scripts/Tools/check_validator_tokens.py --root .` — PASS: 138 emitted tokens, 138 schemas, semantic and emission-source indexes complete.
- `python Scripts/Tools/audit_framework_schemas.py --root .` — 138 schemas, 138 emitted tokens, 133 tokens with a retained valid sample; no duplicate schema keys, no missing/duplicate rows in either index, no field drift in statically comparable payloads, and 161 literal format variants validated with zero mismatches. `ERROR` and `overlay` fields are explicitly dynamic/unbounded and skipped by static field comparison.

Five schemas currently lack valid retained samples: `attack_row_refused`, `pending_hit_refused`, `strafe_budget_exhausted`, `strafe_budget_restarted`, and `strafe_stuck`. This is evidence coverage status, not an index/schema defect. S21–S25's older audit says 132/138 and lists six tokens including `fatigue`; that sample census is stale relative to the present retained-log set, where `fatigue` has a valid sample. Treat current per-run audit output as the active inventory and retain S21–S25 as historical evidence.

## Classified deltas and limits

| Delta | Classification | Disposition |
|---|---|---|
| Emitter/schema/index sets and counts | Current clean structural match: 138 each, no duplicates/missing index rows. | No fix indicated by these scans. |
| Five no-sample tokens | UNSAMPLED evidence gap. | Keep labeled absent; do not fabricate a sample or treat as a schema failure. |
| S21–S25 sample total/list | STALE census after subsequent logs; count moved from 132/six to 133/five. | Refresh historical summary only when that report is next maintained; no need to rewrite its recorded test-run history. |
| `audit_framework_schemas.py` numeric `LOOSE` examples | Schema regex accepts `NOT_A_NUMBER` for some numeric-looking fields in the first valid sample. This scan is a permissiveness witness, not proof that every field is numeric or a bug; string/domain semantics vary by token. | Review only against field-specific contracts. D30 already tightened five parry groups; other fields remain outside D52's scope. |
| Dynamic `ERROR` and `overlay` formats | Intentionally unbounded/dynamic paths are excluded from static field-key comparison. | Preserve as a documented limitation; no missing literal field is inferred. |

The scan establishes current mappings and retained sample presence only. It does not establish that a sampled event's gameplay behavior was correct or that each schema captures all semantic/domain invariants. No files were changed by either command; no test suite, build, or Unreal run was performed.
