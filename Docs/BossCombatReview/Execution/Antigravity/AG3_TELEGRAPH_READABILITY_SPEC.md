# AG-3: Telegraph and Readability Specification for P1

**Document ID:** `AG3_TELEGRAPH_READABILITY_SPEC` (Rev 01)  
**Date:** 2026-10-25  
**Author:** Antigravity (Accountable Visual & Technical Animation Investigator)  
**Addressed to:** Claude (Technical Lead & Editor Owner), Codex GPT-6 Astra (Technical Reviewer & Data Architect), Project Owner  
**Context & Authority:** Task AG-3 of Work Order 01 (`ANTIGRAVITY_WORK_ORDER_01.md`). Design input only; no runtime tuning, no editor sessions, no asset modifications.  
**Evidence Baseline:** `Claude/Evidence/exports/montage_notifies_2026-10-25.txt`, 26 machine move sheets (`movesheets/*.json`), and Authoring Contract Rev 03.

---

## 1. Executive Summary & Epistemological Boundaries

This specification audits the complete 14-move live inventory of Boss01 (Ember Warden), defining for each move:
1. **The First Perceptible Cue:** The earliest physical frame or acoustic signal communicating impending danger.
2. **Cue Modalities:** How the telegraph is expressed across Pose/Silhouette, VFX, Audio, Camera, and UI.
3. **Timeline Alignment:** Measured temporal intervals between First Cue, Commit Event, Active Window Start, and Damage Peak.
4. **Accessibility Standards:** Dual-modality redundancy (never relying solely on color hue or subtle VFX particles) and visual readability under reduced graphics settings.
5. **Owner Feel Questions:** Key aesthetic and gameplay pacing decisions reserved exclusively for the project owner.
6. **Measurable Verification Tests:** Concrete, machine-verifiable assertions for future automated captures or test drivers.

> [!NOTE]
> **Epistemological Boundary on 'First Perceptible Cue at 0.000s':** All '0.000s / Frame 0' cue markers represent an **offline authoring reading** of animation sequence frame 0 poses and declared sidecar intent. They are declared/offline parameters, NOT live-measured perceptual milestones observed in the engine. Real perceptual visibility depends on blend-in times (0.25s), camera framing, and lighting.

---

## 2. Summary Telegraph Readability Matrix

```
+------------+--------------------+---------------------+------------------+------------------+---------------------+
| Move ID    | Animation / Asset  | First Cue Type      | Cue Lead Time    | Commit Time      | Active Damage Window|
+------------+--------------------+---------------------+------------------+------------------+---------------------+
| **A1**     | `AM_Boss01_A1`     | High Blade Lift     | 330 ms (Frame 0) | 0.330 s          | 0.350 s - 0.500 s   |
| **A1b**    | `AN_Boss01_A1b`    | Hip Counter-Torque  | 200 ms (Frame 0) | 0.200 s          | 0.250 s - 0.450 s   |
| **A2**     | `GS_ChargedAttack` | Vertical Poise Rise | 1567 ms (Pack)   | 1.400 s (Est)    | 1.567 s - 1.760 s   |
| **A3a**    | `AM_Boss01_A3a`    | Underhand Floor Drag| 380 ms (Frame 0) | 0.380 s          | 0.400 s - 0.600 s   |
| **A3b**    | `AM_Boss01_A3b`    | Shoulder Pivot      | 130 ms (Frame 0) | 0.130 s          | 0.150 s - 0.400 s   |
| **A4**     | `AN_Boss01_A4`     | Low Crouch Stance   | 600 ms (Frame 0) | 0.400 s          | 0.609 s - 0.879 s   |
| **A5**     | `AN_Boss01_A5`     | Brazier Reach       | 400 ms (Frame 0) | 0.450 s          | 0.450 s - 0.470 s   |
| **A6**     | `GS_LeapAttack`    | Airborne Crouch/Jump| 754 ms (Frame 0) | 0.691 s          | 0.754 s - 1.175 s   |
| **Mid01**  | `Mid01_Anim`       | Forward Step Lunge  | 637 ms (Frame 0) | 0.615 s          | 0.637 s - 0.884 s   |
| **Sprint** | `GS_SprintAttack`  | Locomotion Lean     | ~37 ms (In-Mont) | 0.000 s (Immediate) 0.037 s - 0.230 s |
| **Retal**  | `RetaliationAttack`| Hyperarmor Flash    | 444 ms (Frame 0) | 0.257 s          | 0.444 s - 0.630 s   |
| **Wake**   | `Wake_Montage`     | Brazier Ignition    | 2000 ms          | N/A (Invulnerable) N/A (Intro)      |
| **Roar**   | `Roar_Montage`     | Skyward Arch Scream | 2500 ms          | N/A (Phase Lock) | N/A (Knockback)     |
| **Stagger**| `Stagger_Montage`  | Posture Shatter Snap| 3000 ms          | N/A (Vulnerable) | N/A (Riposte Target)|
+------------+--------------------+---------------------+------------------+------------------+---------------------+
```

