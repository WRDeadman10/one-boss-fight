# D3 Reference Measurement Findings (4 of 10 Clips Measured)

> **Status:** DESIGN INPUT (measured from owner footage, observation only).  
> **Rule:** Observations are qualitative design aids. Strictly **NO** numbers from this review may be applied to runtime gameplay assets or Ember Warden cards without an explicit owner decision.  
> **Methodology:** Video standard 59.9401 FPS, combat zero $t_0 = 105.000\text{ s}$, canonical formula $\text{frame} = \text{round}((t_{\text{orig}} - 105.0) \times 59.9401) + 1$.

---

## 1. Measured Combat Summary Table

The following table summarizes all clips measured to date in `Docs/BossCombatReview/Execution/Claude/D3/D3_MEASURED_LEDGER.json`, generated via `D3_findings_table.py`:

| Ledger priority | Reference ID | Original Move ID | Key Frames (W/C/A/E/R/RE) | Windup | Active | Recovery | Total | Confidence | Camera & Observation Notes |
|---|---|---|---|---|---|---|---|---|---|
| 6 | `REF_HolySwordRain_Setup` | `Move_EmberWarden_SwordRain` | W=2381 C=2423 A=2566 E=2602 R=2620 RE=2818 | 3.0864s (185f) | 0.6006s (36f) | 3.6036s (216f) | 7.2906s (437f) | **low** | camera: behind player, boss small and far away, boss body not readable; this measures the SKY SWORD VOLLEY, not the boss animation. W = swords begin to materialise at the top of frame 144.75 s (+-6 f, none at 144.611, present at 144.811), C = first single sword drop 145.412 s, A = main volley impact flash 147.814 s, E = volley impacts finish ~148.415 s, R = all swords planted 148.7 s (they persist as a ground hazard until at least 156 s), RE = boss starts its next move (leap/dash in) ~152.0 s; observation only from owner footage |
| 8 | `REF_OmenCurseBurst_Phase2` | `Move_EmberWarden_CurseBurst` | W=5189 C=5270 A=5347 E=5612 R=5624 RE=5732 | 2.6360s (158f) | 4.4211s (265f) | 2.0020s (120f) | 9.0590s (543f) | **medium** | camera: steady, boss in frame and close during the buildup (190.8-194.1 s), then boss mid-distance behind the player for the burst; W = orange eye glow and embers start ~191.56 s (+-9 f), C = golden flame aura ignites ~192.91 s, A = golden detonation ~194.2 s (between 194.111 no burst and 194.261 burst, +-5 f), burst rays fade ~195.8 s, flame geysers across the arena erupt from ~196.2 s and burn until ~198.6 s (E = end of the flames), R = flames gone ~198.8 s, RE = next attack flare ~200.6 s (low certainty, boss small and far); NOT the boss's own recovery animation; observation only from owner footage |
| 9 | `REF_MaceSlam_Sweep` | `Move_EmberWarden_MaceSlam` | W=1703 C=1787 A=1796 E=1801 R=1835 RE=1871 | 1.5515s (93f) | 0.0834s (5f) | 1.1678s (70f) | 2.8028s (168f) | **medium** | camera: boss in frame the whole clip, player mostly off screen; W = mace summon flash 133.400 s, hold ~1.3 s, sweep starts 134.801 s; first contact depends on player position; R/RE read at 0.1 s steps (+-3 frames); observation only from owner footage |
| 10 | `REF_GapPounce_Close` | `Move_EmberWarden_GapPounce` | W=3951 C=3981 A=4005 E=4023 R=4047 RE=4065 | 0.9009s (54f) | 0.3003s (18f) | 0.7007s (42f) | 1.9019s (114f) | **low** | camera: boss far then fills the frame, close melee, player partly hidden; W = boss starts its run-in at the far right ~170.9 s (+-6 f), C = boss leaves the ground ~171.4 s, A = boss meets the player at ~171.8 s, E = boss passes through ~172.1 s, R = landing/turn ~172.5 s, RE = the NEXT attack (mace summon flash) starts ~172.8 s, so this is a CHAIN: 'recovery' is only the gap to the next move and is not a true recovery window; observation only from owner footage |

