# BC-A10: Sevarog Stun Trio & LevelStart Frame Notes (`15 Hz` Contact Sheets)

**Queue Lane:** `QUEUE_BC_AG` Task `BC-A10` (Antigravity)  
**Unblocked By:** `[C-1274]` Lead frame capture (`Docs/BossCombatReview/Execution/Claude/P_C1271_SEVAROGFRAMES2/`, `P_C1271_SEVAROGFRAMES3/`)  
**Visual Sheets Inspected (Read-Only):**
- `D:/FightVideo/sevarog_frames/_sheets/Stun_Start_sheet.png` (`27` frames `0–26`, `1.700 s` C1239 length)
- `D:/FightVideo/sevarog_frames/_sheets/Stun_Loop_sheet.png` (`32` frames `0–31`, `2.033 s` C1239 length)
- `D:/FightVideo/sevarog_frames/_sheets/Stun_End_sheet.png` (`12` frames `0–11`, `0.733 s` C1239 length)
- `D:/FightVideo/sevarog_frames/_sheets/LevelStart_sheet.png` (`41` captured frames `0–40` / `2.667 s` of `5.000 s` `LevelStart_Montage` — partial `41/75` per `[C-1274]`)
- `D:/FightVideo/sevarog_frames/_sheets/Death_front_sheet.png` (`16` bright frames `0–15` / `0.000–0.967 s` captured per `[C-1279]` / `Claude/P_C1278_SEVAROGDEATH`, `DATA route_verified`; `0` dark frames)

---

## 1. Stagger Trio Frame Breakdown & Vulnerable Riposte Windows

Matches shared `URPGBossFrameworkProfile` slots `StaggerStartAnim`, `StaggerLoopAnim`, `StaggerEndAnim` (`BB_X11_X15_SEVAROG_DESIGN.md`). Sampling uncertainty is `+/- 0.067 s` (`15 Hz`).

### 1.1 `Stun_Start` (`000–026`, `1.700 s`)

| Frame Span (`15 Hz`) | Montage Time (`s`) | Visual Pose & Motion | Combat / Riposte Candidate Role |
|---|---:|---|---|
| `000–002` | `0.000–0.133` | Upright combat idle (chest facing away/right, hammer held high right); recoil jolt begins at `002` | Initial posture-break hit jolt |
| `003–007` | `0.200–0.467` | Torso pitches forward/down; hammer drops diagonally down-right across shins as knees buckle | Collapse transition (boss transitioning downward) |
| `008–011` | `0.533–0.733` | Dropping into deep kneel; hammer shaft lowers horizontally toward floor; `011` reaches bottom floor contact | Knee/hammer floor contact transition |
| **`012–026`** | **`0.800–1.700`** | **Planted deep kneel:** crown bowed forward over horizontally grounded hammer (`weapon_r` beside knee, shoulder cloaks extended backward). Static settle from `014–026` matching `Stun_Loop` frame `000` | **Grounded Vulnerable State (`>= 0.800 s`)**: riposte window candidate open cleanly once grounded |

### 1.2 `Stun_Loop` (`000–031`, `2.033 s`)

| Frame Span (`15 Hz`) | Montage Time (`s`) | Visual Pose & Motion | Combat / Riposte Candidate Role |
|---|---:|---|---|
| **`000–031`** | **`0.000–2.033`** | Seamless crouched-kneel loop identical to `Stun_Start` `012–026` (subtle breathing rise peaking around `014–016` and settling back smoothly to `028–031`); zero root travel | **100% Vulnerable Riposte Window:** safe frontal/rear riposte prompt eligibility across the entire loop (`2.033 s` per cycle) |

### 1.3 `Stun_End` (`000–011`, `0.733 s`)

