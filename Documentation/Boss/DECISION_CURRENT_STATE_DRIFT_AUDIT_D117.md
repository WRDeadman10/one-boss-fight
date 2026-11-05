# Decision/current-state drift audit — D117

**Scope:** compare the current `PROJECT_STATE.md` header and its retained historical summary against dated owner decisions and the proof ledger. Static document/source-of-record check only.

| Claim | Cross-check | Finding/action |
|---|---|---|
| Current project-state census: ledger v3.36, 75 WITNESSED / 7 PARTIAL / 0 NOT YET of 82 (`PROJECT_STATE.md:5`) | `witness_status_v3.json` declares version 3.36 and census 75/7/0; `NOT_YET_CENSUS.md` says zero current rows; `PARTIAL_UPGRADE_PLAN.md` lists seven current partial blockers. | Current claim agrees with its authorities. |
| Current performance target: packaged 1080p 60 FPS, p99 <=16.67 ms (`PROJECT_STATE.md:100`) | Owner decision in `DECISIONS.md:582` makes RTX 3060 an acceptable proxy and retains 60 FPS / 16.67 ms; the task dashboard keeps Gate 4 performance open pending console-session evidence (`TASKS.md:76`). | Target/proxy policy agrees; evidence remains open. |
| Boss balance values and nine-run 122–143 s result (`PROJECT_STATE.md:6`) | Owner's 2026-10-24 decision at `DECISIONS.md:569` records 2000 max HP, 0.03 bleed fraction, 0.39 starter multiplier, 100 riposte, and 122–143 s; KI-098/096 citations remain attached. | No drift found in the top-line balance summary. |
| Latest suite was BUILD-182, 332/332 and current checkout unverified (`PROJECT_STATE.md:99`) | `TEST_PLAN.md:771` and C-758 report BUILD-187 335/335 after C-757's Source fixes; no later Source edits appear in this work cycle. | Stale; corrected to BUILD-187 and current Source state. |
| Queue D proposal is next after S200 (`PROJECT_STATE.md:52`) | The Queue D status tail now records D116 complete; current task is D117. | Stale pointer; corrected to say Queue D is active through D116. |
| Older project snapshot says 120 FPS / 8.33 ms and names the retired player/boss direction (`PROJECT_STATE.md:152`) | Owner's final 60 FPS decision is recorded in `DECISIONS.md:9,384,582`; the pack-player/boss decision is in the dated decisions section. | Stale but retained historical passage; annotated as superseded so it cannot be mistaken for current scope. |
| Older “Not done” paragraph calls 79 FPS / p99 27 ms the only performance baseline and says the milestone is on hold (`PROJECT_STATE.md:178`) | Later A-220/A-221 Shipping profiling and GPU analysis are recorded in `DECISIONS.md:1057-1074`; `TASKS.md:76` still shows the actual Gate 4 performance result pending. | Status wording was stale; replaced with historical editor baseline, later profiling evidence, and the current open console benchmark. |

**Acceptance result:** current target, census, and balance figures agree with their dated authorities. The stale suite status, Queue D pointer, old 120 FPS scope, and performance-status wording were corrected or explicitly marked historical. No test, build, or engine run was performed.
