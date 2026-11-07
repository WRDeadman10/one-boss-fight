# X1 - ER block probe v4

## Prior evidence reviewed

The three Lead runs are in `Docs/BossCombatReview/Execution/Claude/ER_INPUT_DUMP/probe1..3/editor_raw.log`. Probe 1 enters its guard phase with player health/stamina at 0 (`probe1/editor_raw.log:1872-1873`). Probe 2 reports no player montage at guard start and health -36/stamina 0 at its first sample (`probe2/editor_raw.log:1883-1884`). Probe 3 also reports `montage seen: None` while its separate `boss_montage` field later shows `GS_EquipWeapon_Montage` (`probe3/editor_raw.log:1877-1886`). These observations show the prior output did not establish player weapon draw at test start; they do not establish why blocking was absent.

The input dump confirms `IA_ToggleCombat <- R` and `IA_Block <- Gamepad_LeftShoulder` (`run1/editor_raw.log:1290-1297`). `URPGInputTestUtils.InjectAction` injects an action for one frame, so the driver calls it on every tick during its direct-action arm (`RPGInputTestUtils.h:22-23`, `.cpp:23-35`).

## v4 changes

`Scripts/Editor/pie_er_block_probe.py` now:

- Reads and reports every owned player gameplay tag, without a Block/Guard filter, whenever the tag set changes.
- Enters combat by pressing and releasing mapped key `R`, then records player montages and whether a weapon/equip montage appeared. Player and boss montages are enumerated separately across skeletal meshes.
- Runs two 15-second arms against the active arena boss: the real `Gamepad_LeftShoulder` mapping, then direct `IA_Block` injection each tick. Each arm reports the exact input path, action load/injection counts, tags, montage changes, health, and stamina.
- Calls the existing `RPGCombatDebug.debug_refill_player()` every probe tick. It stops with a clear line if the debug component is unavailable, rather than running without the requested survival control.
- Makes no gameplay-cause claim and does not set PIE component properties.

## Validation and handoff

`python -m py_compile Scripts/Editor/pie_er_block_probe.py` passed. No Unreal/PIE run was performed; Claude runs the probe and reads `[BlockProbeV4]` lines. The script is instrumentation only, and its output may establish input delivery and observed state without identifying the underlying cause.
