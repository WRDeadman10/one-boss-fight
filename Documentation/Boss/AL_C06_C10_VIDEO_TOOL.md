# Queue AL C06–C10 — full-fight video input tool

Offline only; no ffmpeg render, Unreal, PIE, package or asset edit. Claude's retained `Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/pie_full_fight.py` emits `[FullFight] FRAME n g=... action=...` for `f_%05d.png`, `ACTION name t=...`, `COUNTER t=...`, `BOSS_DEAD at ... s`, and a final `finished:` marker. It requests frames at most once per 1/15 s of **game time** while slomo 0.5 is active; real wall-clock capture stalls are excluded from `g` deltas.

| Task | Result |
|---|---|
| C06 | Captured a representative marker sequence in `Scripts/Tools/fixtures/full_fight_sample.log`. FRAME `g` is absolute game time, ACTION/COUNTER times are fight-relative; the first captured frame begins the output timeline. |
| C07 | Wrote isolated offline tests first for 0.080/0.120 s game-time gaps, final duration, action/counter/death subtitles, missing PNGs, duplicate/nonmonotone frames and ASS brace escaping. |
| C08 | `Scripts/Tools/make_fight_video.py` strictly parses consecutive frame IDs and increasing game times, refuses missing PNGs, and writes an ffconcat file with each observed game-time delta. The final frame uses the median observed gap (or 1/15 s if only one frame) and is repeated as ffconcat requires. This final extrapolation is labeled by the code, not claimed as an observed interval. |
| C09 | The tool emits an ASS track with human labels for each ACTION, COUNTER and BOSS_DEAD and writes/prints a reproducible ffmpeg command. It does not execute ffmpeg. The command runs from its output folder so `ass=actions.ass` avoids Windows drive-colon parsing. |
| C10 | `python -I -m unittest discover -s Scripts/Tools -p test_make_fight_video.py` passes 4/4. Fixture concat has `duration 0.080000`, `duration 0.120000`, and one tail duration; subtitle track includes `Light attack`, `Guard counter`, `Boss defeated`. Real capture frame integrity, codec/render quality and owner approval remain Lead/owner gates. |

CLI: `python Scripts/Tools/make_fight_video.py --log <FullFight log> --frames <frame folder> --out <output folder>`. It writes `frames.ffconcat`, `actions.ass` and `ffmpeg_command.txt`, and prints the command. The user can render explicitly after reviewing those files.
