# D3 Reference Measurement Findings (2 of 9 Clips Measured)

> **Status:** DESIGN INPUT (measured from owner footage, observation only).  
> **Rule:** Observations are qualitative design aids. Strictly **NO** numbers from this review may be applied to runtime gameplay assets or Ember Warden cards without an explicit owner decision.  
> **Methodology:** Video standard 59.9401 FPS, combat zero $t_0 = 105.000\text{ s}$, canonical formula $\text{frame} = \text{round}((t_{\text{orig}} - 105.0) \times 59.9401) + 1$.

---

## 1. Measured Combat Summary Table

The following table summarizes all clips measured to date in `Docs/BossCombatReview/Execution/Claude/D3/D3_MEASURED_LEDGER.json`, generated via `D3_findings_table.py`:

| Priority | Reference ID | Original Move ID | Key Frames (W/C/A/E/R/RE) | Windup | Active | Recovery | Total | Confidence | Camera & Observation Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `REF_HolySwordRain_Setup` | `Move_EmberWarden_SwordRain` | W=2381 C=2423 A=2566 E=2602 R=2620 RE=2818 | 3.0864s (185f) | 0.6006s (36f) | 3.6036s (216f) | 7.2906s (437f) | **low** | camera: behind player, boss small and far away, boss body not readable; this measures the SKY SWORD VOLLEY, not the boss animation. W = swords begin to materialise at the top of frame 144.75 s (+-6 f, none at 144.611, present at 144.811), C = first single sword drop 145.412 s, A = main volley impact flash 147.814 s, E = volley impacts finish ~148.415 s, R = all swords planted 148.7 s (they persist as a ground hazard until at least 156 s), RE = boss starts its next move (leap/dash in) ~152.0 s; observation only from owner footage |
| 2 | `REF_MaceSlam_Sweep` | `Move_EmberWarden_MaceSlam` | W=1703 C=1787 A=1796 E=1801 R=1835 RE=1871 | 1.5515s (93f) | 0.0834s (5f) | 1.1678s (70f) | 2.8028s (168f) | **medium** | camera: boss in frame the whole clip, player mostly off screen; W = mace summon flash 133.400 s, hold ~1.3 s, sweep starts 134.801 s; first contact depends on player position; R/RE read at 0.1 s steps (+-3 frames); observation only from owner footage |

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
- **Confidence Rating:** **MEDIUM** (Windup summon flash and the rapid downward sweep are clearly visible in-frame; first contact point is dependent on player positioning).
- **What these numbers CAN be used for:**
  - Establishing macro telegraph pacing: a deliberate $\approx 1.3\text{--}1.55\text{ s}$ raised-weapon hold designed to bait premature player rolling.
  - Pacing the active strike: an extremely rapid, snappy ground sweep ($\approx 5\text{ frames} / 83\text{ ms}$) demanding precise evasion timing.
  - Quantifying recovery punishment opportunity: $\approx 1.17\text{ s}$ ($70\text{ frames}$) of actionable recovery, allowing the player 1–2 standard light counter-attacks.
- **What these numbers CANNOT be used for:**
  - Pinpoint player dodge i-frame alignment (the player was situated partially off-screen at sweep impact; exact collision onset depends on spatial overlap).
  - Direct parameter injection into Sevarog / Ember Warden runtime cards without designer validation.

---

### Clip 2: `REF_HolySwordRain_Setup` (`Move_EmberWarden_SwordRain`)
- **Key Milestones:** $W=2381$ ($144.706\text{ s}$), $C=2423$ ($145.407\text{ s}$), $A=2566$ ($147.793\text{ s}$), $E=2602$ ($148.393\text{ s}$), $R=2620$ ($148.694\text{ s}$), $RE=2818$ ($151.997\text{ s}$).
- **Calculated Durations:**
  - Windup / Volley Telegraph: $185\text{ frames}$ ($3.0864\text{ s}$)
  - Active Impact Volley: $36\text{ frames}$ ($0.6006\text{ s}$)
  - Recovery / Lingering Duration ($RE - E$): $216\text{ frames}$ ($3.6036\text{ s}$)
  - Recovery Tail ($RE - R$): $198\text{ frames}$ ($3.3033\text{ s}$)
  - Total Duration ($RE - W$): $437\text{ frames}$ ($7.2906\text{ s}$)
- **Confidence Rating:** **LOW** (The camera was positioned behind the player; the boss body was small, distant, and occluded. Timestamps measure the projectile volley arrival and environmental impact rather than skeletal animation keyframes).
- **What these numbers CAN be used for:**
  - Pacing multi-phase boss area denial: identifying that a massive sky-projectile attack uses a substantial $\approx 3.1\text{ s}$ telegraph before ground impacts commence.
  - Designing impact cluster density: a rapid impact burst lasting $\approx 0.6\text{ s}$ ($36\text{ frames}$).
  - Hazard persistence design: acknowledging that sword pillars remain planted in the ground creating an area denial hazard lasting well past the initial volley ($>156\text{ s}$), while the boss recovers and initiates subsequent attacks at $\approx 152\text{ s}$.
- **What these numbers CANNOT be used for:**
  - Boss skeletal animation card data (the boss was distant; bone transforms, montages, and AnimBP notify windows cannot be inferred from projectile VFX).
  - Hard collision timing (damage volume duration differs from projectile flight time).

---

## 3. DO NOT APPLY: Architectural Guardrail

> [!CAUTION]
> **Strict Non-Application Policy:**  
> All timings, frame counts, and durations recorded in this review and in `D3_MEASURED_LEDGER.json` represent observational reference measurements derived from third-party boss fight footage.  
> 
> Under **NO CIRCUMSTANCES** may any data from this study be copied, pasted, or injected into shipped gameplay assets or runtime cards located in `Content/OneBossFight/FrameworkProof/Cards/` without explicit, formal direction and sign-off from the project **Owner**.  
> 
> These metrics serve solely as qualitative reference baselines to assist in balancing attack tempo, telegraph windows, and recovery windows during future combat review sessions.
