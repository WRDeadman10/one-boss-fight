# Opt-in proof telemetry verbosity expected sheet (Queue D191)

Status: protocol only. No verbosity option or log change is implemented/enabled. Review default logging, enabled field schema and privacy filters before implementation. Diagnostic output stays local to the project/repository; it is not published or transmitted.

## Claim and privacy boundary

The proposed opt-in verbosity adds reviewed diagnostic fields while leaving default log content unchanged. Enabled diagnostics may include non-personal run/build/map/profile/attack/generation identity necessary to correlate evidence. They must not include secrets, credentials, player identity, host/user/session identity, raw environment values, or unreviewed absolute paths. Raw diagnostic logs remain local; any external review copy must be separately scrubbed, with the original retained unchanged locally.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Run ID, UTC, raw log path and hash | **Expected:** unique run ID and immutable local log with post-capture hash. **Observed:** pending. |
| Build/map/profile | **Expected:** build identifier, map, profile and generation values reviewed as non-personal. **Observed:** pending. |
| Default log baseline | **Expected:** same scenario/output captured with verbosity off for byte/field-level comparison. **Observed:** pending. |
| Verbose schema | **Expected:** enumerated fields, producer, type, redaction rule and retention for each field. **Observed:** UNKNOWN pending review. |
| Secret/privacy scan | **Expected:** scan output and exact patterns/scope recorded without copying secret material into evidence. **Observed:** pending. |

## Paired cases

Replay the same scenario with verbosity disabled/enabled, changing only the reviewed diagnostic option. Keep raw data local.

| Row | Required evidence | Pass condition |
|---|---|---|
| Default log | Capture stable default tokens/fields and gameplay result with verbosity off. | Default log schema/content remains unchanged by the new option. |
| Enabled diagnostics | Capture added fields and source identity for run/build/map/profile/attack/generation as approved. | Required identity is sufficient to correlate the run; no unreviewed personal/host/session data, secrets or credentials appear. |
| Secret handling | Scan enabled output for known credential/token patterns and inspect environment/path fields under approved scope. | No secrets are logged; raw output remains local-only. Avoid storing matched secret contents in the report. |
| Gameplay guard | Compare combat inputs, state, timing and outcomes off/on. | Logging verbosity has no gameplay or scheduling effect. |
| Redacted-copy check | If sharing is explicitly authorized later, inspect a separate copy and compare original hashes. | Only scrubbed copy is shared; original remains local and unchanged. This sheet itself does not authorize sharing. |

## Evidence interpretation and limits

- **Measured:** exact default/verbose schemas, approved identity fields, raw log hash and scan result summary; references must avoid exposing sensitive values.
- **Inferred:** unchanged default only from matched scenario and comparable output; extra line volume alone is not proof that default behavior stayed unchanged.
- **Manual:** whether diagnostics are useful and understandable to reviewers.
- A pattern scan cannot prove absence of every secret. State its scope and patterns; do not claim an exhaustive security guarantee. Never place a discovered secret into this sheet.

## Failure and stop conditions

Fail if default output changes, diagnostics contain secrets or prohibited identity, option affects gameplay, or raw logs are published/transmitted. Stop if field schema/redaction/retention is undefined or findings include sensitive material; quarantine locally and report only the category/path without the value. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No telemetry/source changes, tests/build/Editor execution, or runtime claim. Implementation is not authorized before review.
