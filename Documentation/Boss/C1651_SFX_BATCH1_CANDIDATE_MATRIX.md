# C-1651 Audio/SFX Candidate Matrix: Batch 1/10 (SFX-06..SFX-10)

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2669]`, `[X-2670]`, `[C-1650]`, `[C-1651]`
- **Tasks Covered:** BT-112 (SFX-06), BT-110 (SFX-07), BT-113 (SFX-08), BT-111 (SFX-09), BT-109 (SFX-10)
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)

---

## 1. Executive Summary

Per Lead Codex directive `[X-2669]`, Antigravity has executed the initial discovery, candidate matrix authoring, and audition asset preparation for **C-1651 Audio/SFX Batch 1/10 (SFX-06 through SFX-10)**.

- **Audio Asset Policy:** Strictly repository-internal audio assets only. Zero external downloads, zero engine/asset modifications, zero wiring before Owner selection.
- **Audition Reel Prepared:** For **SFX-10 (BT-109)**, raw WAV exports were pre-existing under `D:\FightVideo\SFX_audition\RawWavs\`. A stitched audition reel (Option A + Option B + Option C separated by 1.0s silence) was generated into the clean, previously non-existent directory `D:\FightVideo\SFX_audition\C1651_Batch1_SFX10\`.
- **Export Blocker Documented:** For **SFX-06 (BT-112)**, **SFX-07 (BT-110)**, **SFX-08 (BT-113)**, and **SFX-09 (BT-111)**, repository Sound Cue `.uasset` packages are fully cataloged, hashed, and validated in-tree. However, raw `.wav` files have not yet been exported to disk. Exporting raw audio data from `.uasset` Sound Cues requires an authorized read-only Unreal Editor C-1155 export pass. Per strict guardrails, Antigravity has halted prior to any Editor launch and reports this export dependency cleanly.

---

## 2. Event-by-Event Candidate Matrix

### 2.1. SFX-06: Guard Counter Clash and Heavy Impact (BT-112)
- **Combat Context:** Player executes a heavy riposte/guard counter immediately following a successful parry or block deflection. Requires a distinct high-energy metallic bite combined with a resonant deflection ring.
- **Candidate Options:**
  - **Option A (Deflection Ring):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Fast_Speed_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Sharpening/Sword_Sharpening_Fast_Speed_Cue.uasset`
    - Size: 4,488 bytes | SHA-256: `57BC77ACD8072E4F230C52F027834E023DB85657F715D2B34C79FE14F4E263F8`
    - Acoustic Profile: Fast, high-frequency metallic scraping resonance; excellent for initial parry/counter contact instant.
  - **Option B (Heavy Buckler Clash):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact4`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Combat/ShieldImpacts/ShieldImpact4.uasset`
    - Size: 120,276 bytes | SHA-256: `534DD9287A163E4372DBEFC828B09CD25644049BD694B1D697C79766CF0E21D7`
    - Acoustic Profile: Solid, heavy buckler shield thud with broad midrange body; emphasizes defensive weight.
  - **Option C (Blade Bite Impact):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_2_Cue.uasset`
    - Size: 4,423 bytes | SHA-256: `7D02E64C8FDEC3AAE742A64FA9166BF52E1AD23154159EF21EB03337C80274D2`
    - Acoustic Profile: Sharp cutting impact transient with minimal tail; ideal for immediate offensive follow-through.
- **Raw WAV Export Status:** Unexported. Raw `.wav` files not present in `RawWavs/`. Requires C-1155 Editor session to export.

---

### 2.2. SFX-07: Air Plunge Crash and Ground Shockwave (BT-110)
- **Combat Context:** Player airborne plunging heavy attack descending into the stone floor of `L_SevarogArena`. Requires heavy sub-bass weight, seismic shockwave dispersal, and crumbling arena stone feedback.
- **Candidate Options:**
  - **Option A (Sub-Bass Shockwave Dispenser):**
    - UE Package: `/Game/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_01_1s_Cue`
    - File: `Content/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_01_1s_Cue.uasset`
    - Size: 4,247 bytes | SHA-256: `84B158CBCD9AA72C67DD69441C3B4FCAB56A1EC2D942C57F168001AE85779D3F`
    - Acoustic Profile: Tight 1.0s low-frequency burst with synthetic shockwave displacement; conveys radial force field.
  - **Option B (Arena Stone Fracture):**
    - UE Package: `/Game/StarterContent/Audio/Collapse_Cue`
    - File: `Content/StarterContent/Audio/Collapse_Cue.uasset`
    - Size: 6,517 bytes | SHA-256: `2BBD215BBB20C2A86F7B9BA4D90AA1870EDD1999E00B5FF64A52A657A50A690B`
    - Acoustic Profile: Heavy masonry collapse with falling stone debris and low rumble; matches arena flagstones.
  - **Option C (Dense Mass Impact):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.uasset`
    - Size: 10,806 bytes | SHA-256: `CB1797D251938322E0CF60806E6F9B9B50DCA094B90EBCC8B326B3085742D534`
    - Acoustic Profile: Heavy blunt kinetic shock with substantial iron armor resonance; emphasizes sheer body mass.