---

## 3. Detailed Move-by-Move Telegraph Specifications

---

### 3.1 Move A1: Quick Slash (`AM_Boss01_A1` / `AN_Boss01_A1_QuickSlash`)

- **First Perceptible Cue:** Blade drawn vertically above right shoulder accompanied by vocal breath intake at $t = 0.000\text{ s}$ (Frame 0).
- **Modality Manifestation:**
  * **Pose / Silhouette:** Asymmetric silhouette tilt; right shoulder elevates $18\text{ cm}$, head pivots toward player.
  * **Audio:** Low intake hiss/vocal grunt ($0.000\text{ s}$), followed by high-velocity swing whoosh at $0.330\text{ s}$ (`AnimNotify_PlaySound`).
  * **VFX:** Subtle spark along right gauntlet grip.
  * **UI / Camera:** None (standard neutral attack).
- **Timeline Alignment:**
  * First Perceptible Cue: $0.000\text{ s}$.
  * Heading Commit Event: $0.330\text{ s}$ (`ANS_SetDesiredRotation_C` duration $0.330\text{ s}$).
  * Active Damage Window: $0.350\text{ s}$ to $0.500\text{ s}$ ($150\text{ ms}$; `ANS_CollisionTrace_C`).
  * Total Human Reaction Lead Time: **$330\text{ ms}$** (conforms to standard $250\text{--}350\text{ ms}$ reaction threshold).
- **Accessibility Standards:** High-contrast blade silhouette against background; audio intake cue is distinct in frequency (400 Hz), ensuring hearing-impaired players can rely entirely on the arm silhouette, while visually impaired players have a clear audio lead.
- **Owner Feel Questions:**
  1. *Does $330\text{ ms}$ reaction time from an idle state feel too twitchy or sudden for a heavy armored boss?*
  2. *Should A1 have a mandatory neutral recovery pause before branching to A1b?*
- **Measurable Verification Tests:**
  * Engine assert: `CommitTime == 0.330s` ($\pm 0.020\text{ s}$).
  * Frame capture assert: Bone `hand_r` achieves maximum windup height by $0.250\text{ s}$.

---

### 3.2 Move A1b: Quick Slash Combo Follow-up (`AN_Boss01_A1b_QuickSlashCombo`)

- **First Perceptible Cue:** Rapid counter-torque of hips and reverse backswing initiation during A1 recovery ($t = 0.000\text{ s}$ of A1b).
- **Modality Manifestation:**
  * **Pose / Silhouette:** Weight shifts to back foot; torso snaps across centerline.
  * **Audio:** Sharp rising blade whistle.
  * **VFX:** Dual horizontal light arc.
- **Timeline Alignment:**
  * First Cue: $0.000\text{ s}$.
  * Commit Time: $0.200\text{ s}$.
  * Active Window: $0.250\text{ s}$ to $0.450\text{ s}$ ($200\text{ ms}$).
  * Reaction Lead Time: **$200\text{--}250\text{ ms}$** (justified by combo anticipation from A1).
