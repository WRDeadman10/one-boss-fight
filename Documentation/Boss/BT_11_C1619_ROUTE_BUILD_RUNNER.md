# BT-11 — C-1619 route build runner

Date: 2026-11-16
Status: source review accepted; no test or engine command was run.

## Change

Added `Scripts/Editor/run_c1619_route_build_locked.ps1` to perform the current C-1619 Development build and complete DD27j-pinned `OneBossFight` suite under the C-1155 two-lock protocol. A pre-build approval receipt must name the acting lead (Codex), approve only the source build, and match the exact current `RPGPlayerMovesSubsystem.cpp/.h` SHA-256 values. The runner refuses a running Editor, rechecks hashes after lock acquisition, requires complete suite evidence, and releases only locks bearing its owner token.

Only after successful build, complete passing suite, unchanged source hashes, and confirmed release of both locks does the runner emit `route_lead_approval.json` for the route Smoke runner. That receipt has `task=C-1619 route acceptance`, `lead=Codex`, `approved=true`, build exit 0, suite PASS and exact subsystem hashes. The Smoke runner now accepts Claude or Codex as lead while retaining the existing approval, build/suite and exact-hash checks.

Added `Scripts/Tools/test_c1619_route_build_runner_contract.py` with seven source-contract assertions. It was not run, per task scope. Antigravity independently reviewed the runner and Codex accepted the source workflow. PowerShell and Python syntax parsing passed. No build, Editor, PIE, asset write, commit or push occurred. Do not execute it until an explicit current-hash lead receipt is prepared and the owner hands over engine access.

## Remaining route evidence

BT-13 investigates actual raw BehaviorTree attack-task tick evidence. BT-14 is the separately gated build/suite execution, and BT-15 is the route Smoke. Smoke does not exercise boss death; a playable build is not yet available.
