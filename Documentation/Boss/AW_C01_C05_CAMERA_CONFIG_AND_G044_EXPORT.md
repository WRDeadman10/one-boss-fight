# AW-C01–C05 — camera config options and G044 readback

## Delivered

- `URPGCameraRig` now exposes `bDefaultHideBossInside` and `bDefaultLockOnFraming` as `UPROPERTY(Config)` settings. Native and `DefaultGame.ini` defaults are false, preserving current behavior until explicitly enabled.
- Development CVars for B/C are tri-state overrides: `-1` follows config, `0` disables, and `1` enables. Their declarations and references remain under `!UE_BUILD_SHIPPING`; only the option logic required to honor config is compiled in Shipping. BossBlocks and camera-debug behavior remain Development-only.
- `Scripts/Editor/export_g044_move_selection_readonly.py` follows the configured G044 encounter to the boss definition and exports serialized tracker records, A4 rows, branch range/cone, LowSweep, phase records, and selected initial phase. It refuses missing/wrong-class/unresolved assets and writes one exclusive timestamped JSON file beneath `Saved/G044`. It does not modify or save asset packages.
- The export explicitly states that serialized definition fields do not prove runtime selection. The AttackTracker record has no per-move phase/range fields; branch range is reported separately, so no A4 phase/range gate is inferred.

## Verification and limits

- Test-first source contracts passed: camera config/exporter contracts plus existing camera hide, lock-on, independence and passive-probe contracts, **36/36**.
- Python syntax compilation passed for the exporter and two new contract modules.
- No Unreal Editor, native build, PIE, asset load, or G044 export was run by Codex. The C++ Shipping compile and actual G044 JSON readback remain Lead-owned.
- No final owner choice for B/C or camera behavior is claimed. Defaults remain false. KI-037/KI-066 and the visual/package gates remain open.

Lead command and the exact verification boundary are in `Documentation/Boss/QUEUE_AW.md`.
