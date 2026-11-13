# BN-06..10: manual check of the heuristic-O KIs (lane BN, batch 2 of 10, per X-2213)

C (implementer), 2026-11-12.

**Not done:** no code, asset, engine, build, PIE or test work. No KNOWN_ISSUES status changes and no commits.

| Task | KI | Row | Evidence checked | Manual class | Offline follow-up? |
|---|---|---|---|---|---|
| BN-06 | KI-002 | `KNOWN_ISSUES.md:73`: about 68 C4996 deprecation warnings come from engine headers. The action is "Ignore; not project code" | The action is a standing acceptance. Recounting the warnings needs a build | **L** (accepted limit) | No |
| BN-07 | KI-009 | `:76`: Greystone's pack AnimBP casts to its Paragon Blueprint. Montages play only through `UpperBody`, or through `FullBody` while the curve is active and the character is not accelerating. The action is "Own AnimBP in the polish milestone" | The fix is authoring an AnimBP asset, an Editor task. A Greystone child route exists, but `rpg.GreystonePlayerTestPawn` is Development-only and defaults to `0` (`RPGPlayerMovesSubsystem.cpp:107-109`); `Config/DefaultEngine.ini:4-6` still selects the pack game mode/map, and `SWITCH_PLAN.md` says the mannequin remains active until the switch gates and owner approval. So the Greystone route is not the active default and the row is not obsolete | **E** (asset authoring in the Editor) | No (asset work) |
| BN-08 | KI-016 | `:83`: the phase roar uses `Ultimate_Targeting` as a stand-in | It is still referenced in `Scripts/Editor/setup_m4_content.py`, `probe_sevarog_animations.py`, `sevarog_pack_05_parity.py` and `Tests/RPGFrameworkRuntimeTests.cpp`. Replacing it needs a new animation asset ("if one is found"), which is art/content work | **E** (content) + D (art is parked) | No |
| BN-09 | KI-020 | `:87`: gamepad input (B dodge, LB block, sticks, mouse gating) could not be tested; the keyboard was tested with real key events | Needs a physical controller playtest | **E** (playtest) | No |
| BN-10 | KI-022 | `:89`: gamepad menu focus and the Settings sliders are untested; Escape stops Play in the editor (use P) | Needs a controller playtest. The Escape note is editor behaviour | **E** (playtest) + L (editor note) | No |

**Batch 2 result:** 0 of 5 are true O. Running total: 0 O out of 9 KIs checked.

**Limits:** row and grep reads only. Ownership of the animation assets was not opened in the Editor.
