# Queue P36–P40 D3 measurement status (superseded by S16, C-879)

P40 offline consistency pass complete; P36–P39 measurements are not claimed. Claude later closed D3 at 5/10 measured and 5/10 withdrawn/inconclusive (C-879). The source video did not establish attack identity and milestone boundaries for P2–P5/P7; this is the final disposition for this footage, not an open request to infer more timings.

## Current ledger and tool results

- `D3_MEASURED_LEDGER.json`: 10 entries; 5 measured (priorities 1, 6, 8, 9, 10) and 5 withdrawn/inconclusive (2, 3, 4, 5, 7). C-881 follow-through restored the 12 P1/P6 PNGs; all 30 canonical frame PNGs are now present, with hashes and extraction metadata. P2–P5/P7 remain unmeasured by Lead disposition.
- `python -I .../Reviews/test_fill_ledger.py`: 14/14 pass after correcting the stale real-ledger fixture, which expected four measured entries despite the accepted priority-1 entry making the current count five.
- `D3_findings_table.py` ran read-only against the current ledger and produced five table rows. No ledger measurements or evidence images were synthesized by this run.
- The earlier 30-missing count predates the S12–S14 restoration and is stale. S16's current path check finds 12 missing P1/P6 frame files; existing contact/detail sheets do not satisfy those per-milestone references.

## Remaining work

No further measurements are authorized from this footage. Re-open only if a new, suitable source clip is supplied. The P1/P6 evidence gaps remain accurately recorded; no gameplay values should be copied from this design-reference study into runtime content.

