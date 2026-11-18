# C-1651 Audio/SFX Candidate Matrix: Batch 2/10 (SFX-11..SFX-15)

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2673]`, `[X-2674]`, `[C-1650]`, `[C-1651]`
- **Tasks Covered:** BT-118 (SFX-11), BT-117 (SFX-12), BT-115 (SFX-13), BT-119 (SFX-14), BT-116 (SFX-15)
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)

---

## 1. Executive Summary

Per Lead Codex directives `[X-2673]` and `[X-2674]`, Antigravity has executed the candidate discovery, package verification, and audition asset compilation for **C-1651 Audio/SFX Batch 2/10 (SFX-11 through SFX-15)**: Boss Attack Whooshes & Heavy Foley.

- **Audio Asset Policy:** Strictly repository-internal audio assets only. Zero external downloads, zero engine/asset modifications, zero runtime wiring before Owner selection.
- **Raw WAV Presence:** All 15 candidate raw WAV files were pre-existing in `D:\FightVideo\SFX_audition\RawWavs\`.
- **Audition Reels Prepared:** Individual event audition reels and a consolidated Batch 2 audition reel were generated into the unique, non-overwriting destination directory `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\`. All audio inputs were normalized to 48.0 kHz stereo 16-bit PCM with 1.0s silence spacers to prevent clock stretching or sample-rate mismatch.
- **Batch 1 SFX-10 Discrepancy Reconciled:** The clock stretching reported in `[X-2673]` (16.39s vs 9.81s) was traced to Option A being 44.1 kHz mono while Options B and C are 48.0 kHz stereo; the demuxer inherited 44.1 kHz mono stream parameters for subsequent clips. Reconciled in [C1651_SFX_BATCH1_CANDIDATE_MATRIX.md](C1651_SFX_BATCH1_CANDIDATE_MATRIX.md).

---

### Lead checksum reconciliation (2026-11-18)

Lead disk check found the original listed SHA-256 values mismatched 10/15 candidate Sound Cue packages and 14/15 source WAVs; all 30 documented byte sizes matched. The hashes in the candidate rows below are now recomputed from the current files. All 12 existing audition outputs (five event WAV/MP3 pairs plus the consolidated pair) independently match their documented byte sizes and SHA-256 hashes. No audio file was changed or rebuilt. This checks present file identity; it does not assert the historical reel build used byte-identical source WAVs.

## 2. Event-by-Event Candidate Matrix

### 2.1. SFX-11: Boss A1 Horizontal Slash High-Speed Blade Air Whoosh (BT-118)
- **Combat Context:** Sevarog's Attack 1 (A1) horizontal sweeping blade arc. Serves as an essential dodge/parry telegraph. Requires a crisp cutting arc with distinct air displacement.
- **Hook Site:** `AM_Boss01_A1` active blade arc notify (`AN_Boss01_A1`).
- **Candidate Options:**
  - **Option A (Preferred - Medium Blade Cleave):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_1_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_1_Cue.uasset` (4,381 bytes, SHA-256 `A289A487635498CB0245496988F4B4DA73D7ADA0D7E9CBEB13E3C3C0F0D6B698`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX11_OptionA_A1_Attack1.wav` (211,498 bytes, 1.101s, 48 kHz stereo, SHA-256 `9FAB8E15F362E5B4358F7D46E4B15F54B7FF61013FD10FE195013B89BC2A116A`)
    - Acoustic Profile: Crisp, cutting arc with high-tension metallic edge.
  - **Option B (Swift Velocity Swoosh):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_1_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_1_Cue.uasset` (4,339 bytes, SHA-256 `0609D1156EB2F1FA2E83B22281920E55B5B6E22FF50625E39EEB6261888DA8C6`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX11_OptionB_A1_Swoosh1.wav` (156,114 bytes, 0.813s, 48 kHz stereo, SHA-256 `AB161163AA4A888B40A3C1E3374D57195B11EEFA04EB9EF9D972054AB3866E84`)
    - Acoustic Profile: Sharp high-velocity swoosh with brief duration; emphasizes speed.
  - **Option C (Standard Sword Swing):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Sword_Swing_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Sword_Swing_Cue.uasset` (8,989 bytes, SHA-256 `BC41A16E46ADFD63D2A3BD431CBC9AA65ECD0EC3B7EAC38B53BD5E414C5D2A35`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX11_OptionC_A1_SwordSwing01.wav` (192,044 bytes, 1.000s, 48 kHz stereo, SHA-256 `3B92C0C579C851D52EB08427586CC4DFCEBAC5DDEA6C6CA65ACC5FA8506E1FD9`)
    - Acoustic Profile: Balanced standard swing whoosh from combat pack.
- **Audition Reel Deliverable:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX11_A1_HorizontalSlash_Audition.wav` (943,462 bytes, 4.913s, SHA-256 `E204E8A8EF13BD3F9D15BBD6B2F55D5BEABAF8567E406D888ED22DAC4F876C35`)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX11_A1_HorizontalSlash_Audition.mp3` (119,276 bytes, SHA-256 `44C9BE1EA1AA5ADF5E7D9E6F27286571EAF1277F148DFBBBCAA624FCD4D3C789`)

---

### 2.2. SFX-12: Boss A2 Overhead Cleave Heavy Downward Wind Pressure Whoosh (BT-117)
- **Combat Context:** Sevarog's Attack 2 (A2) vertical overhead cleave slam. Heavy, deliberate downward strike requiring enormous acoustic mass to communicate danger.
- **Hook Site:** `AM_Boss01_A2` downward stroke frame (`AN_Boss01_A2`).
- **Candidate Options:**
  - **Option A (Preferred - Heavy Vertical Cleave):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_3_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_3_Cue.uasset` (4,381 bytes, SHA-256 `0C2223BED324F36EAAFB75CD2F0D99AB281999D82279039765DE3B2B9A6E15A2`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX12_OptionA_A2_Attack3.wav` (250,266 bytes, 1.303s, 48 kHz stereo, SHA-256 `BCB9A354305C00D14372A0791389E766A4C65AF1AE7DB2F64B48A477D80ED9C7`)
    - Acoustic Profile: Powerful vertical cut with low-end air displacement.
  - **Option B (Weighted Downward Axe Swing):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Axe_Swing_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Axe_Swing_Cue.uasset` (9,260 bytes, SHA-256 `9BD512C73D78759510386EA3499542E72260F50D0B1895B16F55E121C722A2C6`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX12_OptionB_A2_AxeSwing01.wav` (192,044 bytes, 1.000s, 48 kHz stereo, SHA-256 `873AE94D64E3026F42395B5F42D017B30F41C051B24B9D0A3C8D794D056BEED7`)
    - Acoustic Profile: Heavy downward momentum swing with wide tonal body.
  - **Option C (Deep Wind Drag Cleave):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_5_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_5_Cue.uasset` (4,381 bytes, SHA-256 `AA746B7A9A62180FCCEB78201F1449B74F5993E1295C8A52BA01DF371F1807A0`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX12_OptionC_A2_Attack5.wav` (243,806 bytes, 1.269s, 48 kHz stereo, SHA-256 `0525EC22E9C61406B820AE97F99A319A1E2D922CE1496B9598FDA945BD101FE4`)
    - Acoustic Profile: Deep sub-bass air rush with smooth decay.
- **Audition Reel Deliverable:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX12_A2_OverheadCleave_Audition.wav` (1,069,922 bytes, 5.572s, SHA-256 `3A6EFEE7407BE77D58CDD1C82D92015EFFED143E2A741A67B735D65A44718C10`)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX12_A2_OverheadCleave_Audition.mp3` (135,404 bytes, SHA-256 `437ABE2EF8B3048A0849C1E3CABFD1AB348226AA06A2855C58549FDFB4BD95C5`)

---

### 2.3. SFX-13: Boss A3 Ground Stomp Shockwave Sub-Bass Thud (BT-115)
- **Combat Context:** Sevarog's Attack 3 (A3) foot stomp generating a radial shockwave across the arena paving. Demands a heavy sub-bass transient followed by an expanding pressure wave.
- **Hook Site:** `AM_Boss01_A3` footfall frame (`AN_Boss01_A3`).
- **Candidate Options:**
  - **Option A (Preferred - Shockwave Concussion):**
    - UE Package: `/Game/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_01_1s_Cue`
    - File: `Content/Vefects/Easy_Shockwaves_VFX/Audio/Cues/SFX_Vefects_Shockwave_01_1s_Cue.uasset` (4,247 bytes, SHA-256 `84B158CBCD9AA72C67DD69441C3B4FCAB56A1EC2D942C57F168001AE85779D3F`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX13_OptionA_A3_Shockwave01.wav` (183,240 bytes, 1.039s, 44.1 kHz stereo, SHA-256 `4E136A5A686C8028B383A8133692D00787D44BB1D27C4E7AB445830DAA9ADA33`)
    - Acoustic Profile: Radial force displacement with low-frequency punch.
  - **Option B (Detonation Rumble):**
    - UE Package: `/Game/StarterContent/Audio/Explosion_Cue`
    - File: `Content/StarterContent/Audio/Explosion_Cue.uasset` (8,088 bytes, SHA-256 `91B66CEDCFEEDCAA25D7B2AFE79C3DFB636E625F626FB56CE9B410FC6495EF3B`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX13_OptionB_A3_Explosion01.wav` (279,860 bytes, 3.170s, 44.1 kHz mono, SHA-256 `3BD4D37F5961B03664C96148C4AE33F92E2491F797DE8DAC0DCAA7A4D222E0F7`)
    - Acoustic Profile: Heavy seismic low rumble with rolling debris tail.
  - **Option C (Stone Guardian Thud):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.uasset` (10,806 bytes, SHA-256 `CB1797D251938322E0CF60806E6F9B9B50DCA094B90EBCC8B326B3085742D534`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX13_OptionC_A3_GuardianImpact01.wav` (155,372 bytes, 0.809s, 48 kHz stereo, SHA-256 `4614A403A42D7C0B9DA97194F89B2E0BE8EDF2D6B9B87483E06FCA180F57CB16`)
    - Acoustic Profile: Dense kinetic footfall impact with stone resonance.
- **Audition Reel Deliverable:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX13_A3_GroundStomp_Audition.wav` (1,347,530 bytes, 7.018s, SHA-256 `81713AC8447B65073A6B644A3349CA36045C11D72011C89DA50E6743E115D915`)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX13_A3_GroundStomp_Audition.mp3` (169,964 bytes, SHA-256 `F2A7A6F0EBA75361D60F27BA5C3C1CEE24990F305D3E4D1B3111A6E9AD042E96`)

---

### 2.4. SFX-14: Boss Mid01 Forward Thrust Piercing Air Wake Whoosh (BT-119)
- **Combat Context:** Sevarog's Mid01 directional thrust attack. Focused, linear piercing trajectory that requires a concentrated high-velocity forward air cut.
- **Hook Site:** `AM_Boss01_Mid01` thrust apex frame (`AN_Boss01_Mid01`).
- **Candidate Options:**
  - **Option A (Preferred - Piercing Air Wake):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_Short_1_Cue.uasset` (4,423 bytes, SHA-256 `882D6253B32B3548C39EBBD7B082381D8134AEED8D96EECAA99FCF597CD88839`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX14_OptionA_Mid01_AttackShort1.wav` (175,498 bytes, 0.913s, 48 kHz stereo, SHA-256 `C2DDD3EB7F050F9EE63F0EFF9311CF25164B781CAE6B863F11A16A7189D394CF`)
    - Acoustic Profile: Fast, focused forward puncture transient.
  - **Option B (Directional Air Cut):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_4_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Swoosh/Swoosh_4_Cue.uasset` (4,339 bytes, SHA-256 `73B6BC778D96D189B8E2FF5116E2B3709EC356D031D2519E6B8DD038FA264978`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX14_OptionB_Mid01_Swoosh4.wav` (200,422 bytes, 1.043s, 48 kHz stereo, SHA-256 `9CDFBC7B50044DDAAD4C3C6CB80AC75AE5E967E8F17BF53A771880DDC569D370`)
    - Acoustic Profile: Crisp directional whoosh with tight air displacement.
  - **Option C (Linear Slicing Thrust):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_7_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_7_Cue.uasset` (4,381 bytes, SHA-256 `90ADA895558A099B6165AEE4660779C4247972910F6E78788B38E3C446F6A6B4`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX14_OptionC_Mid01_Attack7.wav` (252,114 bytes, 1.313s, 48 kHz stereo, SHA-256 `BBB410E439BD497B191CC0D1F1909E83D746F9AB73587900800CEF6C68DA15E7`)
    - Acoustic Profile: Elongated blade slide with subtle ring.
- **Audition Reel Deliverable:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX14_Mid01_ForwardThrust_Audition.wav` (1,011,770 bytes, 5.269s, SHA-256 `6B94622DBB74DE7DB8277497C70E925A0F147690DAB4A78A1756D3AA7F2E52A0`)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX14_Mid01_ForwardThrust_Audition.mp3` (127,916 bytes, SHA-256 `8B8B7476EF5883E2E4226569C341B49D684ED7BA18706E9D381B825A45C9AD24`)

---

### 2.5. SFX-15: Boss Sprint Gap-Closer Momentum Sweep Whoosh (BT-116)
- **Combat Context:** Sevarog's sprint charge transitioning into a wide horizontal momentum strike. Requires high-energy velocity buildup and heavy arc whoosh.
- **Hook Site:** `AM_Boss01_Sprint` horizontal strike release (`AN_Boss01_Sprint`).
- **Candidate Options:**
  - **Option A (Preferred - Sweeping Momentum Whoosh):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_2_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_2_Cue.uasset` (4,381 bytes, SHA-256 `953005BDF9120732DBA2C321A6F35424F2D92EAA5D757D24169AD95B3AC7128A`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX15_OptionA_Sprint_Attack2.wav` (234,574 bytes, 1.221s, 48 kHz stereo, SHA-256 `07672EF027AB4DBAC4182D864EBC702DB23B5618C9CC15DE152544C0FE1A8AED`)
    - Acoustic Profile: Heavy momentum carry with broad blade sweep.
  - **Option B (Heavy Velocity Hammer Swing):**
    - UE Package: `/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Hammer_Swing_Cue`
    - File: `Content/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Hammer_Swing_Cue.uasset` (9,302 bytes, SHA-256 `0506F7268D57FBD78B3E7F7FF6A03F07EF26D80AFC3529498DCF1DC0DB4F8C95`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX15_OptionB_Sprint_HammerSwing01.wav` (228,044 bytes, 1.188s, 48 kHz stereo, SHA-256 `B0DC1444E91072963040A62AABB75094D516E69EA3E192EDA2246A87B7789A50`)
    - Acoustic Profile: Wide, dense air displacement suited for heavy momentum attacks.
  - **Option C (High-Speed Wide Edge):**
    - UE Package: `/Game/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_8_Cue`
    - File: `Content/RealisticSwordSoundEffects/Cues/Sword_Attack/Sword_Attack_8_Cue.uasset` (4,381 bytes, SHA-256 `0A389946E098E60F7194FF643429007CB7641BB49B4B704A0E05A852FD784DE9`)
    - Raw WAV: `D:\FightVideo\SFX_audition\RawWavs\SFX15_OptionC_Sprint_Attack8.wav` (240,114 bytes, 1.250s, 48 kHz stereo, SHA-256 `E3C88F34B5C294811FDD80D2E642989E12FED0236E5121D16F49F806E802C2FB`)
    - Acoustic Profile: Sharp cutting arc with rapid dissipation.
- **Audition Reel Deliverable:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX15_Sprint_GapCloser_Audition.wav` (1,086,538 bytes, 5.659s, SHA-256 `7E31293529805BFF7322FD596A3D338E39C77F174F075899562E0FCFA20C4F07`)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX15_Sprint_GapCloser_Audition.mp3` (137,132 bytes, SHA-256 `921E7A887CF3C87C0F26E0EF1DBA1E5846712286CBFC02D52ADB3E958D57CA5E`)

---

## 3. Consolidated Batch 2 Audition Reel

In addition to individual event audition reels, a full Batch 2 reel concatenating all five events in sequence (SFX-11 through SFX-15) was built with normalized 48.0 kHz stereo streams:

- Destination Directory: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\`
- WAV Output: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_Batch2_Full_Audition.wav`
  - Size: 5,458,910 bytes
  - Duration: 28.431 seconds
  - SHA-256: `5D53C6F9CE0174711BA76457F027C5477F77614E9B4EEA7BE36FB2193B910FC3`
- MP3 Output: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_Batch2_Full_Audition.mp3`
  - Size: 683,756 bytes
  - SHA-256: `4C8C53BA0FD9F7FA7FE97EC7B19C18C9E5322301E0703CDD2F28CE6F8E6DBC39`

---

## 4. Verification & Compliance Checklist

1. **Repository Isolation:** Only project-internal audio assets referenced. Zero external assets downloaded.
2. **Immutability:** Zero `.uasset` packages or config files modified.
3. **Engine Safety:** 0 Unreal Editor instances started. Both C-1155 locks remain untouched and absent.
4. **Git Safety:** 0 git commits, 0 git pushes performed.
5. **Audition Directory Hygiene:** `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\` was confirmed non-existent prior to creation; no pre-existing files overwritten.
6. **Clock Normalization:** All inputs resampled via ffmpeg `aformat=sample_rates=48000:channel_layouts=stereo` before concatenation; zero sample clock drift.
7. **Task Board Status:** All five tasks (`BT-118`, `BT-117`, `BT-115`, `BT-119`, `BT-116`) advanced to `review`.
