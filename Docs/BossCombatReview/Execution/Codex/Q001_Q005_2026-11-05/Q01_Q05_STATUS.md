# Queue Q01-Q05 parity evidence refresh

Generated from already closed Lead captures; no Editor/PIE/build was run by Codex.

Q001 uses the preserved BUILD-219 A4 `_r2` run identities and logs. Q002 rebuilds both v2 receipts from those logs. Q003-Q005 rebuild receipts from the current available BUILD-220 live pair. Source paths and SHA-256 digests are in `source_index.json`; generated receipt/report hashes are in `evidence_sha256.txt`.

## Results

- **a4_low_sweep_r2: FAIL** — identity MATCH, final marker MATCH, terminal MATCH, observables UNAVAILABLE_OR_MISMATCH.
  - parity mismatch observable S9 info jump at 0.05 s
  - parity mismatch observable S9 info roll at 0.40 s
- **dormant_wake_b220: PASS** — identity MATCH, final marker MATCH, terminal MATCH, observables MATCH.
- **damage_path_b220: PASS** — identity MATCH, final marker MATCH, terminal MATCH, observables MATCH.
- **player_death_reset_b220: FAIL** — identity MATCH, final marker MATCH, terminal MATCH, observables UNAVAILABLE_OR_MISMATCH.
  - parity mismatch observable check-0004
  - parity mismatch observable check-0011
  - parity mismatch observable check-0017
  - parity mismatch observable check-0023
- **telegraph_b220: FAIL** — identity MATCH, final marker MATCH, terminal MATCH, observables UNAVAILABLE_OR_MISMATCH.
  - parity mismatch observable check-0010
  - parity mismatch observable check-0013
  - parity mismatch observable check-0020
  - parity mismatch observable check-0023
- **boss_hud_b220: FAIL** — identity MATCH, final marker UNAVAILABLE_OR_MISMATCH, terminal UNAVAILABLE_OR_MISMATCH, observables UNAVAILABLE_OR_MISMATCH.
  - candidate run failed checks: 28/29
  - parity mismatch final_marker: control={'kind': 'R', 'passed': 29, 'total': 29}, data={'kind': 'R', 'passed': 28, 'total': 29}
  - parity mismatch terminal: control={'clean': True, 'result': 'Completed'}, data={'clean': False, 'result': 'Failed'}
  - parity mismatch observable check-0009

### Evidence boundary

- The A4 `_r2` capture is BUILD-219 and predates H4; its diagnostic is not present. It reproduces 14/14 scripted checks, but legacy/data S9 jump-0.05 and roll-0.40 observables differ, so comparator remains FAIL.
- BUILD-220 telegraph logs predate H5 and contain no `TIMING_OBSERVABLES_JSON`; the refreshed receipts therefore keep their timing checks exact. Lead must rerun to validate the new typed timing path.
- These BUILD-220 runs predate D2. Claude later reports D2 PASS (selected boss health 2000), and fresh BUILD-220+D2 death-reset, HUD, telegraph and A4 pairs are now running; their results supersede these historical pair findings when finalized.
- All source log hashes were verified by the comparator (`--verify-source-logs`). Existing Lead-owned evidence files were not overwritten.
