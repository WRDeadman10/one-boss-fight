# AU-C36–C40 — full-fight receipt accounting and Lead smoke

## Offline changes

- The full-fight driver now emits a JSON `RUN_PROVENANCE` row containing the unique run ID, explicit build ID, map name, configured route, Tier 2 state, and SHA-256 of the driver revision. The receipt checker independently requires exactly one matching `[EncounterActivation] route=...` witness from the same raw log; filenames do not determine route.
- Every scheduled action has a stable `run:action:NNNNN` ID. Frame markers keep the existing `FRAME <index> g=<time>` prefix used by the video generator and add a same-run frame ID, action name, and action ID. Guard Counter markers link to the guard action. The parser returns each action's same-run frame indices and explicit zero counts for action types that did not occur.
- Each actual player refill logs a separate count, fight time, HP before/after, and boss HP sample. Player death is counted and marked independently from refill. The summary includes frame/action/contact/refill/death totals, boss HP/max at setup and HP at finish, starting/ending AI controller identity, and explicit zero driver-side boss health/AI writes. Boss HP can change from combat damage; that does not mean the driver writes it. An unknown AI controller, changed AI controller, or unexplained counter mismatch fails closed.
- Added `Scripts/Tools/fight_capture_receipt.py`, which validates duplicate/missing summaries, action totals, exact-one parry count deltas, refills, deaths, frame continuity, action/frame/run links, boss-death/finish consistency, and provenance. It emits a JSON receipt to stdout via `--log`.

## Checks

Test-first synthetic receipt contracts cover valid accounting, duplicate/missing/contradictory totals, wrong-run frame/action links, missing action types, bad refill readbacks, wrong/unknown AI controller, route/build identity, and the JSON CLI. The driver also has offline contracts for separated refill/death fields and frame/action identity. The video parser still accepts the extended markers while preserving its prior frame regex.

- Full-fight driver offline, capture receipt, and video generator tests: 44/44 pass.
- Python syntax compilation passes.
- No Unreal, Editor, build, package, or image/video rendering by Codex.

## AU-C40 Lead smoke request

Run only after choosing the actual current BUILD ID. Use a fresh run ID and empty frame/output roots:

```powershell
Scripts/RunLeadPie.ps1 -Script Scripts/Editor/pie_full_fight.py -Routes data -Env "FIGHT_RUN=AU_C40_<fresh-id>", "FIGHT_FRAMES=D:/FightVideo/AU_C40_<fresh-id>", "FIGHT_MAX=30", "FIGHT_BUILD_ID=<current-build-id>", "FIGHT_MAP_NAME=L_SevarogArena", "ER_FIGHT_TIER2=0" -OutputDir D:/FightVideo/AU_C40_<fresh-id> -TimeoutSeconds 480
python Scripts/Tools/fight_capture_receipt.py --log D:/FightVideo/AU_C40_<fresh-id>/data.log
```

Return the raw log, same-run activation witness, generated JSON receipt, and output frame count. The 30-game-second smoke should stop cleanly at its time limit; a rejected or absent stop marker, empty action/frame coverage, unknown boss AI identity, or a receipt validation error means no pass. This is a smoke gate only, not another long fight or owner visual review. Claude owns this PIE run and decides whether further capture is warranted.