---

## 2. Qualitative Scope: Usable vs. Non-Usable Scopes per Clip

### Clip 1: `REF_MaceSlam_Sweep` (`Move_EmberWarden_MaceSlam`)
- **Key Milestones:** $W=1703$ ($133.395\text{ s}$), $C=1787$ ($134.796\text{ s}$), $A=1796$ ($134.947\text{ s}$), $E=1801$ ($135.030\text{ s}$), $R=1835$ ($135.597\text{ s}$), $RE=1871$ ($136.198\text{ s}$).
- **Calculated Durations:**
  - Windup: $93\text{ frames}$ ($1.5515\text{ s}$)
  - Active: $5\text{ frames}$ ($0.0834\text{ s}$)
  - Recovery ($RE - E$): $70\text{ frames}$ ($1.1678\text{ s}$)
  - Recovery Tail ($RE - R$): $36\text{ frames}$ ($0.6006\text{ s}$)
  - Total Duration ($RE - W$): $168\text{ frames}$ ($2.8028\text{ s}$)
- **Confidence Rating:** **MEDIUM** (Windup summon flash and the downward sweep are visible in-frame; the player is mostly off screen so first contact point depends on player distance).
- **What these numbers CAN be used for (Observations & Inferences for Design Review):**
  - Observed macro telegraph timing: the footage shows a raised mace hold lasting $84\text{ frames}$ ($1.4014\text{ s}$) before the sweep starts ($W \to C$), with total windup to first active strike lasting $93\text{ frames}$ ($1.5515\text{ s}$, $W \to A$). *(INFERENCE for design review: provides reference timing for an extended windup telegraph).*
  - Observed active strike duration: the footage shows the downward ground sweep completes its visual trail in $\approx 5\text{ frames}$ ($83\text{ ms}$). *(INFERENCE for design review: illustrates a brief, snappy strike release).*
  - Observed recovery duration: the footage shows the boss remains in recovery pose for $\approx 1.17\text{ s}$ ($70\text{ frames}$) after impact before reaching upright/idle pose at $136.2\text{ s}$. *(INFERENCE for design review: reference duration for recovery commitment; note that player counter-actions were not observed as the player was off screen).*
- **What these numbers CANNOT be used for:**
  - Pinpoint player dodge i-frame alignment (the player was situated off-screen at sweep impact; exact collision onset depends on spatial overlap).
  - Direct parameter injection into Ember Warden runtime cards without designer validation and owner decision.

---

### Clip 2: `REF_HolySwordRain_Setup` (`Move_EmberWarden_SwordRain`)
- **Key Milestones:** $W=2381$ ($144.706\text{ s}$), $C=2423$ ($145.407\text{ s}$), $A=2566$ ($147.793\text{ s}$), $E=2602$ ($148.393\text{ s}$), $R=2620$ ($148.694\text{ s}$), $RE=2818$ ($151.997\text{ s}$).
- **Calculated Durations:**
  - Windup / Volley Telegraph: $185\text{ frames}$ ($3.0864\text{ s}$)
  - Active Impact Volley: $36\text{ frames}$ ($0.6006\text{ s}$)
  - Recovery / Lingering Duration ($RE - E$): $216\text{ frames}$ ($3.6036\text{ s}$)
  - Recovery Tail ($RE - R$): $198\text{ frames}$ ($3.3033\text{ s}$)
  - Total Duration ($RE - W$): $437\text{ frames}$ ($7.2906\text{ s}$)
