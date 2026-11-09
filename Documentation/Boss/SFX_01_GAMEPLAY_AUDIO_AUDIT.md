# SFX-01: Gameplay Audio Coverage Audit & Gap Analysis

**Document Version:** 1.0  
**Authority:** Project Owner Order & Claude Directive `[C-1169]`  
**Owner:** Antigravity (`Art/Review/Audit`)  
**Scope:** Exhaustive audit of all combat, character, and environmental audio in `OneBossFight`.

---

## 1. Player Audio Coverage Table

| Gameplay Event | Current Sound Asset Path | Call Site / Trigger Mechanism | Status / Gap Analysis |
|---|---|---|---|
| **Light Attack (R1)** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Sword_Swing_Cue` | `ANS_CollisionTrace` on attack montages | Functional, standard pack whoosh. |
| **Light Attack Hit** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/SwordImpact_Cue` | `BP_ImpactSystem` on trace hit | Functional, basic flesh/metal hit. |
| **Strong Attack (R2)** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Sword_Swing_Cue` | `ANS_CollisionTrace` on strong montages | Functional, uses same light whoosh (could have heavier weight). |
| **Charged Attack** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Sword_Swing_Cue` | `ANS_CollisionTrace` on charged montages | Functional, lacks charge-up hum or heavy blade release. |
| **Air Light / Heavy Attack** | `AM_ER_Attack_Air_Light`, `AM_ER_Attack_Air_Heavy_Plunge` | Pack weapon collision trace | **GAP:** Heavy plunge landing lacks ground impact / shockwave crash. |
| **Guard Counter** | `SwordImpactLarge1..5` (shared strong data) | `GuardCounter` montage trace | **GAP:** Lacks distinct high-tension counter-clash sound on swing release. |
| **Backstep (Mixamo)** | *None* | Root-motion montage (`AM_Greystone_Backstep`) | **CRITICAL GAP:** Completely silent. Needs quick evasive foot slide / fabric whoosh. |
| **Dodge Roll** | Footstep notify only | Roll montage | Minor gap: lacks body roll / armor clink. |
| **Parry Press (Empty)** | *None* | `URPGPlayerParry` / `Ability.Parry` | Minor gap: no shield flick / raise whoosh on miss. |
| **PARRY SUCCESS (Reward)** | *None* (only visual slow-mo 0.2s + recoil) | `URPGPlayerParry::NotifyParried` | **TOP CRITICAL GAP:** Silent parry reward! Urgently needs sharp, resonant metallic deflect/bell clash. |
| **Block Impact** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/ShieldImpacts_Cue` | `BP_ImpactDecision` on block | Functional, solid shield thud. |
| **Hit Taken (Damage)** | `/Game/ParagonGreystone/Audio/Greystone_Effort_Pain` | Pack damage receiver event | Functional vocal grunt. |
| **Death** | `/Game/ParagonGreystone/Audio/Greystone_Death` | Pack character death flow | Functional vocal cry and collapse. |
| **Flask Use** | `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/A_Character_Heal_Mana_Cue` | `DrinkingPotion_Montage` notify | Functional potion gulp / shimmer. |

---

## 2. Boss (Sevarog) Audio Coverage Table

| Gameplay Event | Current Sound Asset Path | Call Site / Trigger Mechanism | Status / Gap Analysis |
|---|---|---|---|
| **A1 / A1b / A3a / A3b (Slashes)** | `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Sword_Swing_Cue` | `GS_Attack01..04` anim notifies | Functional pack whooshes. |
| **A2 (Overhead Ground Slam)** | Heavy swing + ground shockwave | `GS_ChargedAttack` + `AM_SevPack_Shockwave` | Functional; slam has bass impact. |
| **A4 (Low Sweep)** | Standard swing cue | `AN_Boss01_A4_LowSweep` dynamic montage | Functional, but lacks distinct floor-skimming scrape. |
| **A5 (Javelin Throw)** | *None* | `URPGBossHealPunish`, `ARPGBossJavelin` | **GAP (KI-068):** Cylinder leaves hand silently; no launch or flight whoosh. |
| **A6 (Leap Attack)** | Pack leap audio + Niagara slam | `GS_LeapAttack_Montage` | Functional. |
| **Mid01 / SprintFollowUp** | `A_Sword_Swing_Cue` | Pack sword mob montages | Functional basic swings. |
| **Boss Footsteps / Hover** | *None* (Greystone uses `Footstep_Concrete_Boots_*_Cue`) | `URPGFootsteps` (bound to player only) | **GAP:** Sevarog has no ambient ethereal wraith glide / robe rustle. |
| **PHASE 2 TRANSITION (Aura Ignite)** | Roar only (`Sevarog_Ability_Ultimate_Enemy`) | `URPGBossPhases` (50% HP threshold) | **TOP CRITICAL GAP:** Niagara BoostLite burst has no ignition/dark fire explosion sound. |
| **PARRY RECOIL** | *None* | `AM_Boss01_ParryRecoil` montage | **TOP CRITICAL GAP:** Recoil plays on every parry but is completely silent! Needs staggered grunt + weapon stumble. |
| **Stance Break (Poise 0)** | Standard stagger vocal | `URPGBossStagger::StartStagger` | **HIGH GAP:** Lacks a heavy Souls-like posture rupture / glass shatter cue. |
| **Phase Roar** | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Ability_Ultimate_Enemy` | Direct audio play on mesh | Functional, menacing roar. |
| **Boss Death** | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Death` | Pack boss death flow | Functional spectral demise. |

---

## 3. World Audio Coverage Table

| Gameplay Event | Current Sound Asset Path | Call Site / Trigger Mechanism | Status / Gap Analysis |
|---|---|---|---|
| **Arena Ambience** | `/Game/StarterContent/Audio/Ambient_Wind_Cue` | `URPGArenaAmbience::WindPlayer` | Functional desolate ruin wind loop. |
| **Torch / Fire Crackle** | `/Game/StarterContent/Audio/Fire01_Cue` | `ARPGFireSource::Crackle` | Functional fire loop. |
| **Boss Duel Music (Phase 1)** | `/Game/OneBossFight/Audio/MX_Boss01_Phase1` | `URPGBossMusic::EnsurePlayer` | Functional orchestral combat track. |
| **Boss Duel Music (Phase 2)** | `/Game/OneBossFight/Audio/MX_Boss01_Phase2` | `URPGBossMusic::OnPhaseChange` | Functional elevated intensity track. |
| **Victory Sting** | *None* | Encounter completion | **GAP:** Boss death leaves arena abruptly silent. Needs dark triumph brass/bell sting. |

---

## 4. Ranked Top Priority Gaps (For SFX-02 Candidates)

1. **PARRY SUCCESS (Player):** Needs an unmistakable, sharp, high-resonance metal deflection clash that rewards precise timing.
   - *Candidates available in repo:* `RealisticSwordSoundEffects` (e.g. `Sword_Sharpening_Fast_Speed_Cue`, `Sword_Attack_Short_1_Cue`, `SwordImpactLarge3`).
2. **PARRY RECOIL (Boss):** Needs a heavy weapon deflection shudder combined with a frustrated wraith grunt.
   - *Candidates available in repo:* `ParagonSevarog` (e.g. `Sevarog_Effort_PainHeavy`, `Sevarog_Effort_Block`) + `ShieldImpact4`.
3. **PHASE 2 AURA IGNITE (Boss):** Needs a deep, menacing dark flame burst / supernatural eruption accompanying the roar.
   - *Candidates available in repo:* `Vefects/Easy_Shockwaves_VFX/Audio/SFX_Vefects_Shockwave_04_1s_Cue` + `Fire01_Cue`.
4. **BACKSTEP WHOOSH (Player):** Needs a quick, clean wind displacement with subtle armor leather friction.
   - *Candidates available in repo:* `RealisticSwordSoundEffects/Swoosh_1_Cue` or `Swoosh_3_Cue`.
5. **STANCE BREAK SHATTER (Boss):** Needs a resounding heavy posture-crack sound.
   - *Candidates available in repo:* `Vefects/Easy_Shockwaves_VFX/Audio/SFX_Vefects_Shockwave_01_500ms_Cue` + `A_Guardian_ImpactL_Cue`.
