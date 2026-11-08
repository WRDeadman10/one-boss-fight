# AT-C31–C35: shared package evidence intake

This common return sheet carries package identity and process-smoke evidence. Feature-specific gameplay fields remain in their existing KI intake sheets. A process that starts and survives the short smoke window is not by itself gameplay acceptance.

## Required return, once Lead provides package evidence

| Field | Requirement |
|---|---|
| Build identity | One nonempty Build ID, source commit, target platform, engine version, and configuration (`Development` or `Shipping`) for each package. |
| Stage identity | Absolute stage root, stage stamp, selected executable path and SHA-256; the executable must resolve under the declared stage root. |
| Manifest | Exact manifest path, SHA-256, and successful entry/hash verification. Development and Shipping have separate records, even when built from the same source revision. |
| Smoke process | `PackagedSmoke.ps1` captured stdout, exit code, configuration, exactly one process result, exactly one configuration-specific validation result, and exactly one verdict. Survival duration must be at least one second and the process exit code must agree with the verdict. |
| Runtime evidence | Development: exact unique runtime log path and SHA-256 plus checker result. Shipping: binary-symbol checker result; Shipping does not produce runtime logs. |
| Route provenance | For gameplay acceptance, retain the complete same-run `[EncounterActivation] route=data` witness and the feature-specific raw log/receipt. The smoke-token validator does not establish route, gameplay, or build identity. |
| Failure retention | Keep failed stdout, runtime logs, manifests and identity records in the declared evidence directory; do not overwrite the previous attempt. Record the failed process exit code and failure summary. |

## Maintained-tool audit

- `check_packaged_smoke_receipt.py` validates exact token cardinality, configuration-specific check type, process/check/verdict agreement and wrapper exit code. It now rejects a zero-second survival claim, which the runner itself cannot emit because `PackagedSmoke.ps1` constrains `Seconds` to 1–3600.
- `check_evidence_sha256.py` verifies each listed SHA-256 and now refuses entries that resolve outside the manifest directory, including a correctly hashed `../` target. Read errors fail closed.
- `verify_evidence_manifest.py` already constrains normalized JSON evidence paths to the pack root, verifies payload hashes/sizes, and supports strict membership/source-reference verification.
- Maintained feature receipts (including the AR route receipt and repeat aggregate) separately enforce same-run activation witnesses and feature-specific run identity. Smoke receipt success must never substitute for those checks.

## Acceptance boundary

Codex has not opened staged folders, invoked package/smoke commands, read or modified Lead package artifacts, or claimed runtime acceptance. For each configuration, compare the returned Build ID/stage stamp/manifest and executable hashes before interpreting smoke. Missing identity, hash mismatch, absent same-run route witness, zero/contradictory smoke result, or overwritten failure evidence leaves the relevant gate open.
