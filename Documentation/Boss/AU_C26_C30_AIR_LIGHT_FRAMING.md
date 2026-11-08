# AU-C26–C30 — Air Light start framing

**Status:** AU-C26–C29 offline complete; AU-C30 Lead PIE pending. Codex did not run Unreal. No production distance, animation or camera default was changed.

## Source and evidence boundary

- `FIGHT_VIDEO_REVIEW2_AG.md` reports 25 Air Light appearances, readable at mid-range and clipped at some starts close to the boss. It does not identify a minimum distance, a bad montage, or a production fix.
- `pie_full_fight.py` schedules Air Light as jump then R1. Before this change, the action marker recorded only rounded boss distance, while subsequent frame markers named the active action without camera/pivot/arm state. That could not associate exact framing telemetry to an Air Light start.
- The driver now emits JSON `AIR_LIGHT_CONTEXT` records at action start/end with run/action identity, game time, precise player/boss positions and distance, camera/pivot positions, target arm length and an upcoming same-run frame marker. Missing/non-finite positions are explicit `UNKNOWN`.
- `AIR_LIGHT_START_DISTANCE_CM` is an optional diagnostic-only setup input. When set for a Lead observation run, it places the player at that measured test position before Air Light; when unset, the full-fight schedule and distances are unchanged. The parser accepts any positive or unknown measured distance; no minimum clipping threshold is encoded.

## AU-C27 receipt contract

`Scripts/Tools/air_light_receipt.py` validates start/end context JSON and fails closed on missing fields, malformed JSON, non-finite distances, malformed vectors, stale run IDs, and frame-marker mismatch. Fixtures include 80, 110 and 500 cm to prove the parser does not impose a gameplay threshold. Frame references are telemetry sample markers; Lead must provide the corresponding actual captured frame/video reference in the run receipt.

## AU-C29/C30 Lead matrix

| Cell | Lead setup | Result |
|---|---|---|
| Open | Record a repeatable open-start distance; set `AIR_LIGHT_START_DISTANCE_CM` to it | NOT RUN |
| Mid | Record a repeatable mid-start distance under same build/route/action | NOT RUN |
| Close | Record a repeatable close-start distance under same build/route/action | NOT RUN |

Lead chooses and records three observed setup distances; these are comparison points, not minimum-distance acceptance thresholds. Use DATA-default with a same-run G044 activation witness, identical build and Air Light sequence. Return actual start distance, action ID/time, camera/pivot/arm data, matched video/frame references and whether clipping was visible. Keep static camera data separate from visual framing judgment. No camera option is applied.

## Verification

`python -m unittest Scripts.Tools.test_air_light_receipt Scripts.Editor.test_pie_full_fight_offline -q` — 20 passed. `py_compile` and `git diff --check` passed (existing line-ending notices only). Codex did not run the Lead matrix.
