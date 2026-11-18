# C-1651 Audio/SFX Candidate Matrix: Batch 4/10 (SFX-21..SFX-25)

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2676]`, `[C-1650]`, `[C-1651]`
- **Tasks Covered:** BT-126 (SFX-21), BT-127 (SFX-22), BT-128 (SFX-23), BT-129 (SFX-24), BT-130 (SFX-25)
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)

---

## 1. Executive Summary

Per Lead Codex directive `[X-2676]`, Antigravity has executed the candidate discovery, in-repo package verification, and acoustic specification for **C-1651 Audio/SFX Batch 4/10 (SFX-21 through SFX-25)**: Player Defense & Combat Foley.

- **Audio Asset Policy:** Strictly repository-internal audio assets only. Zero external downloads, zero engine/asset modifications, zero runtime wiring before Owner selection.
- **Spec-Only & Export Hold:** In accordance with [BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md](BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md) and directive `[X-2676]`, raw WAV export and audition reel compilation for SFX-21..25 are held pending Owner tone preferences. All 15 candidate Sound Cue packages are confirmed present in-tree, sized, and hashed.
- **Defense Audio Hierarchy:** Standard Block (`SFX-21`) delivers damped, exhausting iron impact thuds to contrast with the crystal-clear reward ping of Parry (`GAP-01`). Deflect / Glancing Blow (`SFX-22`) communicates partial mitigation via blade-to-blade friction rather than blunt absorption. Healing Flask (`SFX-23`) structures physical liquid intake followed by warm restorative shimmer. Armor Foley (`SFX-24`) grounds the knight archetype without obscuring boss telegraphs. Weapon Draw (`SFX-25`) establishes surgical steel crossguard contact.

---

## 2. Event-by-Event Candidate Matrix

### 2.1. SFX-21: Player Shield Standard Block (BT-126)
- **Combat Context:** Player absorbs an incoming boss strike using shield guard without achieving parry timing. Must communicate heavy physical shock and stamina drain without sounding like a rewarding deflection.
- **Hook Site:** `BlockImpactEffect` (Standard Hit Reaction).
- **Candidate Options:**
  - **Option A (Preferred - Shield Concussive Impact Cue):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpacts_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpacts_Cue.uasset`
    - Size: 9,173 bytes | SHA-256: `2EA0C3075C3C7D1F5FC3747485F5933BB173EECE7C50773F036D4D612B5F81CD`
    - Acoustic Profile: Solid iron-on-shield heavy thud with damped metal ring; conveys absorbed blunt force.
  - **Option B (Heavy Metallic Deflection):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact2`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact2.uasset`
    - Size: 119,738 bytes | SHA-256: `F8C2338E7FD7A3182809EDE6DB21F0ED0D6EA26020BE8A5254258CF60FBCA5D1`
    - Acoustic Profile: Crisp high-mass rim deflection crack with sharp edge bite.
  - **Option C (Greystone Vocal Block Reaction Cue):**
    - UE Package: `/Game/ParagonGreystone/Audio/Cues/Greystone_Effort_Block`
    - File: `Content/ParagonGreystone/Audio/Cues/Greystone_Effort_Block.uasset`
    - Size: 10,719 bytes | SHA-256: `35A862496D24885B7433299B9404A56489BBCF0446F57DC91D1EF800E4FAFA36`
    - Acoustic Profile: Player effort vocal grunt layered with shield shock; emphasizes physical strain.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.2. SFX-22: Player Deflect / Glancing Blow (BT-127)
- **Combat Context:** Player receives a partial block or glancing strike where blade/shield skims the attack, taking reduced chip damage. Demands an abrasive sliding friction sound.
- **Hook Site:** `URPGPlayerMovesSubsystem` (Deflect / Partial Block).
- **Candidate Options:**
  - **Option A (Preferred - High-Speed Blade Deflect Friction):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Fast_Speed_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Fast_Speed_Cue.uasset`
    - Size: 4,488 bytes | SHA-256: `57BC77ACD8072E4F230C52F027834E023DB85657F715D2B34C79FE14F4E263F8`
    - Acoustic Profile: Searing metal-on-metal spark scrape with sharp transient; conveys glancing deflection.
  - **Option B (Rough Friction Spark Scrape):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Rough_1_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Rough_1_Cue.uasset`
    - Size: 4,463 bytes | SHA-256: `CF69BD8E2A56595D6C6E0257E4CDAB10C877A50756666B1BAA4BCDDA3A7170E2`
    - Acoustic Profile: Coarse, grinding blade-slide friction hiss with abrasive texture.
  - **Option C (Precision Edge Deflection Contact):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact1`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact1.uasset`
    - Size: 113,363 bytes | SHA-256: `8FC3E91C251DB3BEA19539B9ED563A7947A17CA6CDBB9B2CF11D595AE01DF1D3`
    - Acoustic Profile: Tight edge-to-edge glancing collision click with minimal tail.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.3. SFX-23: Player Healing Flask Recovery (BT-128)
