# Pack melee parry driver source audit (Queue D31)

Scope: read-only trace from native parry input/tag support to pack melee impact handling, and inspect retained driver source for a safe reusable real-arena proof route. No asset readback, driver execution, Editor, build, or tests.

## Source route

- `URPGPlayerParry::TryBind` binds `IA_Parry` Started to `Press` after finding the pawn's Enhanced Input component (`Source/OneBossFight/Player/RPGPlayerParry.cpp:45-60`). A successful press opens the native timed window and invokes `SetParryTag(true)` (`:82-96,179-200`). The pack's `ParryFramesNS` also sets `Status.ParryActive`, as recorded in the component contract (`RPGPlayerParry.h:55-59`).
- The native damage resolver can prove only its own branch: it asks the parry component after health/life/generation/duplicate/invulnerability checks (`RPGDamageResolver.cpp:141-154`) and emits `Parried` without health damage (`:175-185`). The pack boss's weapon trace/impact state machine is Blueprint-owned and is not traced by this native resolver.
- `RPGBossDamage::HurtPlayer` is a reflected pack attribute mutation path, not evidence that a pack melee impact entered `SM_ImpactDecision` (`Source/OneBossFight/Player/RPGBossDamage.h:46-66`). Tag presence alone also proves plumbing only, not the pack's response branch.

## Existing driver/source audit

- The retained `Scripts/Editor/pie_sevarog_pack.py` describes a pack demo-level run, but its `finish` routine ends PIE and its module documentation warns it deletes the boss actor from the editor level. It is not a real-arena parry driver and lacks owned-actor cleanup, a paired no-parry control, and per-contact health/tag/result capture (`Scripts/Editor/pie_sevarog_pack.py:1-5,101-109`; inspect remainder before any reuse).
- BUILD-152's retained parry run is named `pie_parry5_pack_tag`, but its raw log loads `L_SevarogFrameworkProofCOM`, uses a framework proof boss and its `rpg.BossProofPlayerGuard` hook. It demonstrates native input/tag plumbing; it does not witness the pack boss's own melee response (`Documentation/TEST_PLAN.md:512`; `Documentation/Boss/PACK_BOSS_ARENA_PARRY_DRIVER_CONTRACT_D16.md`).
- No maintained source driver was found that loads `L_SevarogArena`, identifies the pack boss melee contact, schedules a real `IA_Parry` at that contact, captures before/after health and response, and cleans up only run-owned actors/state. The exact impact Blueprint branch and appropriate response token remain a reflected/runtime evidence requirement.

## Driver hooks required / blockers

For a new driver, require: verified `L_SevarogArena` and actual pack boss/player/style; contact identity and time from the pack's own weapon/impact path; real bound input action; simultaneous tag readback and pack response; per-contact player health/stamina readback; paired damaging no-parry control from a reset baseline; captured pre-run hook/CVar state; owned cleanup and unique raw evidence. If any of these cannot be read back, label setup/contact inconclusive. Do not reuse broad cleanup from `pie_sevarog_pack.py` or substitute framework-resolver outcomes. D16's no-run contract remains the detailed acceptance sheet; this audit adds no new runtime claim.
