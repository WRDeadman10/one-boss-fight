# C-1651 Owner SFX Audition Pick Sheet

- **Date:** 2026-11-18
- **Directives:** [TEAM_MAILBOX.md](../TEAM_MAILBOX.md) `[X-2688]`, `[C-1650]`, `[C-1651]`, Task `BT-169`
- **Author:** Antigravity (Implementer)
- **Reviewer / Lead:** Codex (Technical Lead)
- **Status:** READY FOR OWNER REVIEW & SELECTION (Zero sound choices made; purely Owner decision)

---

## 1. Overview & Instructions for Project Owner

This document provides a single, consolidated review sheet for all currently playable SFX audition reels prepared under **C-1651 Audio/SFX Batches 1 and 2**.

- **How to Audition:** Play the consolidated reel (`C1651_Batch2_Full_Audition.mp3` or `.wav`) to preview all Batch 2 boss attacks in sequence, or inspect individual event reels for focused listening.
- **Normalization:** All audition reels have been normalized to **48.0 kHz stereo 16-bit PCM** with standardized 1.0-second silence spacers between candidate options.
- **How to Submit Selections:** Copy the [Owner Selection Response Template](#4-owner-selection-response-template) at the bottom of this document, fill in your choice (`Option A`, `Option B`, `Option C`, or `None`) for each event, and paste it into [Documentation/TEAM_MAILBOX.md](../TEAM_MAILBOX.md).

---

## 2. Playable Audition Reels (SFX-10 & SFX-11..15)

### 2.1. SFX-10: Boss Stance Break Heavy Impact & Collapse (Batch 1 / BT-109)
- **Combat Context:** Triggered on boss posture/poise broken threshold (`OnStanceBroken`). Signals critical vulnerability window for player riposte.
- **Direct Reel Paths:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch1_SFX10\C1651_SFX10_StanceBreak_Audition.wav` (1,446,060 bytes, 9.812s)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch1_SFX10\C1651_SFX10_StanceBreak_Audition.mp3` (395,014 bytes)
- **Candidate Options in Reel:**
  - **Option A:** Heavy Stone Masonry Collapse (`/Game/StarterContent/Audio/Collapse01`) — Deep structural rubble shudder and stone crash.
  - **Option B:** Resonant Guardian Impact Crunch (`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/Sounds/Creatures/Guardian/A_Guardian_Impact02`) — Dense, kinetic blunt impact with debris transient.
  - **Option C:** Layered Low-End Guardian Impact Cue (`/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue`) — Sub-bass body with heavy metallic reverberation tail.

---

### 2.2. Consolidated Batch 2 Reel: Boss Attacks & Heavy Whooshes (SFX-11..15)
- **Combat Context:** Sevarog's core melee moveset (A1 slash, A2 overhead, A3 ground stomp, Mid01 forward thrust, Sprint gap-closer sweep).
- **Direct Consolidated Reel Paths:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_Batch2_Full_Audition.wav` (5,458,910 bytes, 28.431s)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_Batch2_Full_Audition.mp3` (683,756 bytes)

---

### 2.3. Individual Event Reels: Batch 2 (SFX-11..15)

#### SFX-11: Boss A1 Horizontal Slash High-Speed Blade Air Whoosh (BT-118)
- **Combat Context:** Horizontal sweeping blade arc; primary dodge/parry telegraph.
- **Direct Reel Paths:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX11_A1_HorizontalSlash_Audition.wav` (943,462 bytes, 4.913s)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX11_A1_HorizontalSlash_Audition.mp3` (119,276 bytes)
- **Candidate Options:**
  - **Option A (Preferred):** Medium Blade Cleave (`Sword_Attack_1_Cue`) — Crisp, cutting arc with high-tension metallic edge.
  - **Option B:** Swift Velocity Swoosh (`Swoosh_1_Cue`) — Sharp high-velocity swoosh; emphasizes rapid blade speed.
  - **Option C:** Standard Sword Swing (`A_Sword_Swing_Cue`) — Balanced standard swing from combat pack.

#### SFX-12: Boss A2 Overhead Cleave Heavy Weight Displacement (BT-117)
- **Combat Context:** Vertical overhead smash; high-damage downward cleave.
- **Direct Reel Paths:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX12_A2_OverheadCleave_Audition.wav` (1,069,922 bytes, 5.572s)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX12_A2_OverheadCleave_Audition.mp3` (135,404 bytes)
- **Candidate Options:**
  - **Option A (Preferred):** Heavy Weapon Whoosh (`A_Hammer_Swing_Cue`) — Massive low-end air displacement.
  - **Option B:** Resonant Blade Drop (`Sword_Attack_6_Cue`) — Aggressive downward cutting transient with blade flutter.
  - **Option C:** High-Mass Air Tear (`Swoosh_2_Cue`) — Deep velocity tear conveying heavy downward momentum.

#### SFX-13: Boss A3 Ground Stomp Earth Impact & Sub-Bass Thud (BT-115)
- **Combat Context:** Boss foot/staff slam creating local shockwave; close-range knockdown telegraph.
- **Direct Reel Paths:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX13_A3_GroundStomp_Audition.wav` (1,347,530 bytes, 7.018s)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX13_A3_GroundStomp_Audition.mp3` (169,964 bytes)
- **Candidate Options:**
  - **Option A (Preferred):** Guardian Stone Impact (`A_Guardian_Impact02`) — Dense stone compression thud with gravel displacement.
  - **Option B:** Masonry Shudder Collapse (`Collapse02`) — Extended low-frequency rubble collapse tail.
  - **Option C:** Heavy Armor Stomp (`Footstep_Concrete_Boots_Land_4_Cue`) — Punchy kinetic footfall transient.

#### SFX-14: Boss Mid01 Forward Thrust Precision Piercing Whoosh (BT-119)
- **Combat Context:** Linear forward thrust attack; tight directional dodge window.
- **Direct Reel Paths:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX14_Mid01_ForwardThrust_Audition.wav` (1,011,770 bytes, 5.269s)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX14_Mid01_ForwardThrust_Audition.mp3` (127,916 bytes)
- **Candidate Options:**
  - **Option A (Preferred):** Narrow Linear Air Cut (`Sword_Attack_Short_1_Cue`) — Focused, piercing transient whistle.
  - **Option B:** Rapid Thrust Swoosh (`Swoosh_3_Cue`) — Fast, narrow air displacement with minimal ring-out.
  - **Option C:** Extended Blade Slide (`Sword_Attack_7_Cue`) — Elongated blade slide with subtle ring.

#### SFX-15: Boss Sprint Gap-Closer Momentum Sweep Whoosh (BT-116)
- **Combat Context:** Sprint charge transitioning into wide horizontal momentum sweep.
- **Direct Reel Paths:**
  - WAV: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX15_Sprint_GapCloser_Audition.wav` (1,086,538 bytes, 5.659s)
  - MP3: `D:\FightVideo\SFX_audition\C1651_Batch2_SFX11_15\C1651_SFX15_Sprint_GapCloser_Audition.mp3` (137,132 bytes)
- **Candidate Options:**
  - **Option A (Preferred):** Sweeping Momentum Whoosh (`Sword_Attack_2_Cue`) — Heavy momentum carry with broad blade sweep.
  - **Option B:** Heavy Velocity Hammer Swing (`A_Hammer_Swing_Cue`) — Wide, dense air displacement for heavy momentum.
  - **Option C:** High-Speed Wide Edge (`Sword_Attack_8_Cue`) — Sharp cutting arc with rapid dissipation.

---

## 3. Status of SFX-06..09 (Batch 1: Player Attacks & Guard Counter)

> [!IMPORTANT]
> **SFX-06 through SFX-09 currently lack playable audition reels.**

- **Why Reels Are Not Present:** All 12 candidate Sound Cue `.uasset` packages exist and are verified in-tree (see [C1651_SFX_BATCH1_CANDIDATE_MATRIX.md](C1651_SFX_BATCH1_CANDIDATE_MATRIX.md)), but raw `.wav` audio has not been extracted to disk. Per [BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md](BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md), raw audio export is held pending Owner direction.
- **Events Affected:**
  - `SFX-06` (BT-112): Guard Counter Clash and Heavy Impact
  - `SFX-07` (BT-110): Light Attack 1 Swing Whoosh
  - `SFX-08` (BT-113): Light Attack 2 Swing Whoosh
  - `SFX-09` (BT-111): Light Attack 3 Swing Whoosh
- **Required Action to Prepare SFX-06..09 Reels:**
  - If the Owner desires playable audition reels for SFX-06..09, authorize a read-only Unreal Editor C-1155 export pass to dump raw WAVs from the verified `.uasset` packages into `D:\FightVideo\SFX_audition\RawWavs\`.
  - Alternatively, the Owner may authorize direct selection from the candidate specifications in [C1651_SFX_BATCH1_CANDIDATE_MATRIX.md](C1651_SFX_BATCH1_CANDIDATE_MATRIX.md) without building reels.

---

## 4. Owner Selection Response Template

To submit your selections, please copy and paste the block below into [Documentation/TEAM_MAILBOX.md](../TEAM_MAILBOX.md):

```markdown
### [O-XXXX] Owner -> Codex, Antigravity, Claude, YYYY-MM-DD HH:MM
SUBJECT: C-1651 SFX Audition Selections (Batch 1 & Batch 2)

#### Batch 1 Selections:
- SFX-10 (Boss Stance Break): [ Option A / Option B / Option C / None ]

#### Batch 2 Selections:
- SFX-11 (Boss A1 Horizontal Slash): [ Option A / Option B / Option C / None ]
- SFX-12 (Boss A2 Overhead Cleave):   [ Option A / Option B / Option C / None ]
- SFX-13 (Boss A3 Ground Stomp):      [ Option A / Option B / Option C / None ]
- SFX-14 (Boss Mid01 Forward Thrust): [ Option A / Option B / Option C / None ]
- SFX-15 (Boss Sprint Gap-Closer):    [ Option A / Option B / Option C / None ]

#### Direction for SFX-06..09 (Batch 1 Attacks / Guard Counter):
- [ ] Authorize read-only Editor export pass to generate playable audition reels for SFX-06..09
- [ ] Approve candidate packages directly from C1651_SFX_BATCH1_CANDIDATE_MATRIX.md without generating reels
- [ ] Defer SFX-06..09 until after Boss attacks are wired

#### Direction for Runtime Wiring:
- [ ] Authorize Lead Codex to schedule discrete runtime wiring tasks for approved picks
```

---

## 5. Discipline & Boundary Verification

- **Integrity Validation:** `check_doc_links.py` reports `broken_links=0`; `test_sevarog_sfx_cue_plan.py` passes cleanly (4/4 tests OK).
- **Strict Guardrails Preserved:**
  - Zero audio files exported, resampled, or modified.
  - Zero Unreal Editor instances launched.
  - Zero `.uasset` files, project configs, or C++ source files edited.
  - Zero git commits or pushes.
