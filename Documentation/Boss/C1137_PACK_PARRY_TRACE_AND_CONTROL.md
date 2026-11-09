# C-1137 pack parry trace and no-parry control

Date: 2026-11-09  
Scope: static native-source trace plus an offline-tested, opt-in comparison-driver mode. No pack asset inspection, Unreal/Editor/build/PIE, or gameplay Source change was performed.

## Static trace result

- The player component opens the native parry timer and mirrors it into the player's `Status.ParryActive` gameplay tag on successful press (`Source/OneBossFight/Player/RPGPlayerParry.cpp:100-105,224-235`). The component contract says the pack's `SM_ImpactDecision` reads this tag, and that pack `GA_PlayerParry` cancels block (`Source/OneBossFight/Player/RPGPlayerParry.h:12-15,73-74`). This establishes the intended tag bridge, not the exact Blueprint decision branch or that it is reached for each named montage.
- `URPGDamageResolver::Resolve` checks health/life/generation/duplicate/invulnerability, then asks `URPGPlayerParry::IsParrying` (the native timer, not the tag) (`Source/OneBossFight/Player/RPGDamageResolver.cpp:142-160`). Only its `Parried` outcome spends the resolver hit key and calls `NotifyParried` (`:187-190`). `NotifyParried` increments `ParriedCount` and stores the grade (`Source/OneBossFight/Player/RPGPlayerParry.cpp:143-151`).
- Native documentation explicitly limits that resolver to project-authored A4/A5/A6 geometry and says pack weapon traces (A1/A2 stand-in/A3) reject at the pack trace instead (`Source/OneBossFight/Player/RPGDamageResolver.h:118-122`). The resolver is installed on a pack boss as a component (`Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:808-813`), but installation alone is not a call path from its Blueprint weapon trace. The project audit also separates pack A1/A3 impact handling from this resolver (`Documentation/Boss/PLAYER_DAMAGE_IMMUNITY_OVERLAP_AUDIT_D28.md:30`; `Documentation/Boss/PACK_MELEE_PARRY_DRIVER_SOURCE_AUDIT_D31.md:7-9`).
- Therefore static native source does **not** prove that the tag causes pack montage damage to be dropped, nor prove that Mid01/A1b/A3x/A2 contacts enter or bypass the resolver. Exact Blueprint `SM_ImpactDecision` checks and runtime contact/response evidence are outside the available native source. C-1137's suspected silent-block/no-reward behavior remains **unconfirmed**; no Source fix is justified by (a). If runtime proves damage is dropped without reward, the candidate direction is to route the confirmed pack parry event into `NotifyParried` and the boss recoil/reaction path, after Lead review; nothing is applied here.

## PARRY_ONLY_CONTROL driver mode

`PARRY_ONLY_CONTROL=1` is a separate opt-in mode, mutually exclusive with parry-only and dodge-only. It starts at 120 cm, maintains a 115–125 cm band, retreats above 125 cm, approaches below 115 cm, and repositions to 115 cm if measured distance exceeds 130 cm. It sends no parry or attack input and logs `PARRY_CONTROL_RANGE` with measured distance, action, and the explicit `press=0 attacks=0` markers. This creates a no-parry reference at a controlled close range; Lead must compare it to the parry run after reset using the same encounter/build and inspect the distance and player-HP logs. It cannot itself prove pack tag semantics.

## Verification and limits

- `python -m unittest Scripts.Editor.test_pie_full_fight_offline -q`: 39/39 passed.
- `python -m py_compile Scripts/Editor/pie_full_fight.py Scripts/Editor/test_pie_full_fight_offline.py`: passed.
- No Unreal, build, Editor, PIE, or asset inspection by Codex. No production Source behavior changed. Lead owns the paired runtime A/B and any subsequent verdict.
