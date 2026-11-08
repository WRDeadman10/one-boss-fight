# Antigravity Full-Fight Video 2 Review

**Target:** `Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/fight_review2.mp4`  
**Properties:** 960x540, 25 fps, 722.04 s duration (12m 02s), 96.1 MB, H.264  
**Run Context:** Route `data` (`DA_Sevarog_G044_Encounter`), BUILD-259 baseline with all 7 Tier 2 & ER assets live (4 ER player montages, live Tier 2 presentation hooks enabled via `rpg.Art.Tier2 1`, A-633 GuardCounter timing). Boss defeated at 716.8 s (11:56.8) after 7202 captured frames and 79 player refills.

**Capture identity boundary:** This report covers BUILD-259 `fight_review2.mp4` only. BUILD-255 `fight_review.mp4` is a separate capture; its six black lead-in PNGs and absent Guard Counter finding do not transfer to BUILD-259. Conversely, BUILD-259's reported Guard Counter sightings and its no-parry-action coverage do not revise BUILD-255. An independent AU-C32 source-pixel audit found seven black BUILD-259 lead-in PNGs (first non-black frame 7), distinct from BUILD-255's six (first non-black frame 6); see `AU_C31_C35_CAPTURE_IDENTITY_AND_TRIM_AUDIT.md`. Keep each capture's build, video, source frames, and findings paired.

---

## 1. Approved Reel Observations (against `FIGHT_VIDEO_REVIEW.md`)

| Move / Visual | Seen? | Key Timestamps | Visual & Timing Assessment |
|---|---|---|---|
| **Backstep** | **YES** (50x) | 00:04.63, 00:34.02, 00:45.20, 00:56.99 | Clean backward hop with planted feet and sword pointing upward; zero unwanted turn. Perfectly readable when at open distance ($\ge 180\text{ cm}$). |
| **Guard Counter** | **YES** (6x) | 02:50.15, 07:27.50, 09:00.43, 11:14.45, 11:33.38, 11:56.50 | **First live sighting in full fight:** 6 counters executed, 4 direct damaging hits. At 02:50.15 (`t=170.15`), the upward diagonal cleave clears shield smoothly and hits with weight. At 07:27.50 (`t=447.49`), direct weapon clash with visible spark flare. At 11:56.50 (`t=716.52`), lethal counter lands with fiery explosion leading directly into boss defeat (`BOSS_DEAD at 716.8 s`). |
| **Air Light** | **YES** (25x) | 00:24.09, 00:47.92, 01:04.85, 01:14.27 | Forward horizontal cleave with extended-leg pose (~0.60 s). Readability is strong in mid-range but clipped when starting too close to boss body. |
| **Air Heavy Plunge** | **YES** (25x) | 00:30.50, 00:54.26, 01:15.27, 01:36.50 | High vertical leap into steep downward slam (~0.87 s). Distinct downward trajectory and heavier recovery clearly differentiate it from Air Light. |
| **Parry Recoil** | **NOT SEEN** (0x in fight) | N/A | Driver did not inject parry actions (focused on Guard Counter & ER attacks). Live recoil stands independently proven in PIE (`P_C1034_PARRY`). |
| **Phase-Two Aura** | **NOT VISIBLE ON CAMERA** | 06:11.40 (`t=371.4s`), 10:45.00 (`t=645.0s`), 11:15.00 (`t=675.0s`) | While the underlying component lifecycle is proven in PIE (`pie_tier2_aura.py`), on camera in `fight_review2.mp4` the ember aura particles (`NS_Boss_PhaseTwoAura`) are **not visible** across any frame in Phase Two. At 06:11.40 ([closeup](fight2_phase2_06m11s_closeup.png)), the camera is wedged inside the boss mantle and arena brazier fire. In open-silhouette shots at 10:45.00 ([silhouette](fight2_phase2_10m45s_silhouette.png)) and 11:15.00 ([counter clash](fight2_phase2_11m15s_counter.png)), the boss's green emissive sword slit is visible but no floating ember particles are rendered/discernible. The remainder of Phase Two consists of inside-mesh close-ups (`ECC_Camera IGNORE`) or wall occlusions. |

