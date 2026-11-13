# Queue BB Batch 7: X31–X35 Greystone Follow-up

## X31 — Saved-wrapper notify readback

Added `Scripts/Editor/verify_greystone_wrapper_readback.py`. After the Lead authoring run creates the four allowlisted wrappers, the driver reloads the source montage and fit sequence, requires each exact saved wrapper package to exist, and compares target slot, skeleton, notify tracks, notify class/state/time/duration rows, sections, and first target sequence against the source table through `author_greystone_player.py`'s UE 5.5 readback helpers. It cannot save/create/delete assets and fails closed if any wrapper is absent. This is a Lead-run Editor check; it has not been run because the wrapper asset path is currently absent.

Offline contract: `Scripts/Tools/test_bb_x31_greystone_wrapper_readback_contract.py` passed 3/3, covering four-table scope, exact path/readback, fail-closed absence, and no save/create/delete calls. The saved-package Editor readback itself remains Lead-run after authoring.

## X32–X35 — blocked prerequisites

- **X32 BLOCKED:** `BP_GreystoneERPlayer` is not present under `Content/OneBossFight/Player/Greystone`; the retarget child and project-owned socket proof are prerequisites for a valid sword-contact/parry driver. The native Sevarog endpoint bones mentioned in C-1248 are not evidence for Greystone sockets.
- **X33 BLOCKED:** the route driver requires the child class and its four saved montage references. Without those packages, flask/hit-react/death checks would silently exercise the mannequin parent and cannot accept the Greystone child route.
- **X34 BLOCKED:** `rpg.GreystonePlayerTestPawn 0` restores the default player startup choice, but a meaningful rollback test must first load/activate the child and then prove the returned pawn class and montage/component state. The child does not exist yet, so the test cannot reach its premise.
- **X35 BLOCKED:** `OneBossFight.Content.CookCoverage` cannot certify child/wrapper assets until the four wrapper packages and child BP have been authored. No speculative cook root was added.

No Unreal, PIE, build, package, source production change, or asset operation was performed. Resume X32–X35 after Lead authoring/readback establishes the child and wrappers.
