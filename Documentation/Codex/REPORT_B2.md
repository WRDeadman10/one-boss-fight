# B2 - PIE driver retry hardening

## Change

- `Scripts/Editor/pie_builds.py`: split the one-swing action into `measure_once` and a wrapper that retries only a zero-intake-record action once. It logs `INFO retry: <action> produced zero intake records...`; a second zero remains a visible failure.
- `Scripts/Editor/pie_fog_gate.py`: each state-changing action (wake, fade refresh, reset, second wake, kill) now has one explicit retry. A retry logs `INFO retry <key>:` and repeats only its corresponding action. A second bad observation still records the original failed check.

## Evidence

- The reported build slip is present in `Saved/Logs/OneBossFight-backup-2026.10.24-06.19.40.log:6622`: `[Builds] FAIL Dex Light: the hit landed (0 intake record(s))`.
- The same run cascades into posture, bleed, and record failures at `...log:6624-6626`; retrying the missed action before checks prevents those derivative false negatives without hiding a repeat failure.
- Existing fog-gate logs show clean summaries at `Saved/Logs/OneBossFight.log:2396` and `:18158`. I did not find the historical timeout line, so the retry design is limited to the fixed-delay state transitions visible in `Scripts/Editor/pie_fog_gate.py:56-95`.

## Static validation

Ran:

```text
python -I -c "import ast ..."
Python AST: OK
```

No editor, build, PIE, package, or game was run. Claude should run each driver repeatedly (the requested 10 runs) to validate that the retries solve flakes without concealing a real failure.
