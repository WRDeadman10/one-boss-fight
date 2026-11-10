# BC-A01..A05 & BC-A06..A10 Status (`QUEUE_BC_AG` Unblock Order per `[C-1271]`)

**Queue Authority:** [`Documentation/Boss/QUEUE_BC_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BC_AG.md), `[C-1271]` (`2026-11-10 18:18`)  
**Check Timestamp:** `2026-11-10 18:25`  

| Task IDs | Title | Current Status | Blocker / Next Unblock Trigger |
|---|---|---|---|
| `BC-A01..A02` | `URPGMontageWrapperLibrary::CreateRetargetWrapper` contract & review | **`BLOCKED`** | `Source/OneBossFightEditor/{Public,Private}/RPGMontageWrapperLibrary.*` present in-flight on disk, but Codex has not posted `C-1269a` READY in `TEAM_MAILBOX.md` (`[C-1272]` lock/run in progress). |
| `BC-A03` | Inspect `Saved/BossCombatReview/bb_a15_greystone_materials_probe.json` | **`BLOCKED`** | `Saved/BossCombatReview/bb_a15_greystone_materials_probe.json` absent; `[C-1270]` deferred Lead `BB-A15` run until `BP_GreystoneERPlayer` exists. |
| `BC-A04` | Local commit of `BB-A45..A50` deliverables | **`COMPLETE`** | Committed in `58ae0739` (`BB-A46..A50`, `3` files, `0` media, `0` push). |
| `BC-A05` | Sync `BB-A09..A10` Stun/Intro/Death capture status | **`COMPLETE (BLOCKED on Lead captures)`** | `D:/FightVideo/sevarog_frames/_sheets/` still contains only the 8 original combat sheets (`Soul_Siphon`, `Speedburst`, `Subjugation`, `Swing1_FAST_v2`, `Swing1_Medium`, `Swing2_Medium`, `Swing3_Slow`, `Ultimate_Swing_120fps`); `[C-1271]` notes Lead capture started for `Stun_Start`/`Loop`/`End`/`LevelStart`/`Death_front`. |
| `BC-A06..A09` | `C-1265b` full-clip trace cross-check & window validator test | **`BLOCKED`** | `Docs/BossCombatReview/Execution/Claude/C1265B_CLIP_TRACE/pie_clip_trace.log` holds only try-1 (`FRAMES=0`); awaiting Codex `X03` trace self-test & log. |
| `BC-A10` | Frame-cite Stun / Intro / Death sheets | **`BLOCKED`** | Awaiting Lead capture completion (`[C-1271]`). |
| `BC-A11..A15` | Sevarog signature cards (`S6..S8`) data prep & module gap matrix | **`IN PROGRESS / UNBLOCKED`** | Executed immediately per `[C-1271]` unblock order. |
