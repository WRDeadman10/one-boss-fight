# Queue AL C31–C35 — capture integration

Offline driver and runner audit only; no UE launch, capture, ffmpeg render or build. Claude still owns the engine lock and runtime smoke.

| Task | Result |
|---|---|
| C31 | `pie_full_fight.py` already ended on boss death after a five-game-second outro, on time limit, and on exceptions; `finish()` releases held keys, unregisters the tick callback, logs SUMMARY/finished and requests PIE end. A missing player previously returned until the global timeout, risking a misleading capture after death/reset. Added a game-time three-second missing-pawn abort and immediate zero-HP player abort. Offline test covers both and recovery when pawn returns. A pending frame still needs Lead on-disk validation; `make_fight_video.py` refuses absent PNGs. |
| C32 | The port imports `unreal` only through a fake module in isolated tests; no Editor process is required. Route selection remains `H019_ENCOUNTER_DEFINITION` in the driver and `RunLeadPie.ps1` sets it per route. Shared helper now owns boss/component/montage/game-time/placement/refill/end-play lookups. A changed controller yaw during setup is the one intentional parity caveat for Lead smoke. |
| C33 | Existing `RunLeadPie.ps1` already accepts the full-fight script and opt-in `-Env`, keeps its lock, `-nosound`, `-abslog`, bounded timeout and route selection. A dry run with `-Routes @('legacy','data')`, `-Env @('ER_FIGHT_TIER2=1','FIGHT_MAX=60')`, `-StopMarker '[FullFight] finished:'` printed both commands and did not create `Saved/AL_FightDryRun`. No runner edit needed. For PowerShell `-File`, passing `legacy,data` as one argument fails validation; use an in-shell array or invoke routes separately. |
| C34 | Isolated fake-Unreal tests now pass 6/6. They verify 15-fps game-time/Png wait, Tier 2 default/off and opt-in before PIE, action cycle, refill rule, player liveness, and cross-tool parsing of FRAME, ACTION, COUNTER and BOSS_DEAD from the fixture. Source presence checks retain SUMMARY and `finished:` markers. |
| C35 | Lead live smoke command below must run only after the engine lock clears. Check both route logs for a `finished:` marker, boss death vs time-limit reason, no player-death abort, ordered FRAME IDs and actual PNG count, then render with `make_fight_video.py` and inspect subtitle/frame alignment. |

Lead PowerShell dry-run command (from the project root):

```powershell
& .\Scripts\RunLeadPie.ps1 -Script Scripts/Editor/pie_full_fight.py -Routes @('legacy','data') -Env @('ER_FIGHT_TIER2=1','FIGHT_MAX=60','FIGHT_FRAMES=D:/FightVideo/al_smoke') -OutputDir Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/AL_SMOKE -TimeoutSeconds 900 -StopMarker '[FullFight] finished:' -DryRun
```

For real two-route capture, invoke the runner separately with `-Routes legacy` and `-Routes data`, using distinct `FIGHT_FRAMES` folders to avoid both runs writing `f_00000.png` into the same folder. The command above only prints the plan. Tier 2 build and PIE proof remain separate KI-191 gates.
