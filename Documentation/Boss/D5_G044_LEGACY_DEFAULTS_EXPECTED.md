# D5 G044 legacy-default audit and correction sheet

Status: Claude completed the backed-up Lead-run Editor correction; Codex made no asset writes. The offline source audit is refreshed against the current manifest.

## Audit inputs and coverage

- Manifest: `Saved/G044/encounter_manifest.json` (boss and player definitions; source manifest hash recorded by the audit report).
- Checked-in legacy defaults: `Scripts/Tools/legacy_defaults_g044.json`. Each comparable value has a source file, exact line, and copied source excerpt. Source excerpts are checked at runtime by the audit tool; stale citations refuse the audit.
- Tool: `Scripts/Tools/compare_manifest_to_legacy_defaults.py`. It walks every scalar leaf in the typed runtime configuration groups, including phase records, statistics and policies, and requires exactly one source-cited rule per leaf.
- Current offline census: 424 typed leaves; 214 MATCH, 0 MISMATCH, 210 NOT-COMPARABLE. NOT-COMPARABLE means the effective legacy value is not established by available source evidence; it is not a parity pass.
- Full row-by-row census and reasons: `Documentation/Boss/D5_G044_LEGACY_DEFAULT_AUDIT.md`.

## Fields corrected in the backed-up Lead run

The values below come from the corresponding native runtime declarations. File and line are also embedded in the checked-in table and verified by the tool.

| Manifest path | Current draft | Legacy default | Source |
|---|---:|---:|---|
| `definitions.boss.death.blend_in_seconds` | 0.2 | 0.1 | `Source/OneBossFight/Player/RPGBossDeath.h:85` |
| `definitions.boss.death.dying_seconds` | 1.0 | 2.5 | `Source/OneBossFight/Player/RPGBossDeath.h:82` |
| `definitions.boss.death.death_mode` | `PackMontage` | `OwnClip` | `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp:769` |
| `definitions.boss.death.guard_pack_death` | true | false | `Source/OneBossFight/Player/RPGBossDeath.h:93` |
| `definitions.boss.death.hold_at_seconds` | 0.5 | 3.0 | `Source/OneBossFight/Player/RPGBossDeath.h:78` |
| `definitions.boss.death.max_clip_restarts` | 0 | 8 | `Source/OneBossFight/Player/RPGBossDeath.h:89` |
| `definitions.boss.death.pack_death_ability_class_name` | `GA_GS_Boss_Death_C` | `GA_EnemyRagdollDeath_C` | `Source/OneBossFight/Player/RPGBossDeath.h:63` |
| `definitions.boss.death.pack_end_time_multiplier` | 1.0 | 0.0 | `Source/OneBossFight/Player/RPGBossDeath.h:74` |
| `definitions.boss.death.pack_poll_seconds` | 0.1 | 1.0 | `Source/OneBossFight/Player/RPGBossDeath.h:70` |
| `definitions.boss.phases[PhaseTwo].entry_health_fraction` | 0.5 | 0.6 | `Source/OneBossFight/Player/RPGBossPhases.h:31` |
| `definitions.boss.phases[PhaseTwo].rate_multiplier` | 1.1 | 1.2 | `Source/OneBossFight/Player/RPGBossPhases.h:58` |
| `definitions.boss.phases[PhaseTwo].speed_multiplier` | 1.15 | 1.2 | `Source/OneBossFight/Player/RPGBossPhases.h:55` |
| `definitions.boss.stats.max_posture` | 120.0 | 100.0 | `Source/OneBossFight/Player/RPGBossPosture.h:31` |
| `definitions.boss.stats.posture_regen_delay` | 3.0 | 6.0 | `Source/OneBossFight/Player/RPGBossPosture.h:35` |
| `definitions.boss.stats.posture_regen_rate` | 15.0 | 13.0 | `Source/OneBossFight/Player/RPGBossPosture.h:39` |

Claude reports the run wrote 15 fields; boss package hash changed from `806d8747...` to `7d2c3052...`, player package stayed `30cdd6b0...`, selection hash changed from `adf5f68b...` to `8d0c5a6f...`, and manifest hash changed from `4bcf1a63...` to `f7c6610d...`. Four package/receipt backups are recorded under `Saved/G044/backups/C850_D5_395c4dc8.../`. `validate_encounter_manifest` passed; the 424-field comparator reported 87 MATCH, 0 MISMATCH, 337 NOT-COMPARABLE at that run. The current table additionally resolves 100 boss attack-tracker leaves, all 25 previously unknown boss constructor-backed asset references, and the two boss fireball cooldown endpoints. These all match source.

## Not-comparable boundary

All 210 current NOT-COMPARABLE leaves belong to the player definition. The audit tool and generated census classify each as `INERT` on the selected route, with source-checked evidence: selection assigns `TargetOnly` (`RPGEncounterSelectionSubsystem.cpp:245`), preflight says that role has no BossCore plan (`RPGBossHydrationPreflight.cpp:368, 513-515`), and actor component configuration iterates only supplied plans (`RPGEncounterBinding.cpp:419`). The player definition is compiled/validated and its values copied into a config snapshot, but those boss-feature values are not applied to the player actor. The 100 tracker leaves also have no player `URPGAttackTracker`. Therefore a Blueprint property read would inventory serialized values but would not establish a legacy runtime counterpart for these fields; keep them NOT-COMPARABLE unless the role/schema contract changes. Every boss definition leaf has a source-backed comparable value and matches. No Blueprint value is inferred.

D2 health is a MATCH at 2000 HP. Claude reports the backed-up correction and refreshed manifest validation passed. The current source audit reports 214 MATCH, zero MISMATCH, and 210 NOT-COMPARABLE. Codex did not run the Editor, save assets, build, commit, or push.