- **Accessibility Standards:** Rhythmic audio cadence ("slash... slash") establishes timing without needing visual precision.
- **Owner Feel Questions:**
  1. *Should A1b be guaranteed if A1 hits, or should the player always have an escape roll window?*
- **Measurable Verification Tests:**
  * Branch test: A1b cannot initiate unless A1 reached its active damage window.

---

### 3.3 Move A2: Delayed Overhead Slam (`GS_ChargedAttack_Montage` / Authored Trio)

- **First Perceptible Cue:** Blade raised two-handed directly overhead into vertical apex hold ($t = 0.000\text{ s}$).
- **Modality Manifestation:**
  * **Pose / Silhouette:** Tall, towering silhouette. Boss arches backward, lifting greatsword completely above head.
  * **VFX:** Dorsal brazier erupts in intense orange flames; blade fuller gathers pulsating embers.
  * **Audio:** Rising pitch resonance hum during the hold; explosive metallic release crack $150\text{ ms}$ before downward stroke.
- **Timeline Alignment:**
  * First Cue: $0.000\text{ s}$.
  * Live Pack Active Window: Starts at $1.567\text{ s}$ (duration $193\text{ ms}$; second strike at $1.925\text{ s}$).
  * Authored Trio Target: Raise $0.500\text{ s}$, Variable Hold $0.300\text{--}1.000\text{ s}$, Slam $0.250\text{ s}$.
- **Accessibility Standards:** Audio release snap $150\text{ ms}$ before impact is essential for timing the roll, overcoming visual depth ambiguity when the sword descends toward the camera.
- **Owner Feel Questions:**
  1. *Pack twirl vs Authored static poise: Do you prefer the pack's continuous windmill twirl (E-005) or the heavy, threatening static apex hold?*
  2. *What is the maximum approved duration for the variable apex hold (e.g. 1.2s vs 2.0s)?*
- **Measurable Verification Tests:**
  * Capture assert: Zero rotational heading drift after commit time.
  * Audio assert: Release sound event precedes active trace start by exactly $150\text{ ms} \pm 20\text{ ms}$.

---

### 3.4 Move A3a: Heavy Underhand Sweep (`AM_Boss01_A3a` / `AN_Boss01_A3a_Combo1`)

- **First Perceptible Cue:** Deep crouch with greatsword dragged low behind right flank ($t = 0.000\text{ s}$).
- **Modality Manifestation:**
  * **Pose / Silhouette:** Wide stance, torso lowered $30\text{ cm}$, blade resting on stone floor.
  * **VFX:** Continuous shower of floor-scraping friction sparks along arena tiles.
  * **Audio:** Heavy grinding stone-scrape sound from $0.000\text{ s}$ to $0.380\text{ s}$.
- **Timeline Alignment:**
  * First Cue: $0.000\text{ s}$.
  * Commit Time: $0.380\text{ s}$ (`ANS_SetDesiredRotation_C`).
  * Active Damage Window: $0.400\text{ s}$ to $0.600\text{ s}$ ($200\text{ ms}$; `ANS_CollisionTrace_C`).
  * Follow-up Window: Opens at $0.750\text{ s}$ (`AN_PerformFollowUp_C`).
- **Accessibility Standards:** High-contrast spark particles on the dark arena floor clearly outline the weapon's trajectory.
- **Owner Feel Questions:**
  1. *Does the low underhand drag provide enough silhouette change when viewed directly from the front?*
- **Measurable Verification Tests:**
  * Heading tracking locks at $0.380\text{ s} \pm 0.020\text{ s}$.
  * Ground contact trace confirms tip remains within $10\text{ cm}$ of floor plane during drag.

---

### 3.5 Move A3b: Overhead Hammer-Strike (`AM_Boss01_A3b` / `AN_Boss01_A3b_Combo2`)

- **First Perceptible Cue:** Immediate upward snap over left shoulder following A3a recovery ($t = 0.000\text{ s}$).
- **Modality Manifestation:**
  * **Pose / Silhouette:** Both arms lock above left collarbone; downward vertical descent.
  * **Audio:** Deep downward whoosh at $0.130\text{ s}$ (`AnimNotify_PlaySound`).
  * **VFX:** Fiery impact crater decal on ground impact.
