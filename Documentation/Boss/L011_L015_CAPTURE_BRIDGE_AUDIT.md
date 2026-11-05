# Queue L Batch 3 — capture bridge and receipt audit

## Task disposition

| Task | Status | Evidence and boundary |
|---|---|---|
| L011 | **DONE — interface audit** | `pie_a4_low_sweep.py` executes from a Slate post-tick callback and obtains the active game world through `UnrealEditorSubsystem.get_game_world()`. `URPGPlayerMovesSubsystem::BuildEncounterParitySnapshot()` is BlueprintCallable, but this repository has no verified Python-to-active-world subsystem accessor/call path. See K011–K015 audit. |
| L012 | **BLOCKED** | A read-only bridge requires the exact UE Python binding and world/subsystem lifecycle to be Lead-verified. No unverified accessor was added. |
| L013 | **LEAD-RUN BLOCKED** | No eligible fresh legacy capture is present; the A4 driver does not currently emit the full v2 envelope. |
| L014 | **LEAD-RUN BLOCKED** | G044 selection assets and a verified capture bridge are absent; no selected-route envelope can be truthful yet. |
| L015 | **TOOLS READY; NO EVIDENCE TO VERIFY** | `compare_encounter_parity.py --verify-source-logs` verifies every v2 observable's raw-log SHA-256. `verify_evidence_manifest.py` checks unique, in-root evidence paths, existence, optional byte counts, and hashes. No new run receipts or manifest exist. |

## Receipt checks available for L015

- `encounter_parity_receipt.py::build_receipt` requires a nonempty run ID,
  full identity, route/selection state, exactly one boss and player participant,
  terminal/check markers, and per-observable source-log path/hash/trial ID.
- `compare_encounter_parity.py::read_receipt` validates the v2 envelope;
  `verify_source_logs` resolves each log relative to its receipt (or accepts an
  absolute path) and rejects missing files or hash mismatches.
- `verify_evidence_manifest.py` roots file entries at the manifest directory,
  rejects duplicate/escaping paths, and verifies present file bytes/hash.
- For paired runs, the comparator requires distinct run IDs, compares declared
  identity and observable values, reports unmatched trial IDs as inconclusive,
  and preserves cited receipt/log hashes in its report.

The offline receipt checks do not prove capture truth: the Lead must retain the
driver, command/configuration, runtime snapshot, raw log, and run manifest from
the same run. No Python-to-UE bridge, runtime receipt, test, build, or Unreal
execution was added or performed for this audit.
