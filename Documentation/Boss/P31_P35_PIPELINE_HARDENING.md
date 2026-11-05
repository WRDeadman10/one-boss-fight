# Queue P31–P35 pipeline hardening

Status: offline preparation complete; two acceptance steps are Lead-run and remain pending. No Editor, asset save, cleanup, or deletion was performed by Codex.

## P31/P32: evidence run safety and hashes

`Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1` now refuses any existing `OutDir` before creating files or checking/starting the engine. This prevents a repeated run from overwriting an earlier evidence folder. Offline refusal test:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Tools/test_run_editor_script_guard.ps1 -Runner Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Tools/test_editor_runner_syntax.ps1
```

The common Lead runner dot-sources `Scripts/Tools/write_evidence_hashes.ps1` and writes a sorted `evidence_sha256.txt` with relative slash-separated paths after `result.json` is closed. The helper excludes its own manifest. Offline hash test:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File Scripts/Tools/test_evidence_hashes.ps1
```

**P32 still requires a new Lead-run evidence folder** and verification of every listed hash. Reuse a fresh unique `OutDir`; the runner intentionally rejects existing folders.

## P33: BUILD index

`Documentation/TEST_PLAN.md` now has a short range index for BUILD-183–BUILD-217 immediately before the detailed build records. Detail records remain intact below it; the index links to their line anchors.

## P34: known-issue sweep

The KNOWN_ISSUES entries that cite this build interval were checked. KI-178 is already resolved by BUILD-187 and retains its reachability caveat. KI-179 remains open because BUILD-186 removed an unworkable transient-world watchdog assertion. KI-180 remains open pending execution verification after the source fix in BUILD-188. No additional row in BUILD-183–BUILD-217 was shown to close an issue; no status was inferred from a green suite alone.

## P35: owner cleanup candidates (no deletion)

The following packages are candidates only, based on the BUILD-204/208 and SEL-008 run notes. Codex has not deleted or changed assets. `Scripts/Editor/report_owner_cleanup_referencers.py` reports direct hard and soft Asset Registry referencers; run it in a read-only Lead Editor process and preserve the `[P35_REFERENCERS_JSON]` line in the run evidence before any owner cleanup decision.

| Candidate package | Reason listed in run notes |
|---|---|
| `/Game/OneBossFight/FrameworkProof/DA_Sevarog_ComboOutcome_FAG23` | Failed/abandoned attempt |
| `/Game/OneBossFight/FrameworkProof/DA_Sevarog_ComboOutcome_FAG23b` | Failed/abandoned attempt |
| `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofComboOutcomeFAG23` | Empty failed-attempt map |
| `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofComboOutcomeFAG23b` | Empty failed-attempt map |
| `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofStrafeBlockerSEL008` | Empty failed attempt; `...SEL008b` is the working map |
| `/Game/OneBossFight/FrameworkProof/DA_Sevarog_ComboOutcome_FAG23c` | Superseded by FAG23d |
| `/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofComboOutcomeFAG23c` | Superseded by FAG23d |

The referencer counts and identities remain pending until Claude runs the script in Editor. A zero direct referencer count is not, by itself, authorization to delete.
