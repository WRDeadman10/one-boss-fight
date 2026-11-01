# Track B Remaining Requirements Census: 1 NOT YET Row

**Document Reference:** `Reviews/NOT_YET_CENSUS.md`  
**Task Reference:** `[C-565]` / `[C-568]` / `[C-617]` / `[C-621]` (Track B Direction Selection Census)  
**Source Authority:** `witness_status_v3.json` (exact titles and observables)  
**Total Census:** 1 requirement currently classified as `NOT YET`  

---

## 1. Executive Summary & Classification Matrix

This document classifies the 1 remaining `NOT YET` combat requirement to inform the Owner's strategic roadmap choice across **Direction A** (Framework completion to full duel), **Direction B** (Track B soulslike boss framework polish), and **Direction C** (Pack-level authoring & Greystone integration).

*(Note: As of BUILD-133/BUILD-134, 0 ENGINE-ONLY, 0 NEEDS DESIGN DECISION, and 0 NEEDS NEW SYSTEM requirements remain in NOT YET; all three categories are 100% completed.)*

### Classification Definitions:
- **ENGINE-ONLY:** Pure C++ / runtime rules or hooks; no art or external system dependencies.
- **NEEDS ART:** Requires animations, montages, notify tracks, VFX/SFX, or arena mesh assets.
- **NEEDS DESIGN DECISION:** Requires designer threshold parameters, precedence rules, or pacing formulas.
- **NEEDS NEW SYSTEM:** Requires an entire unbuilt architectural subsystem (AoE sweeps, memory buffers, grab state machines).
- **PLAYER-SIDE:** Depends on player character combat mechanics, input buffers, or counter-attack intake.

### Cost Estimate Scale (in Engine Witness Runs):
- **S (Small):** 1-2 runs; a simple log line, query param, or cvar test hook.
- **M (Medium):** 2-4 runs; a new rule struct/method, unit tests, and live PIE proof scenario.
- **L (Large):** 4+ runs; new multi-component system, asset plumbing, and multi-actor interaction harness.

---

## 2. Complete 1-Row NOT YET Census Table

| ID | Exact Title | Exact Observable | Dependency Class | Code Reference & Reason | Cost |
|:---|:---|:---|:---:|:---|:---:|
| **BOSS-QA-006** | Camera/readability | Camera framing maintains boss visibility and readability across near and far distance bands. | `PLAYER-SIDE` | no code: camera framing and lock-on tracking evaluation requires player follow camera / lock-on system testing | **M** |

---

## 3. Census Distribution Breakdown

### By Dependency Class:
- **PLAYER-SIDE:** 1 requirements (4.2%)
- **ENGINE-ONLY:** 0 requirements (0.0%)
- **NEEDS ART:** 0 requirements (0.0%)
- **NEEDS DESIGN DECISION:** 0 requirements (0.0%)
- **NEEDS NEW SYSTEM:** 0 requirements (0.0%)

### By Engine Run Cost:
- **Cost M:** 1 requirements (4.2%)
- **Cost L:** 0 requirements (0.0%)
- **Cost S:** 0 requirements (0.0%)
