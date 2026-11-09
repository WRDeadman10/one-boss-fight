# Queue AW — default-off camera options and G044 move-selection readback

**Authority:** Claude C-1128. Work is offline/source-only. Do not run Unreal, edit assets, or inspect an in-flight Lead folder. B and C remain false by default; no owner camera choice is inferred. Batch 2 is an independent source audit of the open KI-037/KI-066 gates while Lead review proceeds. Subsequent batches are selected from open KIs without waiting for review. The G044 exporter remains Lead-owned.

## Batch 1 — config-safe camera B+C and G044 source export

| Task | Work | Acceptance |
|---|---|---|
| AW-C01 | Add test-first source contracts for config-driven HideBossInside and LockOnFraming defaults and override precedence. | Contracts fail before implementation and pass afterward; both config defaults remain false. |
| AW-C02 | Add `UPROPERTY(Config)` booleans `bDefaultHideBossInside` and `bDefaultLockOnFraming` to `URPGCameraRig`, with a Game config section. | Native and project config defaults are false; no existing camera behavior changes unless explicitly enabled. |
| AW-C03 | Move only B/C runtime logic needed by config out of the non-Shipping guard; retain dev-only CVars as tri-state overrides. | In Shipping, config values work without CVar references; in Development, `-1` uses config, `0` disables, and `1` enables. BossBlocks and debug CVars remain non-Shipping. |
| AW-C04 | Author a read-only Editor Python exporter following the selected G044 encounter to its boss definition. Export tracker records, A4 row(s), branch range/cone, low-sweep record, phase records, and selected initial phase. | Missing/wrong-class references refuse; output is one exclusive JSON file under Saved/G044; script does not mutate/save assets and states that serialized values do not prove runtime selection. |
| AW-C05 | Update this queue and the camera/KI handoffs with exact code/test limits and the Lead run command for the exporter. | Lead receives a concise readback request; A4 phase/range gating stays unknown until the JSON output is inspected against witnessed runtime evidence. |

## Current implementation state

AW-C01–C05 are complete offline. The config controls and tri-state overrides are implemented; the read-only G044 exporter and handoff are authored. Focused contracts pass 36/36 and Python syntax compilation passes. C++ compilation, Shipping symbol verification, and running `export_g044_move_selection_readonly.py` are Lead-owned. The exporter output has not been produced, and no G044 asset was opened or modified by Codex.

## Batch 2 — independent config and Shipping source audit

| Task | Work | Acceptance |
|---|---|---|
| AW-C06 | Recheck native and project config defaults for B/C. | Both remain false. |
| AW-C07 | Audit Development override precedence. | `-1=config`, `0=off`, positive=on; Shipping follows config. |
| AW-C08 | Inspect CVar isolation and Shipping-capable B/C path. | CVar declarations/reads remain guarded; config application remains compiled. |
| AW-C09 | Audit option cleanup boundaries from existing contracts/source. | Disable, missing target/controller and EndPlay restore owned state. |
| AW-C10 | Reconcile source comments and handoff limits. | No stale “non-Shipping” label for B/C; no runtime/owner claim added. |

**Progress:** AW-C06–C10 complete. Camera contracts 40/40; syntax and scoped diff-check pass. No native build, Shipping build, Unreal, PIE or exporter run. Details: `AW_C06_C10_CAMERA_CONFIG_SOURCE_AUDIT.md`.

## Lead commands

Build and native test review remain with Claude. To obtain the serialized G044 readback, Claude can run the script under the project Editor with its normal `-ExecutePythonScript` command line:

```powershell
& 'C:/Program Files/Epic Games/UE_5.5/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' 'C:/UnrealProject/OneBossFight/OneBossFight.uproject' '-ExecutePythonScript=C:/UnrealProject/OneBossFight/Scripts/Editor/export_g044_move_selection_readonly.py' -nosound -unattended -NoSplash
```

The script only loads assets and writes a unique JSON readback below `Saved/G044`; run it after confirming the Editor lock permits it. It does not save packages. A4 runtime selection, phase/range gating, and successful natural appearance remain separate questions.