- **Raw WAV Export Status:** Unexported. Raw `.wav` files not present in `RawWavs/`. Requires C-1155 Editor session to export.

---

### 2.3. SFX-08: Sevarog A4 Low Sweep Friction Whoosh (BT-113)
- **Combat Context:** Sevarog's Attack 4 (A4) low ground sweep where the massive scythe blade skims and scrapes across the stone paving. Requires a threatening low-mid whoosh with abrasive friction scrape.
- **Candidate Options:**
  - **Option A (Heavy Low Drag):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_1_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_1_Cue.uasset`
    - Size: 4,381 bytes | SHA-256: `A289A487635498CB0245496988F4B4DA73D7ADA0D7E9CBEB13E3C3C0F0D6B698`
    - Acoustic Profile: Broad blade swing with noticeable air pressure and subtle metallic ring; good telegraph.
  - **Option B (Weighted Arc Displacement):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Axe_Swing_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Axe_Swing_Cue.uasset`
    - Size: 9,260 bytes | SHA-256: `9BD512C73D78759510386EA3499542E72260F50D0B1895B16F55E121C722A2C6`
    - Acoustic Profile: Deep, heavy whoosh suited for massive polearms and two-handed sweeps; high acoustic mass.
  - **Option C (Friction & Air Displacement):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_3_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_3_Cue.uasset`
    - Size: 4,339 bytes | SHA-256: `7E0DE5572368B3BC866C7178A9FE5154F0CCB94D79116C9062D3E029D0A93515`
    - Acoustic Profile: Fast high-velocity blade cutting air; crisp whoosh transient.
- **Raw WAV Export Status:** Unexported. Raw `.wav` files not present in `RawWavs/`. Requires C-1155 Editor session to export.

---

### 2.4. SFX-09: Sevarog A5 Javelin Summon and Release (BT-111)
- **Combat Context:** Sevarog's Attack 5 (A5) ranged magical summon and projectile release. Needs a two-part signature: an ominous ethereal summon build-up followed by a high-velocity piercing release whoosh.
- **Candidate Options:**
  - **Option A (Cosmic Rift Summon Burst):**
    - UE Package: `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift_Cue`
    - File: `Content/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/CosmicRift/A_Ability_CosmicRift_Cue.uasset`
    - Size: 9,449 bytes | SHA-256: `A41BACCD24FEDBC9BDF33B113DC4CC3755D99B399EB5A3A12FF428AD1C8A6782`
    - Acoustic Profile: Dark cosmic portal opening and sudden ethereal detonation; matches Sevarog's void sorcery.
  - **Option B (High-Velocity Launch Whoosh):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue.uasset`
    - Size: 4,423 bytes | SHA-256: `882D6253B32B3548C39EBBD7B082381D8134AEED8D96EECAA99FCF597CD88839`
    - Acoustic Profile: Snappy, high-speed release displacement; emphasizes projectile velocity.
  - **Option C (Spectral Materialization):**
    - UE Package: `/Game/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/Replenishment/CastReplenishment_Cue`
    - File: `Content/AdvancedARPGCombat/MagicCombatSystem/DemoAssets/SoundFX/Replenishment/CastReplenishment_Cue.uasset`
    - Size: 5,785 bytes | SHA-256: `BE9E1963A94403F7B539BDC508C11E17923B330C9BFE72E8578F28053E383993`
    - Acoustic Profile: Eerie magical gathering tone with shimmery high-end sheen; clean telegraph cue.
- **Raw WAV Export Status:** Unexported. Raw `.wav` files not present in `RawWavs/`. Requires C-1155 Editor session to export.

---

