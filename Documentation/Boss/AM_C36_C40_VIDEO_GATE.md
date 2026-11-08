# Queue AM C36–C40: fight-video gate

## C36: original capture and alignment

The BUILD-255 data-route `P_FIGHTVIDEO/fight_full.log` has `FIGHT_START` at line 1603 and `FRAME 0 g=10.272` at line 1608. The driver sets `fight_time=0` for its first fight tick, then advances it by game-time deltas; `make_fight_video.py` uses FRAME game-time gaps for ffconcat and fight-relative ACTION/COUNTER times for ASS. The first action `light t=0.91` (log line 1639) is therefore aligned to the original FRAME 0 origin. The source PNGs `D:/FightVideo/fight/f_00000.png` through `f_00005.png` have mean grayscale 0.00; `f_00006.png` has 51.76 and occurs at `g=11.014`, 0.742 game seconds after FRAME 0. The existing MP4 contains the black lead-in. The source log has one late real guard arm and no accepted counter; Tier 2 was off. This video cannot prove those missing effects.

## C37: opt-in Lead recapture

Lead C-1044's 105/200/300 cm trace found no boss-induced camera occlusion, so there is no camera Source fix to apply. The shared driver already polls guard arm through 3.5 game seconds after a 2.5 second L1 injection; this guard tail is offline tested. BUILD-259 has since proved the real A4 block-to-counter montage chain on both routes, but boss HP did not decrease at 250 cm. Recapture is gated on the C-1045 closer-range probe proving a damaging counter. Then Lead may opt in with separate frame roots per route and Tier 2 enabled. Example for the data route (Lead supplies a new, empty frame root):

```powershell
& ./Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_full_fight.py -Routes @('data') -Env @('ER_FIGHT_TIER2=1','FIGHT_MAX=900','FIGHT_FRAMES=D:/FightVideo/recapture_data') -OutputDir Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO_RECAPTURE_DATA -TimeoutSeconds 9000
```

`RunLeadPie` checks editor/lock and launches with `-nosound`. The driver may refill the player below 35 HP; boss health and AI remain real. A fresh capture must show the real arm and counter acceptance, or be classified as an evidence gap. Lead chooses the actual frame root and owns the engine run and rendering. No recapture is present yet.

## C38–C39: review links and render-marker regression

`FIGHT_VIDEO_REVIEW.md` and `OWNER_REVIEW_PACK.md` still link to the reviewed BUILD-255 MP4, clearly mark Tier 2/counter absent, and leave all seven owner boxes empty. They now cite C-1042 separate PIE Tier 2/default-wiring proof and C-1044 camera/guard results. No new video link is inserted before a new MP4 exists.

The black lead-in is a reproducible capture issue. `make_fight_video.py --trim-leading-frames N` explicitly drops a measured number of leading frames and subtracts their exact game-time offset from ASS event times. A focused test verifies that the first kept frame and subtitles shift together and that removing all frames fails. For the original capture, `N=6` yields first `f_00006.png` and first action at `0:00:00.17`; prepared inputs are `Docs/BossCombatReview/Execution/Codex/P_FIGHTVIDEO_TRIM6/{frames.ffconcat,actions.ass,ffmpeg_command.txt}`. The tool writes an ffmpeg command but does not render. The first visible frame is still the source, not a new screenshot.

## C40: gate status

Offline batch complete: 16 focused Python tests pass; `make_fight_video.py` generated trim-six inputs from 7,326 logged frames without running ffmpeg. The next Lead gate is build/native suite and A4 guard probe (C-1044), then an opt-in recapture, render, and owner full-fight review. No owner box, packaged behavior, camera Source change, or new video is claimed.
