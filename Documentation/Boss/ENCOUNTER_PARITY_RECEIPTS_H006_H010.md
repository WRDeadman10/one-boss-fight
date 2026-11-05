# Encounter parity receipts and comparator (Queue H H006–H010)

## Examples

- Legacy control template: `Documentation/Boss/receipts/legacy_driver_v1.example.json`.
- Data-route template: `Documentation/Boss/receipts/data_driver_v1.example.json`.

Both are illustrative fixtures, not run evidence. Replace every example identity, digest, run ID, actor/component identity, marker and observable with values captured from one real run. Never use `EXAMPLE-*` values in a submitted receipt. A pair must use the same map, binary/build identity, content/settings hashes, seed, registered driver, ordered arguments and exact input hash, but distinct run IDs and separate output directories. Data route includes its selection identity in `activation`; its component census may legitimately differ from legacy.

## Capture contract

The registered driver or its run harness must emit a receipt from captured facts; the comparator does not scrape source or logs to invent a receipt. The comparator continues to accept v1. New captures use `onebossfight.encounter-parity/v2`, built by the pure `Scripts/Tools/encounter_parity_receipt.py` module. V2 records the selected asset object path, encounter GUID, role slots, initial phase and canonical manifest SHA-256 (the manifest covers the authored boss/player definition fields); ordered boss/player participant identity, nonzero generation and reset count; and measured observables carrying trial ID plus source-log path and SHA-256. The uint64 participant generation is represented as an exact decimal string when needed, avoiding JSON floating-point precision loss. A separate Unreal package-byte digest for the selection asset is not currently available and is not fabricated. A legacy control may carry the same requested selection identity while separately recording its legacy activation outcome. Placeholder identity, missing participants, malformed hashes, or absent source citations are refused; this builder does not prove that its caller's supplied facts are truthful.

Declare only observables that the driver actually measures. Include a clean terminal result and at least the driver's registered check minimum. Preserve each raw log, command/config JSON, receipt and exact binary/content identity beside the pair. V2 observables stay exact unless the driver explicitly adds `comparison: {"type":"timing_seconds","range_seconds":[min,max]}` and supplies a finite raw numeric `value` in seconds. For that typed case, both arms must be within the shared authored range and differ by at most 1/60 second. This is schema-driven and never inferred from message text; v1 and undeclared observables keep exact comparison.

## Invocation and output

```powershell
python Scripts/Tools/compare_encounter_parity.py CONTROL.json DATA.json
python Scripts/Tools/compare_encounter_parity.py CONTROL.json DATA.json --report-json report.json
python Scripts/Tools/compare_encounter_parity.py CONTROL.json DATA.json --verify-source-logs --report-json report.json
```

Exit codes are stable: `0` PASS, `1` FAIL for a valid pair whose required identity/marker/terminal/observable values differ, `2` INCONCLUSIVE for invalid/missing receipt evidence, unmatched v2 trials, or report-write failure. The optional report uses `onebossfight.encounter-parity-report/v1`, deterministic sorted compact JSON and same-directory atomic replacement. It contains status, exit code, run IDs, source receipt paths and hashes, issue strings, and per-observable citations to both source logs and hashes. `--verify-source-logs` additionally resolves relative log paths from each receipt's directory and verifies the cited SHA-256 against the retained bytes. Inputs are opened read-only and never rewritten. Activation and component differences are reported only as pair context; they are not parity-equality fields.

## Current limit

The 40 registered standard drivers still emit their established text markers; the new runtime snapshot API is not yet wired into a driver or paired-run envelope, and there are no paired data-route runtime runs. Queue J's five-driver capture map and repeat policy are in `Documentation/Boss/J026_J030_PARITY_CAPTURE_POLICY.md`. The data path is opt-in, and G044 still requires authored typed boss/player definitions plus a canonical manifest receipt. Therefore the examples and offline fixture coverage do not establish parity, G044 readiness, packaged readiness, or a production default. Claude owns Editor/PIE and build execution.
