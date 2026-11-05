# Proof report paired-control boundary audit (Queue D D56)

## Checklist semantics

`proof_report.py:18-48` parses registered token names from backtick checklist spans and from literal `[FrameworkProof] TOKEN` text. A token is considered negative when the word `no` appears within the short preceding text window before that token; the rule is lexical, not a formal expected-sheet grammar. For each checklist line, positive tokens must be present in the primary `log`. Negative tokens are checked against `--control-log` when provided; without it, the same primary log is used (legacy single-log behavior). Thus a line such as `no combo_start control token` checks absence in control only with the option supplied; otherwise it requires absence in the main log. Absence means zero count in the validator's token counts, not absence of all related gameplay behavior.

`test_queue_c_tools.py:67-105` covers single-log positive/negative behavior, a paired-control leak failure, and input-log hash reporting. A valid negative-control log with no token passes; adding the forbidden token fails. The positive token remains checked on the primary log even when a control is present. The parser only verifies registered tokens; unregistered text becomes manual.

## Exit status precedence

After printing all evidence rows, syntax counts, and optional identity/freshness findings, the final status order is:

1. Completeness issues -> exit 2 (`INCOMPLETE RUN`), before feature checklist failures.
2. Missing positive or present forbidden token -> exit 1 (`FAIL`).
3. Input identity mismatch -> exit 1.
4. Stale/invalid manifest evidence -> exit 3.
5. Manual-only checklist rows, schema syntax failures, or semantic warnings -> exit 2 (`INCOMPLETE`).
6. Otherwise exit 0 (`PASS`, presence-only semantics).

Consequences: if gameplay rows fail and input identity also mismatches, exit 1 represents the gameplay failure while the identity detail is still printed. Stale evidence does not override an already-failed checklist/identity. Conversely a stale manifest takes precedence over parser syntax/semantic warnings after the report prints them; callers must read the diagnostics, not only the numeric code.

## Boundaries

A forbidden token in a paired control is meaningful only if the paired log is the intended matched control; this tool does not prove experimental equivalence. The `--manifest` freshness call verifies all entries in the supplied manifest and requires an entry for the primary log by basename, but it does not separately require a manifest entry for the control log. No-control legacy mode intentionally checks negatives against the positive run. PASS means telemetry presence only, not numeric relation, gameplay correctness, or control comparability. Source and fixture review only; tests were not run.
