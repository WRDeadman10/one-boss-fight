# Queue AN-C36–C40 — fight video and renderer handoff

**Scope:** read-only index and renderer/test audit for the retained BUILD-259 data-route capture. Antigravity owns visual verdicts; the owner owns review ticks. Codex did not render, alter footage, or change any owner checkbox.

## Capture index

Primary artifact: [`fight_review2.mp4`](../../Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/fight_review2.mp4). The existing Antigravity report [`FIGHT_VIDEO_REVIEW2_AG.md`](FIGHT_VIDEO_REVIEW2_AG.md) identifies it as 960×540, 25 fps, 722.04 s and ties it to data route / BUILD-259. The timestamped observations below index that report; they are not a new visual assessment by Codex.

| Capture time | Existing report observation | Review boundary |
|---|---|---|
| 00:04.63 and recurring examples | Backstep appearances | Antigravity's report records 50 appearances; owner full-fight tick remains separate. |
| 00:24.09, 00:30.50, 00:47.92, 00:54.26 | Air Light / Air Heavy examples | Reported as visible in this capture; prior default-wired/runtime-assigned proof remains separate evidence. |
| 02:50.15, 07:27.50, 09:00.43, 11:14.45, 11:33.38, 11:56.50 | Guard Counter appearances | Report records six actions and four direct damaging hits. Final example is reported at 11:56.50; boss-death log marker is 716.8 s. |
| 06:11.40, 10:45.00, 11:15.00 | Phase-Two Aura camera samples | Antigravity reports not visible in the capture, including two open-silhouette samples. This does not negate separate PIE lifecycle proof. |
| Full capture | Parry Recoil and Parry Distortion | Report says driver did not inject parries; absence is a capture gap, not a failed visual verdict. |

The frame/event game-time relationship for this second capture was not independently recomputed. Do not treat the table as new runtime timing evidence. BUILD-255 `fight_review.mp4` is separate: its existing review records six black source frames and a prepared trim-six input, but no revised MP4 review. Do not transfer that first-frame limitation to `fight_review2.mp4` without checking its source frames.

## Renderer and test audit

`Scripts/Tools/make_fight_video.py` parses consecutive frame indices and strictly increasing game times, builds ffconcat durations from game-time deltas, shifts subtitle times by the retained-frame game-time offset when `--trim-leading-frames` is used, and writes an ffmpeg command without executing it. Existing `Scripts/Tools/test_make_fight_video.py` covers synthetic trim/subtitle offset, malformed/gapped frames, missing images, escaping, long times, spaced paths, and that the CLI does not render.

No renderer defect was reproduced from checked-in source/tests, so AN-C39's conditional fixture was not added. Existing tests do not verify image pixels or prove a real capture's stated black-frame count; that remains an input-evidence check before any future recapture. No large video was re-rendered.

## Handoff

- Keep owner review boxes unchecked until the owner reviews the capture.
- Preserve Antigravity's per-move/aura findings in `FIGHT_VIDEO_REVIEW2_AG.md`; Codex adds no visual verdict.
- Before presenting a new capture, retain the exact log, source-frame directory/count, generated ffconcat/ASS inputs, and rendered output together. If trimming is needed, compare the first retained frame and subtitle offset against the source log, then review the rendered file.
- Camera A/B/C remains an owner decision; this report does not authorize camera Source or art changes.