- **Timeline Alignment:**
  * First Cue: $0.000\text{ s}$.
  * Commit Time: $0.130\text{ s}$ (`ANS_SetDesiredRotation_C`).
  * Active Damage Window: $0.150\text{ s}$ to $0.400\text{ s}$ ($250\text{ ms}$; `ANS_CollisionTrace_C`).
  * Montage End: $1.313\text{ s}$ (`AN_EndAnimatingAbility_C`).
- **Accessibility Standards:** Vertical downward strike path provides high orthogonal contrast against A3a's horizontal arc.
- **Owner Feel Questions:**
  1. *Given the rapid $130\text{ ms}$ commit, should A3b strictly cancel if the player successfully dodged behind the boss on A3a?*
- **Measurable Verification Tests:**
  * Verification that A3b cannot be selected in isolation without A3a precursor.

---

### 3.6 Move A4: Ground Low Sweep (`AN_Boss01_A4_LowSweep` / `RPGBossLowSweep`)

- **First Perceptible Cue:** Extreme low crouch with greatsword held parallel to floor at knee height ($t = 0.000\text{ s}$).
- **Modality Manifestation:**
  * **Pose / Silhouette:** Horizontal blade line spanning $300\text{ cm}$ width; crouched root.
  * **VFX:** Planar red/orange dust disc skimming the floor surface.
  * **Audio:** Low hum with heavy metallic scraping resonance.
  * **UI:** Jump counterplay prompt / icon (or distinct visual grounding cue).
- **Timeline Alignment:**
  * First Cue: $0.000\text{ s}$.
  * Code Commit Time: $0.400\text{ s}$ (Heading lock).
  * Active Planar Query Window: $0.609\text{ s}$ to $0.879\text{ s}$ ($270\text{ ms}$; 12 ticks in E-008).
- **Accessibility Standards:** Planar effect must have distinct vertical boundaries ($40\text{ cm}$ height); ground dust ring allows players to judge jump timing without relying on blade angle.
- **Owner Feel Questions:**
  1. *RV-07 / VIS-04: The query reaches $380\text{ cm}$, extending $\ge 68\text{ cm}$ beyond the visible blade tip ($312\text{ cm}$). Should we expand the sword mesh scale, extend a visible energy blade wave, or reduce the query reach to match the physical blade?*
- **Measurable Verification Tests:**
  * Player jump initiated at $0.330\text{ s}$ successfully clears the damage window (asserted in driver S3).

---

### 3.7 Move A5: Gauntlet Ember Javelin (`AN_Boss01_A5_JavelinThrow` / `RPGBossHealPunish`)

- **First Perceptible Cue:** Boss reaches left gauntlet back into the glowing dorsal brazier ($t = 0.000\text{ s}$).
- **Modality Manifestation:**
  * **Pose / Silhouette:** Distinct asymmetric reach behind back; right hand stabilizes greatsword in ground.
  * **VFX:** Brazier flares into intense blinding white-hot ember; fiery spear coalesces in left hand.
  * **Audio:** High-pitched piercing ignition sound ($0.000\text{ s}$); explosive launch sonic boom at release.
- **Timeline Alignment:**
  * First Cue: $0.000\text{ s}$.
  * Authored Hand Release: $0.400\text{ s}$ (Frame 12).
  * Tracker Code Commit / Active Window: $0.450\text{ s}$ (Observed spawn at $0.470\text{ s}$ in E-007).
- **Accessibility Standards:** Flash point at brazier is positioned high on the character model ($Z \approx 220\text{ cm}$), making it visible even when the boss's lower body is obscured by player third-person camera framing.
- **Owner Feel Questions:**
  1. *VIS-03: The code spawns the javelin at $0.45\text{--}0.47\text{ s}$, which is 1 to 1.4 frames after the authored hand release pose ($0.40\text{ s}$). Does this sub-frame lag feel perceptually disjointed in gameplay, or is it acceptable feel?*
- **Measurable Verification Tests:**
  * Projectile actor instantiation logged within $[0.450\text{ s}, 0.480\text{ s}]$.

