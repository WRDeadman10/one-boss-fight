# Combat proof workflow

Use this sequence when collecting evidence for a boss framework change. Keep source review, offline validation, native build/automation, PIE proof, and packaged proof as separate claims. A passing earlier stage does not imply a later stage passed.

## 1. Offline and source checks

Run only checks required by the assigned task. For FrameworkProof logs, the checked-in validator command is:

```powershell
python Docs\BossCombatReview\Execution\Antigravity\Reviews\validate_framework_proof_logs.py <run-folder>
```

The validator parses literal schemas and semantic relationships; review its exit status and diagnostic count. Its schema is in the validator's `SCHEMAS` map. For a token inventory comparison, run:

```powershell
python -I Scripts\Tools\check_validator_tokens.py
```

## 2. Build and native automation

From the project root, the repository's full suite command is:

```powershell
powershell -ExecutionPolicy Bypass -File Scripts\Rebuild.ps1 -Tests -NoRelaunch
```

The wrapper builds `OneBossFightEditor Win64 Development`, runs `Automation RunTests OneBossFight` with `-unattended -nullrhi -nosound -nosplash`, and leaves the editor closed. Preserve its raw logs and verify the completion counts and failures; wrapper success alone is insufficient.

For the Sevarog candidate's non-saving Editor validation, the exact locked command used was:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Editor/run_c1253a_locked_validation.ps1
```

That runner performs the Development Editor build, transient-object authoring dry-run with both production C++ validators, and full `OneBossFight` suite. Its retained logs and status are under `Docs/BossCombatReview/Execution/Codex/C1253A_TRANSIENT_DRYRUN/`. It does not save Sevarog content or provide PIE/package proof.

## 3. PIE drivers

PIE driver evidence is a separate live-engine proof. Open the project editor with `-nosound`, ensure the project bridge is available, then use the checked-in runner:

```powershell
Scripts\RunDrivers.ps1
```

For a named subset, use the runner's real `-Only` parameter with comma-separated driver names. Preserve each driver's output and its `RESULT passed/total passed` or `SUMMARY total checks, 0 failed` line. If a driver times out, restart the editor before another driver because a tick callback may still be registered. See [FULL_SUITE_EVIDENCE_HOWTO.md](FULL_SUITE_EVIDENCE_HOWTO.md) and [RunDrivers.ps1](../../Scripts/RunDrivers.ps1) for the checked-in run details.

Use only the per-driver console hooks documented in [TEST_HOOKS.md](TEST_HOOKS.md), with values copied from that driver's setup and expected sheet. Check declaration defaults and Shipping/Development guards first. Record the exact CVar values, selected route, and map in the run report; a hook-triggered or synthetic proof must not be described as unassisted gameplay evidence.

## 4. Evidence folder and hashes

Create a unique folder under `Docs/BossCombatReview/Execution/Claude/<RUN_ID>/` or the location assigned by the Lead. Retain the exact command, timestamp, raw logs, test completion counts, driver outputs, and a report describing only what each run proves. Preserve failed attempts; do not replace them with later passes. Hash evidence after copying it:

```powershell
Get-FileHash Docs\BossCombatReview\Execution\Claude\<RUN_ID>\tests_raw.log -Algorithm SHA256
```

Record SHA-256 values in `evidence_sha256.txt`. Check an evidence tree with the existing checker:

```powershell
python Scripts\Tools\check_evidence_sha256.py .
```

Only claim source audit, build, native automation, PIE, cook, or packaged proof when that exact stage has retained evidence. The commands above are repository commands; this guide records no new run result.
