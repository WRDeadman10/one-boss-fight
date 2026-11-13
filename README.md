# One Boss Fight

> A single-player Soulslike boss duel for Unreal Engine 5.5.4, built on the Advanced ARPG Combat pack: the pack's combat mannequin against the Ember Warden, a re-skinned great sword boss.

[SCREENSHOT: the player facing the Ember Warden in the arena]

## The Duel

One encounter, one boss, and no filler: wake the Ember Warden in `L_SevarogArena` (the level keeps its early working name), learn the attack sequence, manage stamina and posture, then create an opening for a frontal riposte. The fight changes at phase two and ends with a victory/retry flow rather than a menu transition.

[SCREENSHOT: phase-two roar or leap attack]

## Builds

| Build | Weapon identity | Combat focus |
|---|---|---|
| Starter | Pack sword | Baseline melee build. |
| Strength | Claymore | Higher posture damage, heavy stamina commitment, and authored hyperarmor windows. |
| Dexterity | Dual swords | Faster, lower-posture hits that build bleed. |

[SCREENSHOT: the three-build selection screen]

## Controls

The duel uses the supplied Advanced ARPG Combat input layout.

- Move, camera, lock-on, light attack, strong attack, dodge, and jump use that layout.
- Choose a build before waking the boss: press **B** for the in-game selector, or use `rpg.Build Starter|Strength|Dex`. Controller and menu playtesting remain owner validation items.
- After victory, the retry prompt reloads the encounter.

### Close-attack readability

`rpg.CloseTelegraph` stretches the short pack stand-in tells for close attacks. Its shipped default is `0.4`; set it to `0` to compare the pack's raw pacing. This is an interim readability aid while the authored close-attack clips remain art-blocked, and the owner feel test remains the final decision.

## Run A Packaged Build

1. Have Claude run packaging through a Lead-approved C-1155 locked runner. Do not invoke `Scripts/Package.ps1` directly; packaging/cooking launches engine tools and must acquire both locks, abort on either existing lock or any running UnrealEditor process, and release only owned locks.
2. Launch the staged `OneBossFight.exe` produced under `Saved/StagedBuilds/Windows`.
3. For a short launcher-and-log smoke check, use `Scripts/PackagedSmoke.ps1`.

The historical Shipping package passed its binary debug-off check, staged-content manifest check, and launcher smoke check. A full packaged fight and win/retry hand check remain open. Any new package/cook must run through a Lead-approved C-1155 locked runner; do not run `Scripts/Package.ps1` directly.

## Verification Status

- The latest Lead-verified full suite is BUILD-295 at 501/501; the separate later Codex locked C-1262a verification also reached 501/501. See `Documentation/TEST_PLAN.md`; the receipts have different owners.
- Live Sevarog evidence covers four primary cards, with the S1/S2 trace-contact reach gap at 140 cm and general approach navigation still open; see `Documentation/TEST_PLAN.md` and `Documentation/KNOWN_ISSUES.md`.
- Historical PIE regression and Gate 4 soak counts remain in the dated `Documentation/TEST_PLAN.md` entries and are not presented here as current acceptance.
- Current balance verification uses the 2,000-health boss, 3-percent bleed proc (60 damage), starter 0.39 multiplier, and the three build choices.

## Performance Target

The release target is a packaged 1920x1080 full encounter at at least 60 FPS average with a p99 frame time at or below 16.67 ms, on an RTX 2060 Super. The owner-console RTX 3060 proxy runs are valid proxy evidence but remain below the absolute target; the target-hardware acceptance is still pending. See the latest phase results in `Documentation/PERFORMANCE_LOG.md` and the current owner decision in `Documentation/DECISIONS.md`.

[SCREENSHOT: benchmark or performance capture]

## Team Workflow

The owner directs design decisions and commits. Claude owns editor work, builds, PIE drivers, packaging, and runtime verification. Codex owns static engineering, tools, documentation, and code that Claude reviews before building. Antigravity supplies the Blender art and animation loop. The shared task tracker and mailbox retain evidence, open risks, and validation status instead of treating an unrun feature as complete.

## Project Status

Current progress per milestone is the dashboard at the top of `Documentation/TASKS.md`. The remaining high-weight work is balance verification, a valid packaged performance run, Shipping/package checks, presentation capture, owner hand tests, and the remaining art/audio integration.

## Build From Source

Engine builds and automation suites are Lead-owned unless explicitly assigned. Use only the task-specific C-1155 locked runner; never execute the raw build/test commands or `Scripts/Rebuild.ps1` below. The runner must acquire both `ENGINE_LOCK.json` files, refuse any existing lock or running `UnrealEditor*` process, and remove only locks it owns. Automation suites must include `-DD27jManifestHash=cd088e394e42a930b47120d76831d517e92c9d7dbbd140920402fc577be129ec`. If no approved runner exists for the task, stop before launching the engine and ask Claude to provide one.

### Requirements

- Unreal Engine 5.5.4 (launcher install)
- Visual Studio 2022 or newer with the "Game development with C++" workload
- Git + Git LFS (`git lfs install` once per machine)

### Build

The `Build.bat` invocation is intentionally omitted here; select the task-specific locked runner assigned by Claude.

Open `OneBossFight.uproject` only under the explicit owner/Lead editor handoff and applicable C-1155 lock. Close the editor before structural C++ changes (new modules/classes need a restart).

### Test

Headless automation tests are run only through a task-specific C-1155 locked runner, after confirming no `UnrealEditor*` process is running. The raw generic invocation is intentionally omitted; the runner supplies the pinned `-DD27jManifestHash` and verifies complete successful test rows.

Do not start `UnrealEditor-Cmd.exe` directly for this suite.

### Content setup and scripts

| Script | Purpose |
|---|---|
| `Scripts/Editor/setup_m1_content.py` | Historical headless setup utility. Any Editor-Cmd execution requires an explicitly assigned task-specific C-1155 locked runner; do not run this command directly. |
| `Scripts/Package.ps1` | Cook and stage a Development or Shipping build to `Saved/StagedBuilds`; invoke only through an approved C-1155 locked package runner. |
| `Scripts/RunBenchmark.ps1 -Label <name>` | Run the packaged benchmark at 1920x1080 and print `summary.json` (avg FPS, p95/p99, frames over budget). |

Decisions, performance log, test plan and known issues are in `Documentation/`.
