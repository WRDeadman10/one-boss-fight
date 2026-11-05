# V-A031: Owner Play-Test Intake & Scenario Conversion Framework

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)  
**Date:** 2026-11-06  
**Status:** **FRAMEWORK READY — WAITING ON OWNER PLAY-TEST NOTES**  
**Scope:** Intake structure, tagging taxonomy, and automated PIE reproduction mapping for incoming Owner play-session feedback.
**Sources:** Documentation/PROJECT_STATE.md:301-350, Documentation/TASKS.md [PROPOSAL / Intake Template]

---

## 1. Executive Summary

- **Context:** To ensure subjective player impressions ("boss attack felt unreactable", "parry felt late", "dodge got clipped") are converted into rigorous, measurable test scenarios, this intake framework maps qualitative feedback directly into reproducible headless PIE test scripts (`pie_*.py`).
- **Status:** The intake protocol and scenario templates are established. The table is pre-populated with known observation points awaiting Owner session timestamps and notes.

---

## 2. Intake-to-Scenario Mapping Taxonomy

| Play-Test Observation Tag | Core Technical Dimension | Underlying Metrics / Properties | Target Automated Driver / Test |
| :--- | :--- | :--- | :--- |
| **`FEEL-TELEG`** | Attack Telegraph & Windup | Windup frame count, apex pause duration, `CommitTime` | `pie_authored_close_clips.py`, `RPGAttackTracker` |
| **`FEEL-PARRY`** | Parry Leniency & Window | Dilation factor, active parry window (\(0.15\text{ s}\)), spark sync | `pie_legend.py` (L8), `RPGPlayerParry` |
| **`FEEL-DODGE`** | Evasion & i-Frame Leniency | i-Frame window (\(0.00 - 0.20\text{ s}\)), displacement curve | `pie_iframes.py`, `RPGDodgeTiming` |
| **`FEEL-HITSTOP`**| Visceral Contact Freeze | Hitstop duration (\(0.06 - 0.10\text{ s}\)), camera shake impulse | `RPGDamageResolver`, `RPGPlayerParry` |
| **`FEEL-RECOIL`** | Boss Deflection Stumble | Recoil duration (\(0.60\text{ s}\)), recovery blend-in | `AM_Boss01_ParryRecoil`, `rpg.Art.Tier2` |
| **`FEEL-AUDIO`** | Sound Spatialization & Mix | Hit cue latency, clack clarity, music ducking | `V_A034_AUDIO_MIX_AUDIT.md`, `SoundMix` |

---

## 3. Pre-Configured Reproducible Scenario Templates

1. **Scenario SCEN-01 (A2 Slam Jump/Dodge Clarity):**
   - **User Query:** "Did the jump clear the shockwave cleanly, or did lingering damage clip the player?"
   - **Driver:** `pie_a2_scenarios.py` with `A2_TRACKER_PREVIEW=1` and `rpg.Art.Tier1=1`.
   - **Assertion:** `FeetZ - GroundZ >= 50.0` registers `bClearedBand=true` and `Damage=0`.
2. **Scenario SCEN-02 (A4 Low Sweep Crouch/Roll Avoidance):**
   - **User Query:** "Can player roll through the wide sweep without collision capsule snag?"
   - **Driver:** `pie_iframes.py` with horizontal attack trajectory.
   - **Assertion:** Capsule overlap suppressed during active i-frame window.
3. **Scenario SCEN-03 (F1 Parry Slow-Motion Readability):**
   - **User Query:** "Does slow-motion give sufficient reaction time to initiate a riposte or reposition?"
   - **Driver:** `pie_legend.py` scenario L8.
   - **Assertion:** Time dilation maintains 0.15 scale for exactly 0.35 s, smoothly recovering to 1.0.

---

## 4. Owner Play-Test Intake Protocol

- When Owner conducts live play-testing in `L_SevarogArena`, notes logged in chat or mailbox will be appended to this ledger with:
  1. Exact timestamp / clip reference.
  2. Assigned observation tag (`FEEL-...`).
  3. Linked automated test scenario.
