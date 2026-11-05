# Framework proof evidence retention guide (S155)

Use the task-specific parent directory under `Docs/BossCombatReview/Execution/Claude/` as the evidence bundle. Keep the run command, wrapper result, raw editor log, relevant pre/post state, and hash manifest together. A raw log alone cannot establish which command or profile produced it; a manifest alone proves file identity, not the gameplay claim. For handovers, use [EVIDENCE_HASH_REFRESH_CHECKLIST_S187.md](EVIDENCE_HASH_REFRESH_CHECKLIST_S187.md) to distinguish same-source/new-build from unchanged evidence.

**Local-only privacy rule:** keep evidence bundles in the repository's local execution tree; do not publish raw logs or `system_info.txt`. Before sharing any excerpt or report outside the repository, scrub host, user, and session identifiers and review absolute paths and raw input lines for sensitive content. Never alter the retained original evidence to redact it; create a separately labeled redacted copy if external sharing is explicitly required.

## Four useful artifact types already retained

1. **Bounded positive measured result:** `Docs/BossCombatReview/Execution/Claude/B_PARRY_STAMINA/pie_stamina_overlay_run1/` has `command.json`, `result.json`, and `editor_raw.log`. The log records a paid whiff (`before=100 after=80 parried=0`) at line 1771 and a Perfect parry net delta (`before=80 after=70 parried=1`) at line 2155. This supports those two branches; the expected sheet explicitly leaves insufficient-stamina refusal unproven.
2. **Paired negative control:** `Docs/BossCombatReview/Execution/Claude/B_AGGRO/pie_control/` retains its own command, result, and raw log. It uses the same task lane and scheduled dodge inputs but has no `aggro_switch` token; pair it with `pie_enabled` to compare the configured scenario with the common dodge stimulus. The enabled log emits `aggro_switch` at lines 1577/1789, but `AGGRO_SWITCH_EXPECTED.md` explains the first switch occurs at 153.517 cm before the first dodge and the run observes only two of three scheduled dodges. This pair is a control example, not a successful dodge-rate threshold proof. `proof_report.py --control-log` can check positive tokens in enabled evidence and `no TOKEN` assertions in the control; a missing token matters only when the expected sheet defines that assertion.
3. **Failed attempt:** `Docs/BossCombatReview/Execution/Claude/B_STRAFE_STUCK/content_run1_FAIL_editor_crash_INT_DIVIDE_BY_ZERO_spawning_walls/` keeps command, raw crash log, result, and state snapshots. Its `result.json` has `exit_code: 3`. The directory name preserves the failure status; do not discard it or relabel it as a feature result. The separate `pie_r3c_run1/` is a completed process but failed setup for stuck recovery: it has no `strafe_stuck` event (see C-712 and the W3 status in `OPEN_ISSUES_DIGEST.md`). Process exit 0 is not equivalent to feature pass.
4. **Hash manifest:** `Docs/BossCombatReview/Execution/Claude/B_PARRY_STAMINA/evidence_sha256.txt:3-9` hashes the bounded positive run; `B_AGGRO/evidence_sha256.txt:16-29` hashes the control pair; `B_STRAFE_STUCK/evidence_sha256.txt:4-9,36-45` hashes a crash attempt and R3c. Run `python Scripts/Tools/check_evidence_sha256.py .` from the repository root to detect missing or changed files. Do not regenerate a manifest merely to silence a mismatch; investigate the changed evidence first.

## Capture and review checklist

- Use the owning PIE wrapper; retain its `command.json`, `result.json`, and unedited `editor_raw.log` with paths that distinguish control, pass, invalid setup, and crash/failure.
- Keep profile/map authoring readback and pre/post state when they establish the fixture. Record the build/evidence link and expected-sheet path in the owning `TEST_PLAN.md` entry.
- Preserve failed and negative-control runs next to positive evidence. Explain what they falsify or fail to establish; do not cherry-pick only the passing log.
- Hash the selected files after the run. Verify paths, byte counts and digests offline. A matching hash confirms identity, not completeness, correctness, or feature semantics.
- Report manual observations separately from machine-checked tokens. A process launch result, `RESULT outcome=...`, or schema-valid log is only one part of the evidence contract.

## Source and evidence references

- `Documentation/Boss/PROOF_WORKFLOW.md:8-35` — run capture, validator, and evidence paths.
- `Documentation/Boss/TOOLS.md:36-38` — bundle verification and paired `proof_report.py` semantics.
- `Docs/BossCombatReview/Execution/Claude/B_PARRY_STAMINA/pie_stamina_overlay_run1/editor_raw.log:1771,2087,2155` — bounded positive measurements.
- `Docs/BossCombatReview/Execution/Claude/B_AGGRO/pie_enabled/editor_raw.log:1577,1789`; `pie_control/editor_raw.log` — paired aggro observation/control, with its threshold-proof limit in `AGGRO_SWITCH_EXPECTED.md`.
- `Docs/BossCombatReview/Execution/Claude/B_PARRY_STAMINA/evidence_sha256.txt:3-9`; `B_AGGRO/evidence_sha256.txt:16-29` — hashes for a positive run and paired control artifacts.
- `Docs/BossCombatReview/Execution/Claude/B_STRAFE_STUCK/content_run1_FAIL_editor_crash_INT_DIVIDE_BY_ZERO_spawning_walls/result.json:1-6`; `evidence_sha256.txt:4-9` — retained failed attempt and digest entries.
- `Docs/BossCombatReview/Execution/Claude/B_STRAFE_STUCK/pie_r3c_run1/editor_raw.log`; `evidence_sha256.txt:36-45` — completed negative setup and retained hashes.
