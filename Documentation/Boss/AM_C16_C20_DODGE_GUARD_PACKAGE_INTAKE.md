# DATA-default dodge and guard-counter package return

Lead-owned template for packaged controls under C-1104. Fill one row per fresh process and scenario. No true-legacy rerun is required to restore parity wording; route acceptance uses the same-run DATA activation witness. This sheet records evidence; it does not itself close a package gate.

## Package identity (repeat for each package configuration/build)

- Configuration (`Development` or `Shipping`):
- Exact package command, UAT log/hash and exit status:
- Build ID from `BuildStamp.txt`:
- Resolved stage root and stamp path/value:
- Inner executable path/SHA-256:
- UFS manifest path/SHA-256:
- Non-UFS manifest path/SHA-256:
- Cook/required-path check output and hash:
- Packaged smoke command, process exit and completion marker/log hash:

## Per-scenario run records

| Issue/scenario | Run ID | Raw log path/SHA-256 | Same-run `[EncounterActivation] route=data` witness | First input timestamp and press-time movement/input | Action and montage (requested/observed) | Outcome (travel, damage/counter result) | Process completion | Capture path/hash | Failure/omitted fields |
|---|---|---|---|---|---|---|---|---|---|
| KI-196 moving dodge | | | | | `Dodge_Small_Forward_Roll_Montage` | | | | |
| KI-199 first dodge after draw (if included in authorized package smoke) | | | | | `AM_ER_Backstep_Mixamo_V2` | | | | |
| KI-198 guard counter | | | | | `AM_ER_Attack_GuardCounter` | | | | |

## Stop rules

- Require a same-run activation witness that says `route=data`; a launcher argument or probe label is not sufficient.
- Stop on missing/mismatched package identity, missing route witness, incomplete process/log status, or absent required outcome fields. Preserve failed output and do not combine builds.
- Report root-cause fields as unavailable when the probe cannot observe them; package acceptance does not prove KI-199 root cause.
- Keep KI-196 and KI-198 package outcomes separate from KI-199 root-cause status. Do not infer parity or change PIE dispositions from this sheet.