| Frame Span (`15 Hz`) | Montage Time (`s`) | Visual Pose & Motion | Combat / Riposte Candidate Role |
|---|---:|---|---|
| `000–002` | `0.000–0.133` | Uncoiling up from grounded kneel (`000` matches `Stun_Loop`; back cloaks lift and gather behind torso) | Recovery startup / riposte window close (`<= 0.133 s`) |
| `003–006` | `0.200–0.400` | Spine straightens to full height; hammer lifts horizontally across waist height | Standing recovery (non-damaging) |
| `007–011` | `0.467–0.733` | Right arm sweeps hammer diagonally upward-right into neutral idle (`010–011` match `Stun_Start` `000` ready stance) | Ready for selector transition cleanly at `0.733 s` |

---

## 2. `LevelStart` Partial Capture (`000–040` / `41 of 75` Frames, `0.000–2.667 s` of `5.000 s`)

| Frame Span (`15 Hz`) | Montage Time (`s`) | Observed Pose in `LevelStart_sheet.png` | Notes |
|---|---:|---|---|
| `000–004` | `0.000–0.267` | Only the **planted vertical hammer shaft** appears on the center arena floor; Sevarog's mesh is absent/hidden below | Pre-materialization phase |
| **`005`** | `0.333` | Hammer head drops vertically from top frame edge onto the planted shaft (`FX` summon beat) | Weapon summon peak |
| `006–015` | `0.400–1.000` | Vertical hammer planted alone until `015`; dark silhouette starts emerging at shaft base on `015–016` | Pairs with `LevelStart_Montage`'s single `PlayParticleEffect` notify timing check (`TBD`) |
| `016–024` | `1.067–1.600` | Sevarog's hunched shadow mound rises beside the hammer shaft (`016–020`), shoulders & cloak arch upward (`021–024`) | Boss emergence phase |
| `025–034` | `1.667–2.267` | Grips planted hammer shaft and rises to full upright height; horned crown unfolds (`031–034`) | Upright stance acquired (`~2.27 s`) |
| `035–040` | `2.333–2.667` | Towering silhouette stands facing away, holding vertical planted hammer (`Frames 41–74` / `2.733–5.000 s` not yet captured) | Remainder (`2.733–5.000 s`) **PARTIAL / OPEN** pending full 75-frame capture |

---

## 3. `Death_front` (`000–015`, `0.000–0.967 s`) Frame Breakdown (`[C-1279]`)

Visual observation from `D:/FightVideo/sevarog_frames/_sheets/Death_front_sheet.png` (`16` bright frames, `0` dark frames, `Claude/P_C1278_SEVAROGDEATH`, `DATA route_verified`):

| Frame Span (`15 Hz`) | Montage Time (`s`) | Observed Pose in `Death_front_sheet.png` | Phase Role |
|---|---:|---|---|
| `000–001` | `0.000–0.067` | Standing upright facing away/forward (`000`); arms & cloak sleeves flare outward on `001` as fatal knockback begins | Hit knockback onset |
| **`002–009`** | `0.133–0.600` | **Collapse onset (`002–005`):** arms splay wide, knees leave vertical alignment, torso pitches steeply backward off balance; (`006–009`) descends supine toward cobblestones as weapon passes mid-center before dropping right (`009`) | Backward topple & collapse |
| **`010–012`** | `0.667–0.800` | **Ground contact (`010` @ `0.667 s`):** upper back/shoulders strike stone tiles cleanly; left arm & clawed fingers slam flat left (`010–011`); legs rebound briefly upward (`011–012`) | Primary floor impact |
| **`013–015`** | `0.867–0.967` | Legs settle downward toward arena floor (`013`); **`014–015` (`0.933–0.967 s`) reach stationary final supine rest pose** with outstretched clawed hands and idle cloak folds | **Final rest (`015 = 0.967 s` clip end; clean hold/fade)** |

---

## 4. Remaining Capture Blocker

- **`LevelStart` tail (`Frames 41–74` / `2.733–5.000 s`):** Still partial (`41/75`); full idle settle & hammer shoulder-lift occur in the uncaptured `2.733–5.000 s` tail (queued for later capture per `[C-1279]`).
