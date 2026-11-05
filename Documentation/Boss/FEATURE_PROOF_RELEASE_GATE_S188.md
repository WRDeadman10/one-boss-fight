# Feature proof release gate (S188)

Use this gate before enabling or claiming a profile option in a release. A source implementation, passing unit test, or schema-valid log alone is not release evidence. The gate applies to the exact option value, profile, map, build configuration, and supported content combination being shipped.

## Required evidence by layer

| Layer | Required evidence | Does not satisfy the layer |
|---|---|---|
| Decision and scope | Owner-approved intent/value or bounded range; default-off behavior; explicit supported profile/map/content scope; acceptance criteria and a paired control. | A proposed profile field, a default inferred from C++, or an unapproved product choice. |
| Code and authoring | Source path/line for field declaration, resolved value, positive gate, validation/refusal, runtime consumer, reset/terminal behavior, and reflected/asset wiring where applicable. Read back the saved authored profile and the runtime-resolved value in the target build. | Source presence without a caller, an editor script that was not read back, or a hard-coded test value that bypasses the real profile path. |
| Unit and integration tests | Named tests cover enabled positive behavior, default/disabled behavior, invalid/boundary values, and relevant reset/failure paths. Run and retain the test log, build identity, count, and exit status. Add integration coverage where the option crosses components, reflected APIs, or asset data. | A test file that was not built/run; a pure rule test presented as proof of the UE/Blueprint/asset wiring; zero or partial completions. |
| Live behavior | Lead-run PIE or equivalent live encounter on the actual map and saved profile. Retain exact command/setup, profile readback, build ID/configuration, raw log and state snapshots. Show the enabled option causes the declared result and a matched default-off/control setup does not. Use measured tokens or clearly labeled manual observation for claims that telemetry cannot establish. | Code review, a passing suite, schema registration, a synthetic log, an enabled run without a control, or a log whose map/profile/build identity is unknown. |
| Packaged release | If the option is claimed in a packaged build, repeat the behavior check against the exact package/configuration and retain executable/package hashes, content-check result, startup/liveness, and feature observation. Keep the package's profile/config readback. | PIE results presented as packaged proof, a successful cook/build alone, or a binary string scan presented as behavior proof. |
| Review and status | Claude reviews the source/build/live evidence and records disposition. Update the row-level witness ledger/status and release notes using its current rules; retain `WITNESSED` only for the precise claim actually supported. Keep partial/manual limits explicit. | A task marked complete by Codex, accepted code, or a schema-valid token being treated as automatic approval or live witness. |

## Pass/fail checklist

- [ ] The owner-approved option and shipped value are explicit; scope and default-off/control behavior are named.
- [ ] Saved and runtime-resolved profile values match the intended configuration; validation rejects malformed/unsupported values with the documented refusal.
- [ ] Source review follows the option from authoring/reflection through the actual runtime consumer and checks reset, terminal, and failure paths.
- [ ] Build identity matches the reviewed source snapshot; the named unit/integration tests ran against that build with complete results.
- [ ] A controlled live enabled run and a matched disabled/default control are retained; observations meet predeclared criteria.
- [ ] The validator accepts the raw log's syntax/semantics, but the reviewer separately verifies that each log row proves the stated behavior and setup.
- [ ] For a packaged claim, the exact package is identified and the feature was observed in that package; hashes and content/liveness checks are retained.
- [ ] Claude's review and the witness-ledger disposition are recorded, with all untested branches and manual evidence labeled.

Any unchecked item blocks a claim that the option is release-proven. The implementation may remain in source behind a default-off gate, but it must be described as coded/unverified or partially proven. Schema coverage checks event shape/registration; it does not prove event occurrence or game behavior. Unit tests prove only the exercised test boundary. A passing build proves compilation, not runtime behavior.

## Evidence references

- `Documentation/Boss/PROFILE_OPT_IN_AUDIT_R156_160.md` — source-level gate, validation, reset, telemetry, and documentation inventory; explicitly not live proof.
- `Documentation/Boss/EXPECTED_SHEET_AUTHOR_GUIDE_S152.md` — measured, inferred, and manual criterion conventions.
- `Documentation/Boss/EVIDENCE_HASH_REFRESH_CHECKLIST_S187.md` — source/build/run identity and hash freshness when preparing the review bundle.
- `Docs/BossCombatReview/Execution/Antigravity/Ledger/witness_status_v3.json` and its companion census/upgrade plans — row-level witness state and proof authority; never infer a status from code or schema presence.
- `Documentation/GATE4_RUNBOOK.md` — packaged build, content, smoke, and Shipping checks.
