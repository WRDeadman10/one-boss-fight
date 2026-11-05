# Result, suite, and evidence-pack tools (Queue C S31–S35)

Offline tooling changes; no engine or runtime behavior changed.

- `framework_results.py` validates required `RESULT outcome`, rejects duplicate fields and malformed nonnegative integer counters, reports multiple results and flags multiple terminal results in a known generation. Generation is carried from proof lines; unavailable context prints `generation=unknown`. F8 restart1 reports two results as generations 1 and 2.
- The test plan's target `suite_log_report.py` was absent. Added it with stable JSON output (`--json`), finished/passed/failed counts, failure and duplicate identities, and raw test line numbers. Nonzero exit means at least one failed test.
- The referenced `diff_suite_logs.py` was also absent. Added it; exit 0 means identical completed-test maps, 1 means additions/removals/result changes, 2 means invalid/missing/no-completion input. Identity uses test path when present, otherwise test name.
- `evidence_pack.py` now preflights all destinations, refuses existing paths (including symlinks/hard-link targets), and requires every destination to resolve as a direct child of the output root before copying anything. Output names are derived from source basenames.

## Validation

- 17 offline Python tests pass across Queue C schema/token/timeline and the new result/suite/diff/path fixtures.
- F8 restart1 RESULT report: generation 1 at line 1869 and generation 2 at line 2276; exit 0.
- `suite_log_report.py` on BUILD-175's retained suite log reports 328 finished, 328 passed, 0 failed; exit 0.
- A temporary evidence-pack run copies an external source log into the selected root and creates a manifest whose copied path stays inside that root.
- Python bytecode compilation passes. No Unreal build, automation-suite run, PIE, commit, or push.
