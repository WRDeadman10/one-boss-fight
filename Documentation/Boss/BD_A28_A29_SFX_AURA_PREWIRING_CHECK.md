# BD-A28..A29 & Batch 6 (`BD-A26..BD-A30`): SFX Card-Cue & Phase-2 Aura Pre-Wiring Check

**Authority:** [`QUEUE_BD_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BD_AG.md), `[X-1872]` (`0` commits made, `0` pushes, `0` editor calls)

---

## 1. Batch 6 Status Matrix (`BD-A26..BD-A30`)

| ID | Task | Status | Disposition / Missing Input |
|---|---|---|---|
| `BD-A26` | Intake Owner audition picks for `SFX_03` / `SFX_06` Batches `1–3` & `1–9` | **`BLOCKED`** | Awaits Owner reel picks (`BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md`). |
| `BD-A27` | Intake Owner review pick for Sevarog `4-Move Live Clip` & `BB-A24` Phase-2 aura (`Cand A/B/C`) | **`BLOCKED`** | Awaits Owner selection (`BB-A24`). |
| `BD-A28` | Verify `/Game/` sound paths (no `SFX_02` shorthand leakage) & `S6–S8` card-cue opt-in readiness | **COMPLETE** | Verified Section 2 below + [`test_bd_a28_sfx_aura_precheck_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bd_a28_sfx_aura_precheck_contract.py). |
| `BD-A29` | Verify `BC_A26_A30_SFX_AURA_COOK_PRECHECK.md` fixed bounds (`[-220, 220] cm`) & `<= 120` sprite budget across `BB-A24` candidates | **COMPLETE** | Verified Section 3 below + [`BC_A26_A30_SFX_AURA_COOK_PRECHECK.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BC_A26_A30_SFX_AURA_COOK_PRECHECK.md). |
| `BD-A30` | Prepare Owner-ready Batch 6 file manifest (`0` commits made) | **COMPLETE** | Section 4 below. |

---

## 2. `BD-A28`: Card-Cue Path Hygiene & `S6–S8` Opt-In Contract

- All `9` verified candidate/Sevarog specs (`SFX_05`, `SFX_07..SFX_12`, `BB_A11_A13`, `BB_A14`) remain `100%` on disk (`0` missing paths, verified by `test_bc_a26_sfx_specs_disk_contract.py`), avoiding `SFX_02`'s `8` abbreviated paths missing `Cues/Sword_*` & `Audio/Cues/`.
- In `Scripts/Editor/author_sevarog_draft_cards.py:371-430`, `S1..S8` keep `"cues": []` (`FRPGBossMoveCard.cpp:106-118` requires non-empty `Cues` to supply distinct Visual+Sound channels with non-null `Sound`), ensuring zero inadvertent pack audio coupling or unpicked sound wiring prior to Owner picks.

---

## 3. `BD-A29`: Phase-2 Aura Fixed-Bounds & Performance Budget Check (`RTX 2060 Super 16.67 ms`)

- Any Owner-selected `BB-A24` candidate (`Cand A/B/C`) authored into `/Game/OneBossFight/VFX/NS_Sevarog_PhaseTwoAura_*` (project-owned copy, zero `/Game/ParagonSevarog/FX/` edits) enforces:
  - Fixed symmetric AABB `[-220.0, 220.0] cm` on both Emitter & System bounds (`[C-1202]` rule for `165 cm` Sevarog half-height).
  - Exposed `User.Scale` (`1.0`), `User.Opacity` (`0.85`), `User.Color_Primary`, `User.Color_Secondary`.
  - Active particle cap `<= 120` sprites to stay well within the `16.67 ms` frame budget and keep `S6`/`S7`/`S8` telegraphs clear.

---

## 4. Owner-Ready Batch 6 File Manifest (`BD-A30`)

Antigravity deliverables ready for Owner review/commit (`0` commits made per `[X-1872]`):
- `Documentation/Boss/BD_A28_A29_SFX_AURA_PREWIRING_CHECK.md`
- `Scripts/Tools/test_bd_a28_sfx_aura_precheck_contract.py`
