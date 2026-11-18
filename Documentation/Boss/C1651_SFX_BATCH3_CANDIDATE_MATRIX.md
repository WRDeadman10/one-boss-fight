# C-1651 Audio/SFX Candidate Matrix: Batch 3/10 (SFX-16..SFX-20)

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2675]`, `[C-1650]`, `[C-1651]`
- **Tasks Covered:** BT-121 (SFX-16), BT-122 (SFX-17), BT-123 (SFX-18), BT-124 (SFX-19), BT-125 (SFX-20)
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)

---

## 1. Executive Summary

Per Lead Codex directive `[X-2675]`, Antigravity has executed the candidate discovery, in-repo package verification, and acoustic specification for **C-1651 Audio/SFX Batch 3/10 (SFX-16 through SFX-20)**: Phase Transition, Awakening Roar, and Atmosphere Audio.

- **Audio Asset Policy:** Strictly repository-internal audio assets only. Zero external downloads, zero engine/asset modifications, zero runtime wiring before Owner selection.
- **Spec-Only & Export Hold:** In strict compliance with [BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md](BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md) and directive `[X-2675]`, raw WAV export and audition reel generation for SFX-16..20 are held pending Owner tone preferences. All 15 candidate Sound Cue packages are confirmed present in-tree, sized, and hashed.
- **Character Voice Separation:** Per architecture directive `[C-1208]`, Ember Warden (`Boss01`) vocalizations must remain distinct from the future standalone Sevarog encounter (`Boss02`). Candidate options provide non-colliding options (Grux primal bellow, Steel armored exertion) while flagging the native Sevarog vocal cue with an archetype caution.

---

## 2. Event-by-Event Candidate Matrix

### 2.1. SFX-16: Boss Phase 2 Awakening Vocal Roar / Screech (BT-121)
- **Combat Context:** Boss reaches Phase 2 health threshold (<= 60% / 900 HP), triggering the Phase 2 awakening transition presentation. Demands a monstrous, room-shaking vocal roar that commands immediate attention.
- **Hook Site:** `URPGTier2BossPresentation` trigger / `AM_SevPack_Roar`.
- **Candidate Options:**
  - **Option A (Preferred - Grux Primal Beast Roar):**
    - UE Package: `/Game/ParagonGrux/Characters/Heroes/Grux/Sounds/SoundCues/Grux_Effort_Ability_Ultimate`
    - File: `Content/ParagonGrux/Characters/Heroes/Grux/Sounds/SoundCues/Grux_Effort_Ability_Ultimate.uasset`
    - Size: 8,193 bytes | SHA-256: `90113E33A1122FFF343214671D316A2B560792C0D46933CE5389A5477CD6119D`
    - Acoustic Profile: Monstrous, deep primal bellow with guttural sub-bass; keeps Ember Warden audibly distinct from Sevarog.
  - **Option B (Steel Guttural War Cry):**
    - UE Package: `/Game/ParagonSteel/Audio/Cues/Steel_Effort_Ability_Primary_Swing`
    - File: `Content/ParagonSteel/Audio/Cues/Steel_Effort_Ability_Primary_Swing.uasset`
    - Size: 10,856 bytes | SHA-256: `70C17D56D7CCC0094949D1EB61F75D1AEA0AC5716F920CE2468C634406ED3FDE`
    - Acoustic Profile: Armored titan heavy exertion roar with metallic resonance; conveys imposing physical bulk.
  - **Option C (Sevarog Spectral Shriek - Archetype Caution):**
    - UE Package: `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_Ultimate`
    - File: `Content/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Ability_Ultimate.uasset`
    - Size: 8,259 bytes | SHA-256: `20265375CC9E4B2C2D511C9CAD0AA8E9BFC4C6FA10C6B86B561CAB4E9D929AF5`
    - Acoustic Profile: Ghostly wraith screech with eerie reverb tail *(Caution: shares vocal signature with future Sevarog boss)*.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.2. SFX-17: Phase 2 Ember Aura Ignite Burst (BT-122)
- **Combat Context:** Instantaneous eruption of flaming aura encircling the boss upon entering Phase 2. Requires a sudden explosive ignition transient with sharp pressure release.
- **Hook Site:** `PhaseTwoAuraEffect` component spawn event.
- **Candidate Options:**
  - **Option A (Preferred - Detonation Impact Burst):**
    - UE Package: `/Game/StarterContent/Audio/Explosion_Cue`
    - File: `Content/StarterContent/Audio/Explosion_Cue.uasset`
    - Size: 8,088 bytes | SHA-256: `91B66CEDCFEEDCAA25D7B2AFE79C3DFB636E625F626FB56CE9B410FC6495EF3B`
    - Acoustic Profile: Heavy concussive explosion transient with low rolling rumble; conveys violent combustion.
  - **Option B (Fiery Ignition Blast):**
    - UE Package: `/Game/StarterContent/Audio/Fire_Sparks01_Cue`
    - File: `Content/StarterContent/Audio/Fire_Sparks01_Cue.uasset`
    - Size: 4,299 bytes | SHA-256: `3C13448535C552552C0216AA5A9D5AF5957D4606153A004CDCEC934EA5E9A22B`
    - Acoustic Profile: Searing high-frequency flame burst with intense crackling ember sparks.
  - **Option C (Arcane Concussive Explosion):**
    - UE Package: `/Game/AdvancedARPGCombat/RangedCombatSystem/DemoAssets/Effects/ExampleExplosion/ExampleExplosionImpact_Cue`
    - File: `Content/AdvancedARPGCombat/RangedCombatSystem/DemoAssets/Effects/ExampleExplosion/ExampleExplosionImpact_Cue.uasset`
    - Size: 9,237 bytes | SHA-256: `65D9581EFDBCD3924F245F980C618E6642D0FBE09BE05C497ECAE943C9B1B8AD`
    - Acoustic Profile: Tightly focused concussive blast with sharp shockwave onset.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.3. SFX-18: Persistent Fiery Aura Ambient Loop (BT-123)
- **Combat Context:** Continuous ambient sound radiating from the boss throughout Phase 2. Must provide constant atmospheric tension without masking critical combat telegraphed cues (parries, whooshes).
- **Hook Site:** `PhaseTwoAuraComponent` continuous low-pass loop.
- **Candidate Options:**
  - **Option A (Preferred - Continuous Roaring Flame):**
    - UE Package: `/Game/StarterContent/Audio/Fire01_Cue`
    - File: `Content/StarterContent/Audio/Fire01_Cue.uasset`
    - Size: 4,280 bytes | SHA-256: `A3C93DCA255FFE4FCD045103B0CF1341ADDA3640B47A5656C82EF6236639A51C`
    - Acoustic Profile: Broad-spectrum burning embers and low roar; easily shaped with low-pass filtering.
  - **Option B (Subtle Melee Pack Fire Loop):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Fire01_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Fire01_Cue.uasset`
    - Size: 5,054 bytes | SHA-256: `390FF341C251A973E86FF2BE7C0FC405C3A49487D10449F3E851666CE170A9C8`
    - Acoustic Profile: Tight, lower-volume intimate fire crackle; minimal masking of attack cues.
  - **Option C (Low Vapor / Steam Hiss):**
    - UE Package: `/Game/StarterContent/Audio/Steam01_Cue`
    - File: `Content/StarterContent/Audio/Steam01_Cue.uasset`
    - Size: 4,285 bytes | SHA-256: `C43FB733EBFC395AF98CE820DE46FED7D2B3F2A42AD03F55C8CF8E12D1BD417F`
    - Acoustic Profile: Subdued pressurized vapor/steam undertone; adds geothermal heat texture.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.4. SFX-19: Phase 2 Transition Ground Rupture Crackle (BT-124)