### 2.5. SFX-10: Boss Stance Break and Posture Shatter (BT-109)
- **Combat Context:** Boss posture bar fully depleted (100 posture damage reached), triggering a 2.5s stagger / critical riposte window. Must provide an unmistakably authoritative, crunchy audio feedback cue signaling vulnerability.
- **Candidate Options:**
  - **Option A (Preferred - Shattering Masonry Collapse):**
    - Source: `D:\FightVideo\SFX_audition\RawWavs\GAP05_OptionA_StanceBreak_Collapse01.wav`
    - Raw WAV Size: 345,664 bytes | SHA-256: `C5DCE8C2CE74BB23448CC9AC9571B49308DFC825229830F4D31D088AC3FDE6F3`
    - Corresponding UE Package: `/Game/StarterContent/Audio/Collapse_Cue` (`Content/StarterContent/Audio/Collapse_Cue.uasset`, SHA-256 `2BBD215BBB20C2A86F7B9BA4D90AA1870EDD1999E00B5FF64A52A657A50A690B`)
    - Acoustic Profile: Deep structural failure and fracturing stone; conveys devastating posture break.
  - **Option B (Dense Kinetic Impact):**
    - Source: `D:\FightVideo\SFX_audition\RawWavs\GAP05_OptionB_StanceBreak_GuardianImpact.wav`
    - Raw WAV Size: 155,372 bytes | SHA-256: `4614A403A42D7C0B9DA97194F89B2E0BE8EDF2D6B9B87483E06FCA180F57CB16`
    - Corresponding UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue` (`Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.uasset`, SHA-256 `CB1797D251938322E0CF60806E6F9B9B50DCA094B90EBCC8B326B3085742D534`)
    - Acoustic Profile: Heavy blunt thud with resonant iron ringing; conveys armor collapse.
  - **Option C (Sevarog Disorientation Drone):**
    - Source: `D:\FightVideo\SFX_audition\RawWavs\GAP05_OptionC_StanceBreak_SevarogDizzy.wav`
    - Raw WAV Size: 592,974 bytes | SHA-256: `36BD1F1CC9A32F7CC6B61D373AD15044229C52D7D6C672678A866BC6E081A6B5`
    - Corresponding UE Package: `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_ProfileDizzy_010` (`Content/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_ProfileDizzy_010.uasset`, SHA-256 `B58223B234546439A352123E27327A7630CDD98756F1B2DEC9F943ACD243C7AA`)
    - Acoustic Profile: Haunting spectral ringing and pitch-bending disorientation; conveys magical vulnerability.
- **Raw WAV Export Status:** **AVAILABLE ON DISK.**
- **Audition Reel Output:**
  - Destination Directory: `D:\FightVideo\SFX_audition\C1651_Batch1_SFX10\`
  - WAV Output: `D:\FightVideo\SFX_audition\C1651_Batch1_SFX10\C1651_SFX10_StanceBreak_Audition.wav`
    - Size: 1,446,060 bytes
    - Duration: ~16.39 seconds
    - SHA-256: `03180B7148CBB330426D7033CE1EA3A981FCDC3160E4C8A15790EBA8CC5A09FF`
  - MP3 Output: `D:\FightVideo\SFX_audition\C1651_Batch1_SFX10\C1651_SFX10_StanceBreak_Audition.mp3`
    - Size: 395,014 bytes
    - SHA-256: `B952D9A66D37715F671AFF2CC463A8DD8BBD818902C27B82C6E71DBBF794D74E`
  - **Reel Duration Discrepancy Note (X-2673):** Option A is 44.1 kHz mono (`3.918s`), while Options B (`0.809s`) and C (`3.085s`) are 48.0 kHz stereo. The initial concat demuxer concatenation without prior resample filter inherited the 44.1 kHz mono stream parameters for the subsequent clips, resulting in sample clock stretching to 16.39s. Codex independently generated a normalized 48.0 kHz stereo reel at `D:\FightVideo\SFX_audition\C1651_SFX10\` with mathematically exact duration `9.811633s` (3.918s + 1.0s + 0.809s + 1.0s + 3.085s). Both reels are retained non-destructively; Owner choice remains open.

---

## 3. Verification & Compliance Checklist

1. **Repository Isolation:** Only project-internal audio assets referenced. Zero external assets downloaded.
2. **Immutability:** Zero `.uasset` packages or config files modified.
3. **Engine Safety:** 0 Unreal Editor instances started. Both C-1155 locks remain untouched and absent.
4. **Git Safety:** 0 git commits, 0 git pushes performed.
5. **Audition Directory Hygiene:** `D:\FightVideo\SFX_audition\C1651_Batch1_SFX10\` was confirmed non-existent prior to creation; no pre-existing files overwritten.
6. **Task Board Status:** All five tasks (`BT-109`, `BT-110`, `BT-111`, `BT-112`, `BT-113`) advanced to `review`.
