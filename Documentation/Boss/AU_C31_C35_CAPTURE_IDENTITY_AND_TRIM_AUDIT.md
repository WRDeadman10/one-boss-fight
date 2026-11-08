# AU-C31–C35 — capture identity, source-frame audit, and BUILD-255 trim handoff

## Scope and identity

This is an offline provenance/pixel audit of two already retained captures. It does not add a visual verdict or fill an owner review box.

| Capture ID | Review video | Source log | Source PNG directory | Scope kept with this ID |
|---|---|---|---|---|
| BUILD-255 | `Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/fight_review.mp4` | `fight_full.log` | `D:\FightVideo\fight` | Six black initial source frames; no Guard Counter reported in that capture. |
| BUILD-259 | `Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/fight_review2.mp4` | `fight_full2.log` | `D:\FightVideo\fight2` | Guard Counter sightings reported by Antigravity; this capture has its own seven-frame black lead-in, independently measured below. |

The build/video/log/frame-directory tuple is the identity boundary. BUILD-255's Guard Counter absence and six-frame count must not be copied into BUILD-259; BUILD-259's Guard Counter presence must not revise BUILD-255. BUILD-259's independently measured seven-frame lead-in is its own source-image finding, not a transfer of BUILD-255's count. Antigravity's review remains the source of the combat-visibility observations.

## Source-frame pixel audit

Used the existing standard-library `aura_png_metrics.mean_gray` decoder on the retained PNGs. A mean grayscale of exactly 0 means all decoded RGB pixels are black (alpha is ignored by this metric). The game times and action markers below come from the corresponding source log's `[FullFight]` lines; they are capture-relative game time (`g - first frame g`).

| Capture | Frame | `g` | Relative time | Mean gray | SHA-256 |
|---|---:|---:|---:|---:|---|
| BUILD-255 | 0 | 10.272 | 0.000 s | 0.000000 | `99b388208ffd4bf4b09c410f17faf073e4f6a7ba095f3f15b7f3d1cd16990623` |
| BUILD-255 | 5 | 10.784 | 0.512 s | 0.000000 | `99b388208ffd4bf4b09c410f17faf073e4f6a7ba095f3f15b7f3d1cd16990623` |
| BUILD-255 | 6 | 11.014 | 0.742 s | 51.756787 | `510224b3d4c08dc4d8def8fc99ce34e5c5bb3047ed3c79548194438cb4fb7c4c` |
| BUILD-255 | 7 | 11.186 | 0.914 s | 26.920272 | — |
| BUILD-259 | 0 | 10.157 | 0.000 s | 0.000000 | `99b388208ffd4bf4b09c410f17faf073e4f6a7ba095f3f15b7f3d1cd16990623` |
| BUILD-259 | 6 | 10.753 | 0.596 s | 0.000000 | `99b388208ffd4bf4b09c410f17faf073e4f6a7ba095f3f15b7f3d1cd16990623` |
| BUILD-259 | 7 | 10.892 | 0.735 s | 22.418615 | `a092769e4b58100ce6839f9729756b1980d5e355cdc70b194bf7ec172537bad4` |

The initial scan measured all frames 0–5 of BUILD-255 at mean gray 0, and all frames 0–6 of BUILD-259 at mean gray 0. Frame 6 is the first non-black BUILD-255 PNG; frame 7 is the first non-black BUILD-259 PNG. The first `[FullFight] ACTION` is `light t=0.91` in BUILD-255 and `light t=1.01` in BUILD-259. These are source-pixel facts only; no additional fight visual was judged.

Source-log SHA-256: BUILD-255 `fight_full.log` `591dd361bf63218324bcd8fd7d7488be5e029c63c4c127788f9e1c758526e565`; BUILD-259 `fight_full2.log` `9751739a368f8676896f8211ef209bf12b35825a1e2143a2384ab841265ff737`.

## BUILD-255 trim/review handoff

Source frames were retained, so the existing generator was run in input-generation mode only:

```powershell
python Scripts/Tools/make_fight_video.py --log Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/fight_full.log --frames D:\FightVideo\fight --out D:\FightVideo\au_c34_build255_trim6_20261109 --trim-leading-frames 6
```

The generated `frames.ffconcat` starts with source `f_00006.png`; it retains the source PNG numbering and subsequent frames. The first retained frame is 0.742 game seconds after frame 0. The ASS action captions are shifted by that same offset: the first Light attack at 0.91 becomes approximately 0.17 seconds into the trimmed excerpt. Generated inputs are `D:\FightVideo\au_c34_build255_trim6_20261109\frames.ffconcat` and `actions.ass`; `ffmpeg_command.txt` is an instruction only. No ffmpeg process ran and no trimmed MP4 was produced or reviewed. BUILD-259 files were not inputs.

The owner must decide whether this corrected BUILD-255 excerpt is needed and review any resulting video. The BUILD-255 and BUILD-259 owner checklist items remain separate and unchecked. This does not assert gameplay acceptance, owner approval, or package status.

## Checks

- New offline test binds each report's build/video identity and prevents the BUILD-255 black-frame/Guard Counter findings being silently treated as BUILD-259 evidence.
- Synthetic trim test checks retained source-frame numbers, identical frame/ASS time shift, and unchanged untrimmed input lists.
- `Scripts/Tools/test_make_fight_video.py`: 13 tests pass.
