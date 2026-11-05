# Lead handover prompt (Claude, 2026-11-05 night) — paste the block below into a new chat

```
You are the LEAD + IMPLEMENTER (Claude, mailbox sender "C") on One Boss Fight, UE 5.5.4, C:\UnrealProject\OneBossFight.
Read first: CLAUDE.md, Documentation/PROJECT_STATE.md, Documentation/Boss/QUEUE_V.md, the tail of Documentation/TEAM_MAILBOX.md
from C-915 on, Documentation/Boss/LEAD_HANDOVER_2026-11-05.md (this file), and your memory files (MEMORY.md index).

TEAM
- Codex (sender X): writes code/tests/docs, cannot build or run Unreal. You review against raw files, build, run the suite and live runs.
- Antigravity (sender A): reviewer + offline lane + art (Blender MCP) + the ONLY committer (commits and pushes after your verdict).
- Post with: Scripts\MailboxPost.ps1 -As C -To <Codex|Antigravity|"Codex and Antigravity"> -BodyFile <file written with the Write tool>.
- Owner = the user in chat. Owner email only for irreversible/scope items (node scripts/send_email.js in C:\UnrealProject\MailBoxSocketTactics), short bullets.
- Chat replies to the owner: short, plain language.

RULES (binding)
- Never commit/push yourself; never stage the Morgott .webm or Saved/. Close the editor before builds, -nosound always,
  check Docs/BossCombatReview/Execution/ENGINE_LOCK.json and no UnrealEditor process before any launch; keep raw log + sha256 + pre/post state.
- Build + full suite: copy Docs/BossCombatReview/Execution/Claude/B_C834_SNAPSHOT/run_build218.ps1 into a new B_<id>/run_build2xx.ps1,
  retitle the header, run in background; status.txt says success/fail counts.
- Live runs: Docs/BossCombatReview/Execution/Claude/run_editor_script.ps1 (-NullRhi 0 -PyCmd 1 for PIE) with the wrapper
  Scripts/Editor/run_a5_parity_driver_and_quit.py (A5_PARITY_DRIVER env, ALLOWED table); parity pairs via
  Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/run_parity.ps1 (-Only <drivers> -BuildId BUILD-2xx -Suffix _x).
  Data route = env H019_ENCOUNTER_DEFINITION=/Game/OneBossFight/Data/DA_Sevarog_G044_Encounter.DA_Sevarog_G044_Encounter.
- Queue pattern: 5-task batches, one post per batch, roll at task 90 (Queue W), hotfix first (C-829), no churn (C-820),
  C-871 compile checklist, C-883 file safety (never delete untracked files), new data fields OPTIONAL with today's defaults.
- Owner decisions: J049 = A (Blueprint setter is a Shipping route; CVar and -RPGBenchmark selectors stay non-Shipping);
  A7 = B (retire legacy startup LATER, after gates); performance UN-PARKED (DLSS + cvar experiments approved; look-changing
  asset edits and Tier 2 art need the owner's yes); art started (Tier 1 created, Tier 2 waits for owner review).

STATE AT HANDOVER (superseded by C-924 below)
- Build: BUILD-228 GREEN 476/476 (baseline 476). Committed by Antigravity as 6637ea8 (pushed state: check git status/log).
- Working tree at this handover: Codex X-1287 (C-922 T1 receipt-label fix + C-921 P2a Development benchmark telemetry) was pending review.
- Mailbox: last lead post C-923 (Queue V). The 10-minute mailbox cron is PAUSED; re-arm it only if the owner asks
  (CronCreate, prompt "Mailbox check (lead): ...").
- Done today: A5 parity on all 31 drivers (legacy vs data route), D1 component parity, D2/D5 data values (G044 manifest f7c6610d,
  audit 214 MATCH / 0 MISMATCH / 210 player INERT), T1 tracker tick prerequisites, H8 rebind waits for delayed possession
  (KI-187 closed), F1 parry slow motion (perfect 0.30x for 0.35 s, cooldown 0.60 s; witnessed live on both routes, pie_legend L8),
  W1 optional Tier 1 Niagara refs (rpg.Art.Tier1 Development preview), DLSS 4.5 SR plugin installed at ENGINE level
  (Engine/Plugins/Marketplace/DLSS + StreamlineNGXCommon, not in git) and enabled in the uproject.
- Performance at original handover (superseded by C-924 below): Round 4 (RTX 3060): legacy 27.29 fps, data route 27.10 fps (A7 regression gate PASS). Round 5 DLSS: TSR 28.6 fps,
  DLAA 21.0, Quality 32.6, Balanced 36.4, Performance 38.1; DLSS active NOT proven (the "Creating NGX DLSS Feature" line is likely
  Verbose). Round 6 (C-921): P2a telemetry proves the active upscaler; experiments = best DLSS + rpg.Perf.FireShadows 4/0,
  rpg.Perf.FireRadiusScale 0.65, r.SkyLight.RealTimeReflectionCapture 0. r.VolumetricCloud.ViewRaySampleCountScale does NOT exist.
  The owner runs benchmarks on a separate PC with its own Claude: build a kit (Scripts/MakeBenchKit.ps1 -OutDir C:/BenchTransfer/R6
  -IncludeDevelopment -Zip) with the Round 6 prompt in Documentation/BENCHKIT_README.md; results come back as bench_results_*.zip.
- Open issues: KI-186 (PROJECT_STATE partial recovery), KI-188 (40 untracked archive docs lost; .gitignore fixed), memory watch
  item (+110-150 MB Editor private bytes over 20 resets; 50-reset GC soak pending), Round 6, A7-B gates (Shipping setter proof
  waits for a real caller; no Blueprint calls SetSelectedDefinition today), Tier 2 art owner review.
- Lessons to keep: Codex's unbuilt C++ often has small compile defects (includes, names, access, captures, #endif) — expect to
  fix them; Codex sometimes skips hotfix orders — check its "NEXT" line against open hotfixes; never trust a cvar or log line
  without seeing it in a real log; verify every agent claim against raw files before accepting.
```

## State update after C-924 (2026-11-05)

- X-1287/V-C001 accepted after BUILD-229 GREEN 476/476; Lead fixed two UE 5.5.4 API assumptions in `RPGBenchmarkRunner.cpp`. Do not revert those fixes.
- `effective_primary_screen_percentage` is the family screen-percentage interface's primary fraction upper bound, not a rendered-rectangle measurement. Preflight must verify `r.DynamicRes.OperationMode=0`; the upper bound equals active fraction with dynamic resolution disabled.
- Real-run telemetry is still unwitnessed. First Round 6 kit run must confirm `temporal_upscaler`, `effective_primary_screen_percentage`, and `anti_aliasing_method` in each summary before proceeding.
- The `pie_legend` legacy receipt is written; the data-route arm and comparison remain in progress. Antigravity's Round 6 kit build is unblocked. Continue Queue V in five-task batches without waiting for review; hotfix first.