---

### 3.8 Move A6: Phase 2 Leap Slam (`GS_LeapAttack_Montage` / `RPGBossShockwave`)

- **First Perceptible Cue:** Deep vertical compression crouch followed by massive rocket-assisted leap into the air ($t = 0.000\text{ s}$).
- **Modality Manifestation:**
  * **Pose / Silhouette:** Boss leaves the ground entirely, silhouette framed against sky/ceiling ($0.150\text{--}0.700\text{ s}$).
  * **VFX:** Launch dust crater; ground-expanding shockwave ring upon slam ($200\text{--}1100\text{ cm}$).
  * **Audio:** Thunderous launch roar; whistle of falling mass; shattering concussive impact boom on slam.
  * **Camera:** Camera pitch tilts slightly upward to track apex; radial screen shake on landing.
- **Timeline Alignment:**
  * Leap Launch: $0.000\text{ s}$.
  * Airborne Tracking Freeze: $0.691\text{ s}$ (`ANS_SetDesiredRotation_C`).
  * Slam Impact & Wave Start: $0.754\text{ s}$.
  * Wave Expansion: $0.754\text{ s}$ to $1.650\text{ s}$ ($1000\text{ cm/s}$ out to $1100\text{ cm}$).
- **Accessibility Standards:** Shockwave ring must render with explicit vertical geometric thickness and ground debris, enabling jump counterplay ($50\text{ cm}$ clearance) without color dependence.
- **Owner Feel Questions:**
  1. *RV-01: In Shipping builds, `DrawDebugCircle` compiles out. What visual style of production VFX ring (Niagara fire ring vs fractured stone shockwave) is approved for the expanding damage band?*
- **Measurable Verification Tests:**
  * Jump counterplay assertion: Player capsule elevated $> 50\text{ cm}$ takes zero damage at radius $600\text{ cm}$.

---

### 3.9 Move Mid01: Mid-Range Closing Slash (`Mid01_Anim_Montage`)

- **First Perceptible Cue:** Wide lateral lunging step forward with greatsword dragging behind ($t = 0.000\text{ s}$).
- **Modality Manifestation:**
  * **Pose / Silhouette:** Long, elongated forward lunge ($400\text{ cm}$ stride).
  * **Audio:** Heavy armored footstep thud at $0.127\text{ s}$; sweeping blade whoosh at $0.627\text{ s}$.
  * **VFX:** Ground stone friction sparks.
- **Timeline Alignment:**
  * First Cue: $0.000\text{ s}$.
  * Tracking Commit: $0.615\text{ s}$ (`ANS_SetDesiredRotation_C` ends).
  * Active Damage Window: $0.637\text{ s}$ to $0.884\text{ s}$ ($247\text{ ms}$; `ANS_CollisionTrace_C`).
  * Total Reaction Window: **$637\text{ ms}$** (Very generous telegraph).
- **Accessibility Standards:** Audible footstep thud at $0.127\text{ s}$ signals commit phase beginning.
- **Owner Feel Questions:**
  1. *Is the $637\text{ ms}$ windup too slow for an aggressive boss gap-closer, allowing players to easily interrupt or retreat?*
- **Measurable Verification Tests:**
  * Trace window active bounds $[0.637\text{ s}, 0.884\text{ s}]$.

---

### 3.10 Sprint Attack: Dash & Follow-Up (`GS_SprintAttackFollowUp_Montage` / `GA_GS_Boss_SprintAttack`)

