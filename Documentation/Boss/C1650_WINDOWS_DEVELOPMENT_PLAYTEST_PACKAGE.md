# C-1650 Windows Development Playtest Package

Date: 2026-11-18 (Asia/Kolkata)
Status: packaged and archived; playable session has not yet been run.

## Build and delivery

- Configuration: Win64 Development.
- Map: `/Game/OneBossFight/Maps/L_SevarogArena`.
- BuildCookRun: PASS, exit 0, 436.76 seconds. Cook was given `-nosound`; the packaged game was not launched by Codex.
- C-1155: the task-specific runner acquired both locks, recorded 525 source/config input hashes as stable, and released both exact-token locks after UnrealEditor-Cmd exited. No asset/config edits were performed by the runner.
- Zip: `D:\BenchTransfer\OneBossFight_TestBuild_20261118_0438Z.zip`
- Zip size: 3,922,305,302 bytes (about 3.65 GiB).
- Zip SHA-256: `D871E3494606C651CF3EC04B7E1E46F1312F6DB2E3976B83DE900B7120501AEA`.
- Archive listing succeeded and showed 124 entries, including the game launcher, `.ucas`/`.utoc` content containers, play launchers, README, build info, and C-1155 receipt.
- Build ID: `OBF-DEVELOPMENT-20261118T0438Z-C1650`; executable SHA-256: `D6F5E6570A3A5AE71C3C8CEF57D6426F39BF479373F0261DBC41AD698539D698`.
- UAT log: `Saved/PackageBuilds/C1650_20261118/buildcookrun.log`; C-1155 receipt: `Saved/PackageBuilds/C1650_20261118/package_receipt.json`.

## Owner launch options

- `Play_AllFeatures.bat`: default mannequin plus Tier 1/Tier 2 art and camera options.
- `Play_Default.bat`: project defaults.
- `Play_Greystone_Visual_Experimental.bat`: Development-only Greystone visual opt-in; not a fit or Shipping acceptance.

The normal launch retains the mannequin player. The archive includes explicit notes and limitations in `README_OWNER.txt`.

## Unclosed acceptance

- BT-62 is still not accepted: the raw BehaviorTree attack-task tick is not instrumented, and full boss-death lifecycle is not proven by the automated Smoke.
- BT-71 owner Full-mode playtest was not performed.
- Greystone root-motion/combat trace/parry/Owner review gates remain open; its optional launch mode is experimental.
- No packaged executable smoke, gameplay run, or performance benchmark was performed for this package.

Cook warnings: material compilation fell back to Default Material for `M_Greystone_Ultimate_SpeedLines`, `M_Swirl_Plasma`, `M_Greystone_ToughSword`, and `M_Greystone_shield` on one or more SM5/SM6 targets. Details are in the retained UAT log.

The repository worktree was already broadly dirty (245 paths) and remains uncommitted. Codex made no commit or push.