**Disposition correction (A-637 accepted in C-1053):** “not visible on camera” is the accepted full-fight visibility finding and corrects A-636. It does not revoke the C-1042 lifecycle witness: PIE proves component presence/activity, while the captured fight does not make the effect discernible. C-1062 sent an attachment/intensity proposal; A-646 later reported candidate-only changed module values, accepted as authoring readback in C-1075. The paired comparison then failed (black data frames and inactive candidate on legacy), and Codex's driver hotfix is awaiting Lead rerun. This technical review gives no visual approval; the original asset remains untouched and matched Lead PIE plus owner disposition are still required.

## Technical evidence and owner visual disposition

This file contains Antigravity's technical observations for BUILD-259. The seven owner decisions remain exclusively in `FIGHT_VIDEO_REVIEW.md`; its boxes are blank. Treat each evidence source independently:

| Evidence | What it can establish | Owner action |
|---|---|---|
| BUILD-255 `fight_review.mp4` and retained frames | BUILD-255 move sightings and its six black lead-in frames only; do not transfer those frame findings to BUILD-259. | Review the BUILD-255 excerpt only if requested; keep its checklist row open until the owner ticks it. |
| BUILD-259 `fight_review2.mp4` and retained frames | Antigravity's BUILD-259 move and aura visibility observations, including seven black lead-in frames; this report is technical review, not owner approval. | Review this exact capture and record each choice in the owner checklist. |
| Focused PIE captures | Runtime component/contact, route and render-pixel evidence for the tested scenario only; activation or an unoccluded test cannot determine appearance across the full fight. | Lead reports technical results; owner judges the final in-game appearance. |
| Separate showcase renders | The authored preview variants and their isolated framing; not full-fight or runtime proof. | Owner disposition of the specific current/boosted aura option remains open. |

The latest aura capture recovery is also bounded: C-1120 identified comma-packed runner environment values and first-use black HighResShot frames. Codex's offline fixes now split and log each `-Env` value and warm up on decoded brightness, capped at 20 frames/4 game seconds; Claude owns the rerun. No new visual finding is claimed here until a Lead capture is reviewed.
| **Parry Distortion** | **NOT SEEN** (0x in fight) | N/A | No parries injected by driver. Chromatic aberration fringe is independently proven working in PIE (`P_C1042_AURA` / `r5`). Subtle chromatic aberration is visible on high-contrast edges when post-process pulse is active. |

---

## 2. Dynamic Camera & Framing Findings (Lead Finding C-1051)

1. **Dynamic Melee Clipping:**
   - In static tests (`C-1044`), open-ground raycasts at 105–300 cm showed full arm extension with `ECC_Camera IGNORE` on the boss capsule.
   - However, in dynamic combat, when the boss circles beside or behind the player, the camera spring arm is pushed inside the boss mesh bounds (under the mantle, through leg geometry) rather than shortening against the outer boundary.
   - At melee range ($\sim 105\text{--}180\text{ cm}$), frames frequently show interior mantle surfaces or extreme player-back close-ups, obscuring combat silhouette.
2. **Support for Proposed Lead Options (to be decided by Owner):**
   - Option (a): Boss capsule blocks `ECC_Camera` so the arm pulls in rather than entering interior mesh geometry.
   - Option (b): Mesh dither/fade when camera penetrates boss bounding box.
   - Option (c): Orbit/lock-on framing keeping the boss centered in front.

---

## 3. Summary & Verification

- **Asset Visibility in Fight Video:** All 4 ER player moves (Backstep, Guard Counter, Air Light, Air Heavy Plunge) are visually verified in continuous combat. Guard Counter is fully validated in full-fight context (6 executions, lethal blow at 11:56.50). In contrast, Phase-Two Aura (`NS_Boss_PhaseTwoAura`) is **not visible on camera** throughout the video due to camera penetration inside mesh geometry, close-up framing, and brazier flame obstruction.
- **Evidence Cropped PNGs:**
  - `Documentation/Boss/fight2_phase2_06m11s_closeup.png` (06:11.40: camera inside mantle/brazier flame at Phase 2 threshold)
  - `Documentation/Boss/fight2_phase2_10m45s_silhouette.png` (10:45.00: open-air silhouette; sword green slit seen, zero ember particles)
  - `Documentation/Boss/fight2_phase2_11m15s_counter.png` (11:15.00: guard counter clash; zero ember particles)
- **Video Reference:** `Docs/BossCombatReview/Execution/Claude/P_FIGHTVIDEO/fight_review2.mp4` (retained uncommitted per instruction).