- **Combat Context:** Player consumes an Estus-style healing flask during an opening. Requires two distinct auditory cues: physical consumption intake followed by magical restorative bloom.
- **Hook Site:** Flask consumption event / `BP_ReplenishmentCue`.
- **Candidate Options:**
  - **Option A (Preferred - Health/Mana Recovery Shimmer):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Character_Heal_Mana_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Character_Heal_Mana_Cue.uasset`
    - Size: 6,105 bytes | SHA-256: `58FDCA4E8D725CDB4891615AC277E12CD645EC41358FD7FC66B6B582B48552CA`
    - Acoustic Profile: Ethereal liquid intake followed by warm restorative bloom; classic soulslike flask chime.
  - **Option B (Mystic Replenishment Chime):**
    - UE Package: `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/Replenishment/CastReplenishment_Cue`
    - File: `Content/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/Replenishment/CastReplenishment_Cue.uasset`
    - Size: 5,785 bytes | SHA-256: `BE9E1963A94403F7B539BDC508C11E17923B330C9BFE72E8578F28053E383993`
    - Acoustic Profile: Magical resonance chime indicating restoration completion.
  - **Option C (Radiant Light Ascension Stinger):**
    - UE Package: `/Game/StarterContent/Audio/Light01_Cue`
    - File: `Content/StarterContent/Audio/Light01_Cue.uasset`
    - Size: 4,237 bytes | SHA-256: `BC123926FC005ACEAA148EDFC4CF3778E694A8C17E1E359448377462D4A63D95`
    - Acoustic Profile: Clean, luminous high-register restorative shine.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.4. SFX-24: Player Dodge Roll Armor Foley (BT-129)
- **Combat Context:** Player executes a defensive roll or backstep evasion. Needs subtle leather, mail, and boot contact foley that grounds movement without cluttering telegraphs.
- **Hook Site:** `AM_ER_Backstep_*` / Roll recovery ground contact frame.
- **Candidate Options:**
  - **Option A (Preferred - Concrete Boot Land & Armor Settle):**
    - UE Package: `/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue`
    - File: `Content/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue.uasset`
    - Size: 9,983 bytes | SHA-256: `51C28F5B35F13304FE3BB046233638C70CD346CF6491EFFC14838E4A02BBDCF0`
    - Acoustic Profile: Heavy leather/plate compression and arena stone thud; matches flagstone flooring.
  - **Option B (Dirt Ground Contact & Roll Scrape):**
    - UE Package: `/Game/Essential_Foosteps_SK/CUE/Dirt/Footstep_Dirt_Boots_Land_1_Cue`
    - File: `Content/Essential_Foosteps_SK/CUE/Dirt/Footstep_Dirt_Boots_Land_1_Cue.uasset`
    - Size: 9,932 bytes | SHA-256: `3C142D84CDFA202A91447288C0E40C68621E21B04F0B81823619490ED7FA32D1`
    - Acoustic Profile: Abrasive gravel/dirt ground contact roll rustle.
  - **Option C (Heavy Armor Tactical Step Transient):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/Character/A_Character_Step01`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/UI/MainMenu/Assets/Sounds/Character/A_Character_Step01.uasset`
    - Size: 197,868 bytes | SHA-256: `DD834627F99035979D06AE21CF81335EBD6002B8EF3A11F5A2AE097E57483B52`
    - Acoustic Profile: Damped heel-to-toe tactical armor adjustment foley.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.5. SFX-25: Player Weapon Draw & Sheathe (BT-130)
- **Combat Context:** Player enters or exits combat stance, unsheathing or locking sword into scabbard. Needs an authoritative steel rasp and scabbard click.
- **Hook Site:** Combat stance entry / exit (`DrawSword_Montage`).
- **Candidate Options:**
  - **Option A (Preferred - Realistic Sword Unsheathe Draw):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Unsheathe/Sword_Unsheathe_1_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Unsheathe/Sword_Unsheathe_1_Cue.uasset`
    - Size: 4,411 bytes | SHA-256: `1DE2AAA320405708AAEC6F61DB0D04FBD67178493AF5A601EABD03C5AC3BD42C`
    - Acoustic Profile: Searing surgical steel ring drawn from scabbard; crisp high-end definition.
  - **Option B (Pack Metallic Scrape Draw Cue):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/DrawDisarm/SwordDraw1_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/DrawDisarm/SwordDraw1_Cue.uasset`
    - Size: 4,418 bytes | SHA-256: `A589579E6970E57842627E9E81D177ED149742FEB3FC49869940F7014ED917FD`
    - Acoustic Profile: Heavy battlefield steel slide across crossguard.
  - **Option C (Pack Weighted Leather Sheathe Cue):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/DrawDisarm/SwordSheath2_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/DrawDisarm/SwordSheath2_Cue.uasset`
    - Size: 4,432 bytes | SHA-256: `06039C884AEB61737452714DFF968E7A4702A8D4982D01309CC9F46EDE36B219`
    - Acoustic Profile: Weighted leather-throated scabbard lock with solid final click.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

## 3. Verification & Compliance Checklist

1. **Repository Isolation:** Only project-internal audio assets referenced. Zero external assets downloaded.
2. **Immutability:** Zero `.uasset` packages or config files modified.
3. **Engine Safety:** 0 Unreal Editor instances started. Both C-1155 locks remain untouched and absent.
4. **Git Safety:** 0 git commits, 0 git pushes performed.
5. **Hold Compliance:** In accordance with `BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md`, zero WAV files were exported and zero audition reels were built; candidates remain spec-only.
6. **Task Board Status:** All five tasks (`BT-126`, `BT-127`, `BT-128`, `BT-129`, `BT-130`) advanced to `review`.
