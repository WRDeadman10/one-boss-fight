# I001 — typed definition source map

**Scope:** identify the existing proof boss and pack player inputs for a future selected-route definition without inferring authored values from class names or unrelated framework profiles.

## Verified content identities

| Role | Verified package/class | What this establishes |
|---|---|---|
| Pack boss | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C` | The Blueprint package exists under `Content/AdvancedARPGCombat/.../BP_ExampleGreatSwordBoss.uasset`. The current startup census recognizes this class by name (`RPGPlayerMovesSubsystem.cpp`, `IsPackBoss`). |
| Pack player | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C` | The Blueprint package exists under `Content/AdvancedARPGCombat/.../BP_CombatPlayerCharacter.uasset`; existing editor tooling loads this class directly (for example `Docs/BossCombatReview/Execution/Claude/B_AWR005/create_vertical_content.py`). This is the pack player class, not proof of a separate Greystone class. |
| Sevarog framework proof profile | `/Game/OneBossFight/FrameworkProof/DA_Sevarog_SwingProof.DA_Sevarog_SwingProof` (and `_F4` variant) | These are framework boss profiles used by framework proof fixtures. Their existence does not establish that their values match the Advanced ARPG pack boss Blueprint's reflected components. |

The first two content package paths are verified from the `.uasset` files on disk. Their generated-class names and the class-name census are also cited by the source/scripts above. No Unreal asset readback was run for this task.

## Typed schema and source boundary

`Source/OneBossFight/Player/RPGEncounterBinding.h:293-310` defines `URPGBossDefinition`: schema, IDs, stats, encounter/stagger/phase policy, optional abilities, pack bindings, phases, skeleton, animations, and provenance `Fields`. `URPGBossEncounterDefinition.h:11-29` defines the separate selection record that references one boss definition and one player definition. The selection record is not itself a definition of either Blueprint.

The current `_G044` selection script requires each definition to provide a nonempty `Fields` manifest, a resolvable skeleton, at least one animation, and (for the boss) `PhaseOne`. These are pre-save/readback conditions, not evidence that values were extracted from the two pack Blueprints.

## Existing pack readback (historical, not refreshed in this task)

`Documentation/Archive/DELTA_AUDIT.md:9-20` records Claude's 2026-10-20 Editor readback: both pack characters use mesh `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin_Simple`, skeleton `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SK_CombatMannequin`, and skeleton size 111 × 42 × 181 cm. The boss mesh scale is 1.5, offset Z -142, capsule radius 63 cm / half-height 144 cm; player mesh scale 1, capsule radius 42 cm / half-height 96 cm. Those physical values are sourced to that historical Editor readback, not inferred from C++ defaults.

The same readback (`DELTA_AUDIT.md:30-42`) names available boss animations: `GS_Attack01_Montage`, `GS_Attack02_Montage`, `GS_Attack03_Montage`, `GS_Attack04_Montage`, `GS_ChargedAttack_Montage`, `GS_LeapAttack_Montage`, `GS_SprintAttackFollowUp_Montage`, `KnockdownStart_Anim_Montage`, `Knockdown_Getup_Anim_Montage`, and `Ability_R_Intro_Anim_Montage`. It says these assets use the shared mannequin skeleton. It does not specify which are consumed by every `URPGBossDefinition` config or give a player animation list.

`PhaseOne` in `create_g044_encounter_definition.py` is currently a script constant, not proof that the pack boss's selected source has a matching serialized phase. The phase identity and its exact values still require a fresh Editor readback from the production source chosen for the definition.

## Authoring disposition

No fresh Sevarog pack-boss component/property snapshot or Greystone/pack-player animation set was created for this task. The 2026-10-20 readback provides the shared skeleton and physical dimensions, but not a complete `URPGBossDefinition` field mapping. `DA_Sevarog_SwingProof` is not a substitute for the pack boss CDO, and the `BP_CombatPlayerCharacter` package name does not identify a separate Greystone subclass. Consequently, I001 identifies asset roots, selected historical values and schema while leaving the rest **UNREAD / requires current Editor readback**. The I002/I003 scripts must require an explicit readback/spec receipt with per-field source paths and refuse creation while any required field is missing; they must not copy code defaults or invent a Greystone identity.

## Relevant source references

- `Source/OneBossFight/Player/RPGEncounterBinding.h:293-310` — typed definition fields.
- `Source/OneBossFight/Player/RPGBossEncounterDefinition.h:11-29` — selection record and definition references.
- `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:139-145` — runtime pack boss/player class recognition by class name.
- `Documentation/Archive/DELTA_AUDIT.md:9-20,30-42` — dated Editor readback for classes, mesh/skeleton, scale/capsule and available boss animation assets.
- `Docs/BossCombatReview/Execution/Claude/B_AWR005/create_vertical_content.py:73` — existing tool's pack player generated class path.
- `Scripts/Editor/create_g044_encounter_definition.py:40-65` — definition prerequisites checked before G044 selection asset creation.
