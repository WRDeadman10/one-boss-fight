# AU-C21–C25 — dynamic melee camera baseline

**Status:** AU-C21–C24 offline complete; AU-C25 Lead run pending. No production camera option or default changed; Codex did not run the Editor.

## Evidence reconciliation

- C-1051 (BUILD-259 / fight video 2) reports close-range frames around 180 cm with the camera inside the boss mantle/legs or against ruins; the boss capsule's `ECC_Camera=IGNORE` lets the spring arm enter the body when the boss is beside or behind the player.
- C-1044 tested open ground at 105/200/300 cm and found full arm extension with no boss-caused trace hit. It did not cover a circling boss or the camera-inside-rendered-mesh state. The samples answer different questions.
- C-1105's B+C plus look-injected attack scenario is bounded to nine A4/A6 starts and records no intrusion/hide events. It is not continuous orbit coverage and does not close the dynamic baseline gap.
- The existing `probe_camera_inside_boss.py` already samples camera/pivot positions, actual and target arm length, approximate sweep hit, capsule channel response, visible-mesh AABB occupancy, CVar values, route and scenario. Sweep endpoint and AABB remain explicitly approximate.

## AU-C21–C24 additions

- Each 10 Hz probe row now emits `SAMPLE_JSON` with run, route, sample/frame-marker ID and game time, player-boss distance, pivot-to-camera distance, target arm length, boss-relative angle, camera-inside-mesh AABB state and HideBossInside CVar state. Unknown or non-finite telemetry remains `UNKNOWN`.
- Route labeling now follows C-1099/C-1104: unset encounter selection is DATA-default; only explicit `RPG_LEGACY_STARTUP=1` labels a run legacy, and combining that override with explicit G044 selection is refused. Lead must retain the matching same-run `[EncounterActivation]` witness.
- `Scripts/Tools/camera_probe_receipt.py` validates sample JSONL and rejects missing fields, malformed/non-finite values, stale run/frame-marker identities, mismatched marker/game times and non-boolean obstruction/hide states. `UNKNOWN` is preserved, never converted to a clear/zero intrusion result.
- C-1105's nine-start B+C look case is recorded as a separate bounded coverage cell; no continuous-circling claim is made.

## AU-C25 Lead return

Run the no-option-change, DATA-default, 30-second manual orbit at 150–250 cm in both directions, with scenario notes for standing, recovery, dodge, phase-two aura, and wall/floor passes. Preserve build ID, same-run G044 activation witness, probe revision, `SAMPLE_JSON` rows, control notes and correlated frame/video references. Record unreadable bounds as `UNKNOWN`; do not treat approximate AABB or sweep hits as rendered-pixel or collision-causality proof. Owner option selection remains open.

## Verification

`python -m unittest Scripts.Editor.test_probe_camera_inside_boss Scripts.Tools.test_camera_probe_receipt -q` — 8 passed. Codex did not run the Lead probe.
