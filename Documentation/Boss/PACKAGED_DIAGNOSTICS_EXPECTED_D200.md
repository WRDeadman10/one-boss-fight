# Opt-in packaged diagnostics panel expected sheet (Queue D200)

Status: protocol only; no panel, field set, or default change is implemented. Review the approved fields, default-hidden behavior and exact Shipping visibility policy before implementation. Live packaged build and binary inspection are Lead-owned.

## Claim and privacy boundary

The proposed packaged diagnostics panel is hidden by default and exposes only a reviewed, explicitly approved field list when enabled. It must not change gameplay. It must not expose secrets, credentials, player identity, host/user/session identity, raw environment values, unreviewed absolute paths, or private raw logs. Any displayed diagnostics remain local; no panel output is published/transmitted by this protocol. No Shipping inclusion/exclusion decision is made here.

## Run identity and setup

| Field | Expected / observed |
|---|---|
| Build/package identity | **Expected:** exact Shipping package hash, build config, map, version and binary inspection record. **Observed:** UNKNOWN until Lead packages/reviews it. |
| Run ID, UTC, screenshots/logs and hashes | **Expected:** unique local capture, immutable evidence and post-capture hash. **Observed:** pending. |
| Approved field schema | **Expected:** every displayed field, source, type, units, privacy classification, redaction and authorization reference. **Observed:** UNKNOWN pending review. |
| Feature state | **Expected:** panel read back hidden by default; enabled only for the reviewed diagnostic run. **Observed:** pending. |
| Runtime identity | **Expected:** non-personal build/map/profile/generation/attack identity only where explicitly approved. **Observed:** pending. |

## Paired cases

Compare the exact same packaged Shipping binary/configuration with panel hidden and enabled, changing only the approved panel toggle. Keep raw evidence local.

| Row | Required evidence | Pass condition |
|---|---|---|
| Hidden packaged control | Launch exact Shipping package with panel off/read-back; capture screen, build hash and gameplay baseline. | Panel is not visible by default; gameplay and default presentation remain unchanged. |
| Enabled approved fields | Enable only the reviewed fields; capture panel and independently read source values. | Every shown field matches its source and approved schema; no unapproved or sensitive fields appear; gameplay is unchanged. |
| Shipping visibility review | Inspect the exact Shipping binary/package/config for panel code, strings, flags and enabled-field paths; record hash and method. | State only what the inspected artifact proves. Do not infer exposure/absence from Development builds, source guards, or config defaults alone. |
| Privacy scan | Scan visible output and local diagnostics for secrets/personal/host/session/path data without copying sensitive values into report. | No prohibited data is exposed. Raw logs/screens remain local; any later shared review copy requires separate authorization and scrubbing. |
| Disabled regression | Turn panel off and repeat baseline. | Panel remains hidden and behavior matches initial control. |

## Evidence interpretation and limits

- **Measured:** exact package hash/config, panel toggle, approved field values and screen capture with local evidence references.
- **Inferred:** panel correctness only when each displayed value is independently compared to the same build/run source.
- **Manual:** legibility and usefulness; panel must not obscure combat.
- A Development screenshot or source-level `#if` does not establish Shipping visibility. Binary inspection applies only to the exact recorded package hash/config. A bounded privacy scan is not proof that every possible secret pattern is absent.

## Failure and stop conditions

Do not implement or claim Shipping visibility until the owner/Lead approves the field schema and exact package review. Fail if default-visible, any unauthorized field appears, values are wrong, gameplay changes, or secrets/personal data are exposed. Stop if package hash, binary evidence, field provenance or redaction policy is missing; quarantine sensitive findings locally and report only category/path without value. Missing evidence is UNKNOWN/inconclusive.

## Verification boundary

Expected protocol only. No panel/source/config changes, tests/build/Editor/package execution, or Shipping visibility claim. Implementation and Shipping review require owner/Lead approval.