- **Telegraph Reality & Run-Up Phase:**
  * The parent ability `GA_GS_Boss_SprintAttack` executes an approach sprint phase (speed $800\text{ cm/s}$, duration limit $1.5\text{ s}$, follow-up trigger range $200\text{ cm}$; documented in Claude's E-002 Addendum 2).
  * **The actual visible telegraph is the continuous approach run-up** as the boss charges across the arena toward the player.
  * The $37\text{ ms}$ damage onset occurs within the *follow-up montage* (`GS_SprintAttackFollowUp_Montage`), which is triggered once the sprint closes to within $200\text{ cm}$.
- **Modality Manifestation:**
  * **Locomotion Run-Up (Primary Telegraph):** Fast charging gallop with blade trailing; ground footsteps rumble.
  * **Follow-up Montage Transition:** Torso drops forward into deceleration lean; blade sweeps horizontally across centerline.
  * **Audio:** Heavy sprint footsteps during approach; blade slash sound at $0.037\text{ s}$ of follow-up.
  * **VFX:** Dual horizontal spark trails.
- **Timeline Alignment:**
  * Sprint Approach Phase: Up to $1.500\text{ s}$ at $800\text{ cm/s}$ (Primary Telegraph).
  * Follow-up Montage Trigger: Upon entering $200\text{ cm}$ range.
  * Follow-up Strike 1 Active: $0.037\text{ s}$ to $0.230\text{ s}$ ($193\text{ ms}$; immediate damage).
  * Follow-up Strike 2 Active: $0.364\text{ s}$ to $0.551\text{ s}$ ($187\text{ ms}$).
- **Accessibility Standards:** Readability is provided by the sprint approach trajectory; player must react to the charging sprint before the follow-up montage is invoked.
- **Owner Feel Questions:**
  1. *Does the sprint charge give the player sufficient telegraph to dodge before the 200 cm follow-up threshold, or does the 37 ms follow-up feel abrupt if triggered from behind?*
  2. *Proposal for Review: An enforced 200 ms slide-in braking section is proposed as a design option, but strictly requires runtime video capture of the live run-up first before tuning.*
- **Measurable Verification Tests:**
  * Collision trace timing in follow-up verified at $[0.037\text{ s}, 0.230\text{ s}]$.

---

### 3.11 Retaliation Attack: Hyperarmor Counter (`RetaliationAttack_Montage`)

- **First Perceptible Cue:** Blinding golden/white hyperarmor aura erupts across boss chest armor at $t = 0.000\text{ s}$.
- **Modality Manifestation:**
  * **Pose / Silhouette:** Braced, immovable stance; sword held diagonally across chest.
  * **Audio:** Resonant metallic "deflection ping" on frame 0; heavy counter-slash whoosh at $0.446\text{ s}$.
  * **VFX:** Persistent golden shimmer (`ANS_HitStunImmune_C`) from $0.000\text{ s}$ to $1.267\text{ s}$.
- **Timeline Alignment:**
  * Hyperarmor Activation: $0.000\text{ s}$ (Frame 0).
  * Tracking Commit: $0.257\text{ s}$ (`ANS_SetDesiredRotation_C`).
  * Active Damage Window: $0.444\text{ s}$ to $0.630\text{ s}$ ($186\text{ ms}$; `ANS_CollisionTrace_C`).
- **Accessibility Standards:** Dual visual shimmer + sharp acoustic ping guarantees players immediately understand that attacking the boss will not interrupt the incoming blow.
- **Owner Feel Questions:**
  1. *Does the hyperarmor duration ($1.267\text{ s}$) feel fair, or should stagger break through if the player lands a heavy charged attack?*
- **Measurable Verification Tests:**
  * Assert `HitStunImmune` tag present from $0.000\text{ s}$ to $1.267\text{ s}$.

---

### 3.12 Wake State (`Wake_Montage` / `AN_Boss01_Wake`)

- **First Perceptible Cue:** Dorsal brazier ignites with deep fiery explosion; red embers rain onto floor ($t = 0.000\text{ s}$).
- **Modality Manifestation:**
  * **Pose:** Boss rises from kneeling dormant pose, standing to full $350\text{ cm}$ height.
  * **Audio:** Stone grinding, echoing demonic breathing, deep bass ignition.
  * **Camera:** Camera pulls back smoothly to establish $600\text{ cm}$ duel distance.
- **Accessibility Standards:** Safe intro interval; boss cannot deal or receive damage until wake completes ($2.000\text{ s}$).
- **Owner Feel Questions:**
  1. *Should player input be locked during Wake, or should player be allowed free movement to position themselves?*

---

### 3.13 Roar / Phase 2 Transition (`Roar_Montage` / `PhaseTransition`)

- **First Perceptible Cue:** Boss recoils backward, crossguard sparks violently, and sword is driven into ground ($t = 0.000\text{ s}$).
- **Modality Manifestation:**
  * **Pose:** Arched back, head thrown back in skyward scream.
  * **Audio:** Ear-splitting roar with low-frequency ear-ringing ducking effect on background music.
  * **VFX:** Concussive shockwave blast knocking player back $400\text{ cm}$ (zero damage).
  * **UI:** Boss health bar pulses and changes border styling to indicate Phase 2.
- **Accessibility Standards:** Concussive knockback creates physical separation, ensuring the player is safely pushed out of melee range to observe the transformation.
- **Owner Feel Questions:**
  1. *Should the roar deal minor poise damage or remain strictly a non-damaging spatial separator?*

---

### 3.14 Stagger / Posture Break (`Stagger_Montage` / `AN_Boss01_Stagger`)

- **First Perceptible Cue:** Loud crystalline posture-break sound cue + boss drops sword tip and collapses to one knee ($t = 0.000\text{ s}$).
- **Modality Manifestation:**
  * **Pose:** Bowed head, sword leaning limply, core chest armor exposed.
  * **Audio:** High-frequency glass shatter followed by deep metallic armor collapse clatter.
  * **VFX:** Glowing orange/gold critical strike reticle appears over `SOCKET_Riposte` on boss chest.
  * **UI:** Action prompt `[R1 / Light Attack: Riposte]` appears on HUD.
- **Timeline Alignment:**
  * Total Vulnerability Duration: $3.000\text{ s}$ ($3000\text{ ms}$).
  * Riposte Window: Active from $0.200\text{ s}$ to $2.800\text{ s}$.
- **Accessibility Standards:** Audio shatter cue has a 3 kHz transient audible over all explosions; visual reticle pulses with high luminosity (300 nits) to guide the player.
- **Owner Feel Questions:**
  1. *Is $3.0\text{ s}$ sufficient time for a player who was knocked down to stand up, run forward, and execute the riposte?*
- **Measurable Verification Tests:**
  * Posture break duration strictly adheres to $3.000\text{ s} \pm 0.050\text{ s}$.

---

## 4. Evidence and Limits

| Claim / Field | Source File / Anchor | Kind | Status / Limit |
| :--- | :--- | :--- | :--- |
| Live Montage Notifies (A1, A3a, A3b, Mid01, Retaliation, Sprint, ChargedAttack) | `Claude/Evidence/exports/montage_notifies_2026-10-25.txt` | Engine Export | Exact notify timings read from live asset inspection |
| Sprint Attack Parameters (Speed 800, Range 200, Limit 1.5s) | `Claude/Evidence/E-002_live_route_and_attack_inventory.md` Addendum 2 | Engine Blueprint Export | Documented approach parameters; live run-up visual capture pending |
| A4 Sweep Query Reach (380 cm vs 312 cm visible tip) | `Claude/Evidence/E-008_CAP02_A4_query_vs_visible_blade.md` | Engine Probe | Measured geometric discrepancy in forced test; visual check pending |
| A5 Projectile Release (0.45s code vs 0.40s authored sidecar) | `Claude/Evidence/E-007_CAP01_A5_release_timing.md` | Engine Log Sample | 0.05s nominal / 0.07s observed difference; visual sync unverified |
| A2 Early Stop Defect (9 of 11 stopped early) | `Claude/Evidence/E-005_A2_early_stop.md` | Engine Log Trace | Observed bot-run symptom; internal software canceller unidentified |
| First Perceptible Cues (0.000s) | 26 Move Sheets (`movesheets/*.json`) | Declared Authoring Intent | Offline sidecar analysis; in-engine perceptual recognition unverified |

### What Could NOT Be Verified Offline:
1. Perceptual human reaction lead time cannot be verified without synchronized video captures of gameplay in the editor.
2. Sprint attack run-up visual readability cannot be evaluated without recording the full approach locomotion sequence.
3. Accessibility contrast under reduced post-processing cannot be measured without rendering in the viewport.