- **Combat Context:** Arena stone floor tearing and fracturing radially outward during the transition. Needs a prolonged tearing rock fissure audio signature.
- **Hook Site:** `NS_Boss_ShockwaveRing` floor crack emergence.
- **Candidate Options:**
  - **Option A (Preferred - Extended Ground Rupture):**
    - UE Package: `/Game/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_04_2s_Cue`
    - File: `Content/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_04_2s_Cue.uasset`
    - Size: 4,247 bytes | SHA-256: `AED63352954768E6A1B12980865C237195BBE4BC9D13FD9699A251FA5B28EB25`
    - Acoustic Profile: 2.0s tearing rock fissure with expansive concussive wave; matches visual crack FX.
  - **Option B (Stone Collapse & Debris):**
    - UE Package: `/Game/StarterContent/Audio/Collapse_Cue`
    - File: `Content/StarterContent/Audio/Collapse_Cue.uasset`
    - Size: 6,517 bytes | SHA-256: `2BBD215BBB20C2A86F7B9BA4D90AA1870EDD1999E00B5FF64A52A657A50A690B`
    - Acoustic Profile: Heavy structural masonry crumble with falling stones and subterranean rumble.
  - **Option C (Deep Earth Tremor Shockwave):**
    - UE Package: `/Game/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_02_2s_Cue`
    - File: `Content/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_02_2s_Cue.uasset`
    - Size: 4,247 bytes | SHA-256: `66AAAF35BEC87B15EB12BD136E221728E7A4C11D9CB989EF6646A785963D3B89`
    - Acoustic Profile: Deep subsonic floor rumble with punchy leading edge.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

