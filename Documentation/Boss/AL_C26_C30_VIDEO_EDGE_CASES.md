# Queue AL C26–C30 — video tool edge cases

Offline tool/test changes only. No ffmpeg render, Unreal capture, package or asset edit.

| Task | Result |
|---|---|
| C26 | `make_fight_video.py` now rejects malformed FRAME/ACTION/COUNTER/BOSS_DEAD lines explicitly instead of silently skipping them. It already rejects missing first frame, duplicate/skipped frame IDs, non-increasing game timestamps and nonmonotone action times. Fixture tests exercise a skipped index and `g=nan`. |
| C27 | The CLI test creates an `Owner's frame folder` and a spaced output folder, verifies ffconcat's apostrophe escape, uses a relative `ass=actions.ass` filter command from the output folder, and confirms no MP4 is produced. ASS braces are escaped by a separate test. |
| C28 | Added single-frame fallback duration (1/15 s), long (>1 h) subtitle time and event-after-end checks. Full fixture still checks three variable durations and counter/death subtitles. |
| C29 | For a multi-frame capture, each concat duration is the next `FRAME g` delta. The final duration is a median-gap estimate, not a measured final interval; repeating the last image lets ffmpeg honor it. ACTION/COUNTER/BOSS_DEAD `t` fields are fight-relative and rendered against video start; Lead capture must confirm that first-frame alignment in actual output. |
| C30 | `python -I -m unittest discover -s Scripts/Tools -p test_make_fight_video.py` passes 8/8. Real ffmpeg decode, media timing and owner visual approval remain separate Lead/owner gates. |

CLI remains `python Scripts/Tools/make_fight_video.py --log <FullFight log> --frames <frame folder> --out <output folder>`; it writes concat, ASS and command text only.
