# Queue AP-C36–C40 — switch isolation and evidence audit

**State:** offline closeout complete for this batch; all Lead build/runtime acceptance is still pending.

## Sequential run and contamination controls

For each route, run S0 first, then each single switch S1–S3, followed by mixed states S4–S7. Use a clean process/PIE identity per state, set all three switches explicitly, read them back from the passive probe, record the scenario label and build/source identity, and return all three to zero before ending PIE. The rig's three Apply methods are called independently each camera tick; EndPlay invokes each matching cleanup. If reset or target replacement interrupts a run, retain the artifact, verify cleanup, then restart the affected state under a new run identity.

## State ownership and effects

Static source tests establish that:

- BossBlocks changes only the identified pack boss capsule's `ECC_Camera` response and restores the saved value only when the experiment's Block value remains present.
- HideBossInside adds only visible boss skeletal/static mesh components to the local controller's `HiddenPrimitiveComponents` list and removes only entries it added. It does not touch collision, actor visibility, gameplay, aura or non-mesh components.
- LockOnFraming changes only the existing spring arm's world rotation and temporary `bUsePawnControlRotation` mode. It does not write controller rotation, player transform, movement input or attack aim.
- All three cvars are distinct, Development-only and default `0`; each behavior has an independent dispatch, target-loss/disable handling and EndPlay cleanup path.

The offline contracts check target replacement, missing targets, weak component cleanup, finite/unreadable geometry, independent CVar combinations, player-input ownership, and no unrequested gameplay side effects. CVar numeric values (5 cm margins, 0.35 s grace, 120 deg/s cap) are cross-checked against source and explicitly marked provisional.

## Acceptance status

Focused camera-source tests and passive probe tests pass; syntax, link and diff checks are recorded at the current Queue AP status. No C++ build, native suite, Unreal runtime, PIE or package run has been performed by Codex. Claude still owns the build/native suite and legacy/data PIE. The eight Development-package matrix cells remain blocked because the existing dynamic probe requires the Editor and no package camera driver exists. Do not close KI-037 or KI-066, mark any option runtime-proven, or treat S7 as an approved combination. Owner option and default remain undecided.
