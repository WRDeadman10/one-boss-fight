# Pack-arena melee driver source review

Scope: static review of `pack_arena_melee_driver.py` and `run_pack_arena_driver.ps1` per Claude C-783. No Editor, PIE, build, or test run was performed.

## Safety and run ownership

- The wrapper uses the maintained `run_editor_script.ps1` lock/snapshot/log/result path with windowed Unreal (`NullRhi=0`) and `-nosound` inherited from that launcher.
- The driver loads only `/Game/OneBossFight/Levels/L_SevarogArena`, checks the editor world's package, requires an actual `BP_SevarogBossPack_C` and the possessed pawn, and logs actor class/name/location plus style and health/stamina values.
- The script does not spawn, destroy, or save actors/assets. It owns one Slate tick callback, requests normal PIE end, unregisters the callback, and quits the editor. The wrapper stores run parameters in a task-owned config file; each raw run is written to a unique `OutDir`.
- `control` mode sends no defense input. `block` mode injects `IA_Block`; `parry` mode injects `IA_Parry` at a caller-supplied offset after an observed boss montage starts. The driver records native parry-window and best-effort `Status.Blocking` state. Parry mode requires the `LogRPGParry` IA_Parry binding line; IA_Block binding remains UNKNOWN until runtime effect evidence.

## Evidence boundary

This is a bounded probe collector, not a pass/fail classifier for the pack Blueprint. It records montage transitions/positions, parry-window state, player health/stamina samples, and health deltas. D31/D32 require the exact pack weapon-trace contact identity and `SM_ImpactDecision` response at that same contact. Those Blueprint event tokens are still UNKNOWN in the source audit. A health delta or unchanged health sample alone is only a candidate observation, never a valid control/parry row. Lead must inspect the raw log and reflected/runtime event output; if contact identity and pack response are absent, record INCONCLUSIVE and do not claim BOSS-COM-004/HIT-008 closure.

## Static review result

- Python syntax parses; path and mode bounds are explicit; input action asset load failure is fatal to the run.
- The pairing requires separate fresh PIE runs (`control` and `parry`) from the same saved arena start. Keep the chosen parry offset and control baseline in the run artifacts.
- No execution validation was performed, so Unreal Python API exposure, actor discovery, map package naming, and timing remain Lead-owned preflight checks.
