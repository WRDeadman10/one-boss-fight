# BC-A01..A05 & BC-A06..A10 Status (`QUEUE_BC_AG` Unblock Order per `[C-1271]`)

**Queue Authority:** [`Documentation/Boss/QUEUE_BC_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BC_AG.md), `[C-1271]` (`2026-11-10 18:18`)  
**Check Timestamp:** `2026-11-10 18:25`  

| Task IDs | Title | Current Status | Blocker / Next Unblock Trigger |
|---|---|---|---|
| `BC-A01..A02` | `URPGMontageWrapperLibrary::CreateRetargetWrapper` contract & review | **`COMPLETE`** | Unblocked by `[X-1821]` (`C1269_GREYSTONE_WRAPPER`, `503/503` PASS); verified in `BC_A01_A02_MONTAGE_WRAPPER_VERIFY.md` + `test_bc_a01_montage_wrapper_contract.py` (`3/3 OK`). |
| `BC-A03` | Inspect `Saved/BossCombatReview/bb_a15_greystone_materials_probe.json` | **`BLOCKED`** | `Saved/BossCombatReview/bb_a15_greystone_materials_probe.json` absent; `[C-1270]` deferred Lead `BB-A15` run until `BP_GreystoneERPlayer` exists (`--write` next per `[X-1821]`). |
| `BC-A04` | Local commit of `BB-A45..A50` deliverables | **`COMPLETE`** | Committed in `58ae0739` (`BB-A46..A50`, `3` files, `0` media, `0` push). |
| `BC-A05` | Sync `BB-A09..A10` Stun/Intro/Death capture status | **`COMPLETE (BLOCKED on Lead captures)`** | `D:/FightVideo/sevarog_frames/_sheets/` still contains only the 8 original combat sheets (`Soul_Siphon`, `Speedburst`, `Subjugation`, `Swing1_FAST_v2`, `Swing1_Medium`, `Swing2_Medium`, `Swing3_Slow`, `Ultimate_Swing_120fps`); `[C-1271]`/`[C-1273]` Lead capture queued next. |
| `BC-A06..A09` | `C-1265b` full-clip trace cross-check & window validator test | **`COMPLETE`** | Unblocked by `[X-1821]` (`C1269_X03_TRACE`); cross-checked in `BC_A06_A09_SEVAROG_X03_TRACE_CROSSCHECK.md` (flagged `Swing2` `37.022 cm` @ `0.229 s` + `Swing1` `0.247 s` active-window tick gap) + `test_bc_a09_sevarog_window_bounds_contract.py` (`2/2 OK`). |
| `BC-A10` | Frame-cite Stun / Intro / Death sheets | **`BLOCKED`** | Awaiting Lead capture completion (`[C-1271]`, `[C-1273]`). |
| `BC-A11..A15` | Sevarog signature cards (`S6..S8`) data prep & module gap matrix | **`COMPLETE`** | `BC_A11_A15_SEVAROG_SIGNATURE_CARDS_DRAFT.md` + `test_bc_a14_sevarog_signature_cards_contract.py` (`3/3 OK`), committed `56cd329c`. |
