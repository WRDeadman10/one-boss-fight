# KI-192 packaged R2 boundary intake

Lead-owned Shipping-package intake; fill one run row per fresh packaged process. This template does not require a repetition count; Lead records the selected count and environment. Do not pad, merge, or re-label runs to match the PIE-only five-per-route aggregate wrapper. Keep `0.34`, `0.35`, `0.36`, and `0.70` seconds as the existing hold cases. No threshold, input mapping, or latency claim changes.

## Package identity (one section per configuration)

### Shipping

- Exact package command, full UAT log/hash, exit status:
- Build ID from this stage's `OneBossFight/Saved/BuildStamp.txt`:
- Configuration: `Shipping`
- Resolved stage root:
- Inner executable path/SHA-256:
- `Manifest_UFSFiles_Win64.txt` path/SHA-256:
- `Manifest_NonUFSFiles_Win64.txt` path/SHA-256:
- Cook receipt/check output and hash (if supplied):
- Packaged smoke command, process status, completion marker/log hash:
- Repetition count selected by Lead and environment/tick metadata:

## Per-run receipt (repeat for every fresh process)

| Trial ID | Run log path/SHA-256 | Same-run `[EncounterActivation] route=...` witness | Route | Requested holds | Per hold: selected action/montage, montage position, observed game tick, tick duration | Completion marker/process result | Capture path/hash | Failure/omission |
|---|---|---|---|---|---|---|---|---|
| | | | | 0.34 / 0.35 / 0.36 / 0.70 s | | | | |

## Stop and interpretation rules

- Stop if Build ID, configuration, stage root, stamp, executable, manifests, or smoke output are absent or inconsistent. Do not mix runs from different package identities.
- For each run, accept route only from a same-run activation witness and cross-check any probe route label. A filtered excerpt without its matching full-log witness is insufficient.
- Stop/mark incomplete if any required hold sample or canonical completion marker is absent, malformed, or duplicated. Retain failed output; do not silently substitute a run.
- Keep every per-hold outcome; any summary is descriptive and game-tick-bounded, not physical controller latency or causal proof.
- PIE closure remains separate from package evidence. Package validation does not alter the authored timing threshold.