- **Confidence Rating:** **LOW** (The camera was positioned behind the player; the boss body was small, distant, and unreadable. Timestamps measure the sky sword volley VFX and ground impact flashes rather than boss skeletal animation).
- **What these numbers CAN be used for (Observations & Inferences for Design Review):**
  - Observed projectile telegraph timing: the footage shows sky swords begin materialising at the top of the frame $\approx 3.1\text{ s}$ ($185\text{ frames}$) before main volley ground impact flashes begin. *(INFERENCE for design review: informs macro telegraph pacing for long-range area setup).*
  - Observed impact volley duration: the footage shows ground impact flashes cluster across an interval of $\approx 0.6\text{ s}$ ($36\text{ frames}$). *(INFERENCE for design review: informs active volley cluster brevity).*
  - Observed hazard persistence: the footage shows sword pillars remain planted in the ground until at least $156\text{ s}$ ($>7\text{ s}$ after impact), while the boss initiates its next action (dash/leap in) at $\approx 152.0\text{ s}$. *(INFERENCE for design review: illustrates a persistent environmental hazard outlasting boss recovery).*
- **What these numbers CANNOT be used for:**
  - Boss skeletal animation card data (the boss was distant; bone transforms, montages, and AnimBP notify windows cannot be inferred from projectile VFX).
  - Hard collision timing (damage volume duration differs from projectile flight time).
  - Direct parameter injection into Ember Warden runtime cards without designer validation and owner decision.

---

### Clip 3: `REF_GapPounce_Close` (`Move_EmberWarden_GapPounce`)
- **Key Milestones:** $W=3951$ ($170.899\text{ s}$), $C=3981$ ($171.400\text{ s}$), $A=4005$ ($171.800\text{ s}$), $E=4023$ ($172.100\text{ s}$), $R=4047$ ($172.501\text{ s}$), $RE=4065$ ($172.801\text{ s}$).
- **Calculated Durations:**
  - Windup / Run-in & Leap: $54\text{ frames}$ ($0.9009\text{ s}$)
  - Active Traversal Strike: $18\text{ frames}$ ($0.3003\text{ s}$)
  - Recovery ($RE - E$): $42\text{ frames}$ ($0.7007\text{ s}$)
  - Recovery Tail ($RE - R$): $18\text{ frames}$ ($0.3003\text{ s}$)
  - Total Duration ($RE - W$): $114\text{ frames}$ ($1.9019\text{ s}$)
- **Confidence Rating:** **LOW** (Camera: boss is far then rapidly fills the frame, close melee, player is partly hidden).
- **What these numbers CAN be used for (Observations & Inferences for Design Review):**
  - Observed gap-close telegraph pacing: boss starts its run-in from the far right at $\approx 170.9\text{ s}$ ($W$, frame $3951$), leaves the ground at $\approx 171.4\text{ s}$ ($C$, frame $3981$, $30\text{ frames}$ / $0.50\text{ s}$ ground run), and meets the player at $\approx 171.8\text{ s}$ ($A$, frame $4005$, $54\text{ frames}$ / $0.90\text{ s}$ total windup). *(INFERENCE for design review: illustrates a medium-range gap closer with a bifurcated ground-run into leap telegraph).*
  - Observed active strike traversal: the aerial strike passes through player space from $171.8\text{ s}$ to $172.1\text{ s}$ ($18\text{ frames}$ / $0.3003\text{ s}$). *(INFERENCE for design review: snappy collision pass-through window).*
  - Observed combo chain timing: boss lands and turns at $\approx 172.5\text{ s}$ ($R$, frame $4047$) and initiates the NEXT attack (mace summon flash) at $\approx 172.8\text{ s}$ ($RE$, frame $4065$). **CHAIN: "recovery" ($42\text{ frames}$ / $0.7007\text{ s}$) is only the gap to the next move and is not a true recovery or punish window.** *(INFERENCE for design review: in combo strings, recovery values measure move-to-move chaining cadence rather than player punish vulnerability).*
- **What these numbers CANNOT be used for:**
  - Player punish window design (the move chains immediately into the next attack without neutral recovery).
  - Precise hurtbox/hitbox collision alignment (player was partially obscured during pass-through).
  - Direct parameter injection into Ember Warden runtime cards without designer validation and owner decision.

---