### 2.5. SFX-20: Phase Transition Stinger / Combat Shift (BT-125)
- **Combat Context:** One-shot musical / atmospheric accent marking the boss's transformation into Phase 2 state. Communicates dramatic escalation.
- **Hook Site:** Tier 2 Boss Presentation state entry stinger.
- **Candidate Options:**
  - **Option A (Preferred - In-Engine Cosmic Void Swell):**
    - UE Package: `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift_Cue`
    - File: `Content/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift_Cue.uasset`
    - Size: 9,449 bytes | SHA-256: `A41BACCD24FEDBC9BDF33B113DC4CC3755D99B399EB5A3A12FF428AD1C8A6782`
    - Acoustic Profile: Deep atmospheric void swell with sub-bass drop; non-orchestral in-engine cue.
  - **Option B (Orchestral - Starter Battle Orchestral Swell):**
    - UE Package: `/Game/StarterContent/Audio/Starter_Music_Cue`
    - File: `Content/StarterContent/Audio/Starter_Music_Cue.uasset`
    - Size: 3,753 bytes | SHA-256: `E6FDBDA2320B26AA806D967CA88390FBD6DD6078432952800FD029CF313BB2CE`
    - Acoustic Profile: Full orchestral brass/string dramatic accent; high cinematic impact.
  - **Option C (Mystic Chime - Ethereal Ascension Riser):**
    - UE Package: `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/Replenishment/CastReplenishment_Cue`
    - File: `Content/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/Replenishment/CastReplenishment_Cue.uasset`
    - Size: 5,785 bytes | SHA-256: `BE9E1963A94403F7B539BDC508C11E17923B330C9BFE72E8578F28053E383993`
    - Acoustic Profile: High-register mystical chime riser and shimmering decay.
- **Export / Reel Status:** Spec-only; held on disk pending Owner tone selection per `BB-A05`.

---

## 3. Verification & Compliance Checklist

1. **Repository Isolation:** Only project-internal audio assets referenced. Zero external assets downloaded.
2. **Immutability:** Zero `.uasset` packages or config files modified.
3. **Engine Safety:** 0 Unreal Editor instances started. Both C-1155 locks remain untouched and absent.
4. **Git Safety:** 0 git commits, 0 git pushes performed.
5. **Hold Compliance:** In accordance with `BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md`, zero WAV files were exported and zero audition reels were built; candidates remain spec-only.
6. **Task Board Status:** All five tasks (`BT-121`, `BT-122`, `BT-123`, `BT-124`, `BT-125`) advanced to `review`.
