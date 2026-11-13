# BK-41–45 — PIE driver safety

## Implemented source work

- `Scripts/Editor/pie_driver_support.py` adds a one-shot terminal `RESULT=PASS|FAIL` formatter and a bounded Enhanced Input readiness poll. Readiness callback exceptions, invalid deltas, timeout, and repeat polls return explicit terminal statuses.
- `Scripts/Editor/pie_er_air_reach.py` and `pie_er_air_hits.py` now wait up to five seconds for the `RPGDodgeTiming` input context before any injected key event. A refused press/release terminates through the single final result line instead of raising on a pre-mapping release. Both preserve the C-1283 warm-up order: 12-second settle, Right Trigger 0.5–1.2 seconds, then 3.7 seconds before trials.
- `Scripts/Editor/pie_er_inputs.py` now gates its first warm-up R2 key event on the same bounded mapping-readiness poll, tracks held inputs for terminal cleanup, and emits one final result after its checks.
- Follow-up safety pass: `Scripts/Editor/pie_er_block_probe.py` now waits for the mapping before its first combat-toggle press, fails explicitly on refused press/release, and emits one guarded terminal result.
- Follow-up safety pass: `Scripts/Editor/pie_er_control_latency.py` gates its retrying R2 draw warm-up and latency samples on the same readiness gate, refuses pre-mapping key failures without raising, and emits one terminal result.
- Follow-up safety pass: `Scripts/Editor/pie_er_a4_guard_counter.py` now waits for its actual dodge mapping before the first R2 event, treats refused key events as failed witness paths, and emits a single terminal RESULT distinct from its counter-detail row.
- Follow-up safety pass: `Scripts/Editor/pie_full_fight.py` waits for `RPGDodgeTiming` mapping readiness before its initial draw press, records any refused later input as a terminal driver failure, and emits one final RESULT based on the boss terminal outcome.
- Follow-up safety pass: `Scripts/Editor/pie_player_tags.py` gates the diagnostic dodge press, handles refused press/release as terminal failures, and emits a one-shot result with explicit input outcomes.
- Follow-up safety pass: `Scripts/Editor/pie_jump_probe.py` waits for the player's mapped input context before pressing its configured jump key, handles refused transitions as failures, and emits a terminal RESULT.
- Follow-up safety pass: `Scripts/Editor/pie_remains.py` waits for mapped input before retry, checks press/release results, cleans up a held R key on terminal paths, and emits one terminal RESULT.
- `Scripts/Tools/scan_pie_driver_safety.py` inventories `pie_*.py` scripts that register a PIE tick or request PIE, reporting absent final-result markers and direct key-up calls without recognizable mapping-readiness markers. Default mode is informational; `--strict` makes findings fail the command.
- Focused offline tests: `test_pie_driver_support.py` (13 cases) and `test_scan_pie_driver_safety.py` (3 cases). Both passed; changed Python files compile.

## Limits / remaining work

The current scan found 139 runtime-driver candidates and 136 source-marker findings: 129 have no recognized standard final-result marker and 7 contain a direct key-up call without a recognized readiness marker. These are heuristic source findings, not proof that each script fails at runtime; BK-44's scanner reports them for targeted follow-up instead of rewriting historical probes indiscriminately. Ten input/reach drivers (nine ER probes plus the remains probe) now use the shared helpers; this batch does not claim the entire historical driver inventory has been migrated.

No Unreal Editor, build, or PIE run was performed because Claude's C-1293 X26 live matrix still owns the engine and no release was present in the mailbox. This is source/tooling completion only; no live driver behavior is claimed.