### Clip 4: `REF_OmenCurseBurst_Phase2` (`Move_EmberWarden_CurseBurst`)
- **Key Milestones:** $W=5189$ ($191.553\text{ s}$), $C=5270$ ($192.904\text{ s}$), $A=5347$ ($194.189\text{ s}$), $E=5612$ ($198.610\text{ s}$), $R=5624$ ($198.810\text{ s}$), $RE=5732$ ($200.612\text{ s}$).
- **Calculated Durations:**
  - Windup / Buildup & Aura Telegraph: $158\text{ frames}$ ($2.6360\text{ s}$)
  - Active (Detonation + Flame Geysers): $265\text{ frames}$ ($4.4211\text{ s}$)
  - Recovery ($RE - E$): $120\text{ frames}$ ($2.0020\text{ s}$)
  - Recovery Tail ($RE - R$): $108\text{ frames}$ ($1.8018\text{ s}$)
  - Total Duration ($RE - W$): $543\text{ frames}$ ($9.0590\text{ s}$)
- **Confidence Rating:** **MEDIUM** (Camera is steady; boss is close and clearly framed throughout the buildup from $190.8\text{ s}$ to $194.1\text{ s}$, then moves to mid-distance behind the player during the burst).
- **What these numbers CAN be used for (Observations & Inferences for Design Review):**
  - Observed phase transition / macro buildup telegraph: the footage shows the boss hunched with orange eye glow and embers beginning at $\approx 191.56\text{ s}$ ($W$, frame $5189$), igniting a golden flame aura at $\approx 192.91\text{ s}$ ($C$, frame $5270$, $81\text{ frames}$ / $1.35\text{ s}$ initial hunch), followed by an explosive golden detonation at $\approx 194.2\text{ s}$ ($A$, frame $5347$, $158\text{ frames}$ / $2.6360\text{ s}$ total windup). *(INFERENCE for design review: informs macro telegraph pacing for a major phase transition explosion).*
  - Observed hybrid active phase (instant burst + persistent hazard): the initial detonation occurs at frame $5347$ ($\approx 194.2\text{ s}$); explosive burst rays fade by $\approx 195.8\text{ s}$, while arena-wide flame geysers erupt from $\approx 196.2\text{ s}$ and continue burning until $\approx 198.6\text{ s}$ ($E$, frame $5612$). **The active duration ($265\text{ frames}$ / $4.4211\text{ s}$) combines both the instant primary detonation and the subsequent persistent arena flame hazard.** *(INFERENCE for design review: illustrates a compound move where primary shockwave transitions into area denial).*
  - Observed recovery and flare: flame geysers extinguish by $\approx 198.8\text{ s}$ ($R$, frame $5624$), followed by next attack flare at $\approx 200.6\text{ s}$ ($RE$, frame $5732$, $120\text{ frames}$ / $2.0020\text{ s}$ after active flames end). **NOTE: End milestone $E$ covers the arena geyser fire rather than the boss's own recovery animation, and $RE$ carries lower certainty due to distant framing.** *(INFERENCE for design review: boss action recovery must be distinguished from lingering spell VFX).*
- **What these numbers CANNOT be used for:**
  - Boss skeletal animation card data (the active end $E$ measures environmental fire FX persistence, not boss character animation).
  - Exact recovery vulnerability (boss recovery pose overlaps with arena flame hazard).
  - Direct parameter injection into Ember Warden runtime cards without designer validation and owner decision.

---

## 3. DO NOT APPLY: Architectural Guardrail

> [!CAUTION]
> **Strict Non-Application Policy:**  
> All timings, frame counts, and durations recorded in this review and in `D3_MEASURED_LEDGER.json` represent observational reference measurements derived from third-party boss fight footage.  
> 
> Under **NO CIRCUMSTANCES** may any data from this study be copied, pasted, or injected into shipped gameplay assets or runtime cards located in `Content/OneBossFight/FrameworkProof/Cards/` without explicit, formal direction and sign-off from the project **Owner**.  
> 
> These metrics serve solely as qualitative reference baselines to assist in balancing attack tempo, telegraph windows, and recovery windows during future combat review sessions.
