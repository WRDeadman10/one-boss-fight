# Sevarog Montage Inventory & Audit Plan (C-1177 Phase 2 Step 4)

**Document Version:** 1.0  
**Authority:** Claude Lead Directive `[C-1236]` (2026-11-10).  
**Owner:** Antigravity (`Art/Review/Audit`).  
**Status:** PROPOSED PLAN (Read-Only; Zero Asset Mutations; Zero Runtime Wiring).  
**Scope:** Specification of Sevarog animation assets to probe under `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/` in support of future `URPGANS_BossMoveTiming` cataloging.

---

## 1. Executive Summary & Objectives

Per Directive `[C-1236]`, this document drafts the read-only inventory plan for **Sevarog** combat animation assets. Following the Ember Warden (`Boss01`) notify timing audit (`C-1228` through `C-1235`), Sevarog (`Boss02` / Boss duel counterpart in `L_SevarogArena`) requires a systematic catalog of on-disk montages, sequences, section divisions, and existing anim notifies to establish exact ground-truth timings before any authoring is planned.

### Lessons Learned from Ember Warden Audit (`C-1235` / `C-1236`)
1. **Never Assume Montage Composition:** As demonstrated by `AM_Boss01_A2` (which proved to be a `0.600 s` partial raise tell rather than a `3.134 s` composite), every asset length and section count must be verified via programmatic readback, never inferred from raw sequence filenames on disk.
2. **Defensive API Probing:** All inspection scripts must wrap property and method calls in individual `try/except` guards, logging `n/a <field>` rather than failing on unexposed Python bindings in UE 5.5.
3. **Dedicated Notify Tracks:** When authoring is eventually scheduled, timings must live on clean dedicated tracks (`BossMoveTiming`) with strict pre-mutation safety checks.

---

## 2. Target Asset Catalog for Probe Execution

The Paragon Sevarog animation directory (`/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/`) contains 127 animation `.uasset` files. The probe will classify and inspect the following prioritized asset categories:

### 2.1. Category A: Existing Montages (High Priority)
Existing montage containers to be probed for sections, blend times, and notify footprints:
| Montage Asset Name | Relative Path | Anticipated Role |
| :--- | :--- | :--- |
| `Swing1_Medium_Montage` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Medium_Montage` | Primary Heavy Hammer Swing 1 |
| `Swing2_Medium_Montage` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing2_Medium_Montage` | Primary Heavy Hammer Combo Swing 2 |
| `LevelStart_Montage` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/LevelStart_Montage` | Boss Intro / Spawn Sequence |

### 2.2. Category B: Primary Melee Attack Sequences (Core Swings)
Raw attack sequences available for combat moves or montage assembly:
| Sequence Asset Name | Variant / Speed | Combat Role Candidate |
| :--- | :--- | :--- |
| `Swing1_Medium` | Medium pace | Swing 1 Standard Attack |
| `Swing1_Slow` | Slow / Heavy windup | Swing 1 Delayed Tell Variant |
| `Swing1_FAST_v2` | Fast pace | Swing 1 Quick Slash Variant |
| `Swing1_Return2Idle` | Return blend | Swing 1 Recovery / Follow-through |
| `Swing2_Medium` | Medium pace | Swing 2 Combo Link Standard |
| `Swing2_Slow` | Slow / Heavy windup | Swing 2 Delayed Tell Variant |
| `Swing2_FAST_v2` | Fast pace | Swing 2 Quick Combo Variant |
| `Swing2_Return2Idle` | Return blend | Swing 2 Recovery / Follow-through |
| `Swing3_Medium` | Medium pace | Swing 3 Combo Finisher Standard |
| `Swing3_Slow` | Slow / Heavy windup | Swing 3 Heavy Finisher Variant |
| `Swing3_FAST_v2` | Fast pace | Swing 3 Fast Finisher Variant |
| `Swing3_Return2Idle` | Return blend | Swing 3 Recovery / Follow-through |
| `Swing_In_Air` | Aerial swing | Jump Attack / Aerial Slam |

### 2.3. Category C: Signature Abilities & Specials
Unique boss attack maneuvers and spells:
| Sequence Asset Name | Mechanical Feature | Combat Role Candidate |
| :--- | :--- | :--- |
| `Ultimate_Swing_120fps` | Colossal 360-degree hammer sweep | Boss Phase Transition / Ultimate Cleave |
| `Ultimate_Targeting` | Heavy windup / charge tell | Ultimate Telegraph Window |
| `Ultimate_Targeting_Loop` | Sustained power hold | Delayed Heavy Slam Tell |
| `Subjugation` | Ground pound / summon root | Area-of-Effect Ground Snare / Root |
| `Soul_Siphon` | Spectral drain channeling | Ranged Life Drain / Tether Ability |
| `Soul_Siphon_Targeting` | Aiming / cast tell | Drain Telegraph |
| `Speedburst` | Phantom slide / dash | Rapid Gap Closer / Reposition Dash |
| `Cast` | Generic spellcast | Magic / Projectile Cast Tell |
| `Bound` | Teleport / ethereal shift | Evasive Phase Blink |

### 2.4. Category D: Reactions, Staggers & Defeat
Defensive and reaction animations essential for hit response and parry rewards:
| Sequence Asset Name | Reaction Type | Combat Role Candidate |
| :--- | :--- | :--- |
| `Hitreact_Front` | Light hit reaction | Frontal Poise Flinch |
| `Hitreact_Back` | Light hit reaction | Backstab / Rear Hit Flinch |
| `Hitreact_Left` / `Right` | Directional hit reaction | Lateral Hit Flinch |
| `Stun_Start` | Heavy stun initiation | Parry Stun / Poise Break Entry |
| `Stun_Loop` | Vulnerability window | Riposte Window Loop |
| `Stun_End` | Stun recovery | Recovery to Neutral |
| `Knock_back` / `Knock_back_bwd`| Heavy displacement | Guard Counter / Heavy Knockdown |
| `Death_front` | Defeat sequence | Boss Duel Victory Frame |

### 2.5. Category E: Soul Armor Evolution (Phase Escalation)
Visual progression sequences tied to boss health thresholds:
| Asset Name | Phase Tier | Combat Role Candidate |
| :--- | :--- | :--- |
| `Stage_1` | Baseline | Phase 1 Initial Form |
| `Stage_2` | Pauldrons & Spikes | Phase 1 Escalation |
| `Stage_3` | Full Shoulder Armor | Phase 2 Transition Candidate |
| `Stage_4` | Crown & Spikes | Enraged / Phase 2 Climax Form |

---

## 3. Probe Execution Methodology & Safe Architecture

In accordance with Directive `[C-1236]`, the forthcoming inspection script (`probe_sevarog_montages.py`) will adhere to strict safety guidelines:

1. **Guarded Field Queries:**
   - Property and method reads (`get_play_length`, `get_num_sections`, `get_section_name`) are isolated in `safe_call` wrappers.
   - If an API property is unexposed in UE 5.5, the script outputs `n/a (<reason>)` and advances without termination.
2. **Standard Notify Extraction:**
   - Notifies are retrieved exclusively via `unreal.AnimationLibrary.get_animation_notify_events(asset)`.
3. **Zero Asset Mutation:**
   - Strictly read-only; no calls to `save_asset` or `save_loaded_asset`.
4. **Execution Gate:**
   - Script will remain UNRUN until Claude Lead executes it under engine lock.

---

## 4. Next Steps
- Await Claude Lead review and approval of this asset scope.
- Following Lead approval, author `Scripts/Editor/probe_sevarog_montages.py` along with its offline contract test.
- Plan only; zero runtime wiring or asset mutation.
