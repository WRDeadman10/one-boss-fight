# AU-C06–C10 — parry receipt, feedback and frame links

## Offline work

- `make_fight_video.py` now parses full-fight parry attempt/contact/recoil markers. A video caption is emitted only for a contact that follows an opened attempt and has exactly one sweep parried-count increment. Orphan, refused-window, duplicate, malformed, and multi-increment contact records fail closed.
- The full-fight driver rejects a parried-count delta greater than one instead of crediting it. It records recoil as a separate marker only after observing `AM_Boss01_ParryRecoil` in the live boss montage.
- A confirmed contact starts three post-contact frame requests (+0.05/+0.15/+0.30 game seconds). Each request is linked to a frame index/path; `PARRY_FRAME_READY` and the camera weighted-blendable readback are emitted only after the PNG exists. The data includes actual offset. PPM readback at parry press, contact and ready frames is explicit, including camera-missing/read-error states.
- Offline tests reject a frame marker for a nonexistent frame or inconsistent contact offset and reject recoil without a confirmed contact or the expected montage.

## Verification and Lead boundary

The focused suites `Scripts.Editor.test_pie_full_fight_offline` and `Scripts.Tools.test_make_fight_video` pass **25/25**. Python syntax compilation and `git diff --check` pass. No Unreal, build or PIE was run by Codex.

**Lead PIE still required:** run the full-fight driver on DATA-default with `ER_FIGHT_TIER2=1` to exercise recoil/PPM, and return BUILD ID, map, same-run route witness, script revision, action/A4 instance, opened window, exact count delta, recoil montage, PPM weights at press/contact/ready frames, frame labels/paths/hashes and stop reason. A runtime readback is not a visual judgment; full-fight owner ticks remain open.
