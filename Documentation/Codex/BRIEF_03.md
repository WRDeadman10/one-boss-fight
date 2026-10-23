# Codex Brief 03: documentation integrity checker and a staleness audit

From Claude via the owner. Files only; you do NOT run the editor, a build, a package or the game. Claude validates your report by evidence and writes Brief 04.

## Validation of Report 02 (so you know where you stand)
Accepted. Evidence: only the three named files changed; the checker parses and runs clean on the archived logs; I also ran it against synthetic logs with planted failures and it caught the missing `/Game` asset, the cook and shader errors, `LogRPG*` warnings, the debug strings and a fatal line, and returned FAIL. Your honesty about patterns unverified on real failures was right: they stay unverified until a real Gate 4 log exists. Not done and carried over (optional here): the per-encounter watchdog message in `Scripts/Editor/pie_soak.py` (section 2.3).
Context: the soak driver has not run yet (Claude's editor is busy with the regression gate).

## 1. Context
Read `AGENTS.md`, `Documentation/PROJECT_STATE.md`, `Documentation/TASKS.md`, `Documentation/TEST_PLAN.md`, `Documentation/KNOWN_ISSUES.md`, `Documentation/DECISIONS.md`, `Scripts/RunDrivers.ps1` (the table of drivers: name `N`, kind, minimum checks `Min`, balance rows `$balance`), and the list `Scripts/Editor/pie_*.py`. These docs are patched by hand after every piece of work, so they drift. Your job is to find the drift with evidence; Claude fixes it.

## 2. Deliverables (new files only; no existing file edited, except 2.3 if you do it)
1. `Scripts/CheckDocs.py` (Python 3.10, standard library only, read-only on the project, run as `python -I Scripts/CheckDocs.py`): prints a list of findings and exits 0 when there are none, 1 otherwise. Checks:
   a. every driver row of `RunDrivers.ps1` (gate and balance rows) has a script file in `Scripts/Editor` (balance rows use their `S` script), and every `Scripts/Editor/pie_*.py` that is neither in the table nor named in `TEST_PLAN.md` is listed as "not in the gate and not documented";
   b. every driver of the gate table is named in `TEST_PLAN.md`, and where the row text contains `PASS n/m` the number `m` is compared with the driver's `Min` (report mismatches, not equal-or-greater: say which is lower);
   c. every KI-xxx id used in any doc exists as a row in `KNOWN_ISSUES.md`; ids are unique; a row whose last cell says Open while another doc says "fixed" or "closed" for that id is listed (heuristic, label it as such);
   d. every `Documentation/*.md` or `Scripts/*` path mentioned in backticks in `PROJECT_STATE.md`, `TASKS.md`, `TEST_PLAN.md`, `DECISIONS.md`, `KNOWN_ISSUES.md` exists;
   e. `CLAUDE.md`, `AGENTS.md` and `Documentation/PERFORMANCE_LOG.md` agree on the FPS target (60 FPS average, p99 <= 16.67 ms; 120 only as stretch).
2. `Documentation/Codex/REPORT_03.md`: run the script and paste its output; then a hand-checked list of the ten most important contradictions or stale statements across `PROJECT_STATE.md`, `TASKS.md`, `TEST_PLAN.md`, `KNOWN_ISSUES.md`, `DECISIONS.md` (for each: the two places with file:line quotes, which one you think is right and why, what evidence would settle it). Do not fix anything. Mark what you could not verify.
3. (Optional) the soak watchdog follow-up from Report 02 / mailbox C-3: in `Scripts/Editor/pie_soak.py` and `Documentation/SOAK_NOTES.md` only, a per-encounter watchdog message that names the last step reached. Say in the report whether you did it.

## 3. Rules
Same as before: no commit or push, no git command that changes the working tree (about 240 uncommitted changes must survive), no editor, build, package or game run. The script must not write anything. Never claim a check ran that did not. Running `python -I Scripts/CheckDocs.py` and reading files is allowed and expected.

## 4. Acceptance criteria (Claude checks)
1. Only the named new files changed (plus the two soak files if 2.3 was done).
2. The script runs with `python -I`, exits with the right code, and every finding line says which file and line or driver it concerns. Claude plants a known mismatch in a scratch copy of a doc to see that it is caught.
3. Each of the ten hand-checked contradictions has two real quotes with file:line that Claude can open.
4. The report lists what could not be verified.

## 5. Report
`Documentation/Codex/REPORT_03.md` as in 2.2. Tell the owner "Report 03 is ready".
