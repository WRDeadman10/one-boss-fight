# Report B7 — Gate 4 Runbook Corrections

## Scope

Updated only `Documentation/GATE4_RUNBOOK.md`, as claimed. No editor, build,
package, game, or PIE session was started.

## Delivered

- `GATE4_RUNBOOK.md:9`, `:27`, and `:130-137` now require `fight_started`
  to be true for every retained fight-mode run, in addition to the valid GPU
  check.
- `GATE4_RUNBOOK.md:35` and `:130-133` distinguish Development's staged
  output root from Shipping's `%LOCALAPPDATA%` root; both current benchmark
  scripts search both roots.
- `GATE4_RUNBOOK.md:37`, `:41`, and `:138-144` set the result order:
  GPU/fight validity first, average FPS and overall p99 against the gate,
  then the largest of game/render/GPU p99 as the diagnostic bottleneck.
- `GATE4_RUNBOOK.md:106-118` records the requested stage names and replaces
  the obsolete Shipping uncertainty with: **verified to run by Claude
  2026-10-24 (invalid GPU under RDP)**.

## Finding

`Scripts/RunBenchmark.ps1:6-8` still describes only the staged output path,
while its actual search list at `:43-50` includes both staged and
`%LOCALAPPDATA%` roots. This is a script-header documentation drift only; it
is outside the B7 claimed files and was not changed.

## Validation

Ran `python -I Scripts/CheckDocs.py`; output: `No documentation integrity
findings.` No runtime behaviour was exercised.
