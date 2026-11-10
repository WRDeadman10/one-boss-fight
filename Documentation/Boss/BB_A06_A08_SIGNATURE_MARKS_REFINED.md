# BB-A06..A08: Refined Frame-Cited Marks (`Ultimate_Swing_120fps`, `Subjugation`, `Soul_Siphon`)

**Authority:** `Documentation/Boss/QUEUE_BB.md` (`BB-A06`, `BB-A07`, `BB-A08`), refining [`Documentation/Boss/C1242_SEVAROG_CONTACT_MARKING.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/C1242_SEVAROG_CONTACT_MARKING.md).  
**Owner:** Antigravity (`frame-cited visual audit; zero asset/card mutations`).  
**Sources Inspected:**
- `D:/FightVideo/sevarog_frames/_sheets/Ultimate_Swing_120fps_sheet.png` (frames `000..040`, `0.000–2.633 s`)
- `D:/FightVideo/sevarog_frames/_sheets/Subjugation_sheet.png` (frames `000..043`, `0.000–2.867 s`)
- `D:/FightVideo/sevarog_frames/_sheets/Soul_Siphon_sheet.png` (frames `000..028`, `0.000–1.833 s`)

---

## 1. Summary Table (Refined Windows @ 15 Hz, Clamped End Times)

| Task | Clip | Length | Tell / Windup (Commit) | Release / Active Window | Follow-Through / Punish Hold | Full Recovery to Rest |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BB-A06** | `Ultimate_Swing_120fps` | `2.633 s` | `000–009` (`0.000–0.600 s`), commit `009` (`0.600 s`) | `010–013` (`0.667–0.867 s`) | `014–023` (`0.933–1.533 s`) — wide-open chest shoulder hold (`0.60 s` punish window) | `024–040` (`1.600–2.633 s`) |
| **BB-A07** | `Subjugation` | `2.867 s` | `000–011` (`0.000–0.733 s`), commit `011` (`0.733 s`) | `012–013` (`0.800–0.867 s`) *(ground AoE trigger; no weapon trace)* | `014–029` (`0.933–1.933 s`) — crouched ground channel/hold (`1.00 s` vulnerable recovery) | `030–043` (`2.000–2.867 s`) |
| **BB-A08** | `Soul_Siphon` | `1.833 s` | `000–003` (`0.000–0.200 s`), commit `003` (`0.200 s`) | `004–019` (`0.267–1.267 s`) *(1.00 s sustained cone drain channel)* | `020–023` (`1.333–1.533 s`) — hammer raise transition | `024–028` (`1.600–1.833 s`) |

---

## 2. Detailed Frame-by-Frame Notes

### BB-A06: `Ultimate_Swing_120fps` (`000–040`, `2.633 s`)
- **Tell (`000–009`, `0.000–0.600 s`):**
  - `000–003` (`0.000–0.200 s`): Right arm lifts the hammer high overhead-right, shaft angling diagonal.
  - `004–008` (`0.267–0.533 s`): Hammer pulls back across overhead/left-rear coil while shoulder tendrils flare wide (`007–008`).
  - `009` (`0.600 s`): Windup apex / commit boundary just before release.
- **Release / Cleave (`010–013`, `0.667–0.867 s`):**
  - `010` (`0.667 s`): Torso whips rapidly down-right, cloak tendrils fanned horizontally, hammer descending on right side (**active start**).
  - `011` (`0.733 s`): Deep crouched horizontal cleave, hammer sweeping low-right (`bottom-right`).
  - `012` (`0.800 s`): Mid/late spin follow-through low around torso, tendrils trailing left-down.
  - `013` (`0.867 s`): Hammer exits low cleave rising diagonally up-left (`viewer's upper-left`), glowing chest visible (**active end**). By `014` (`0.933 s`), the hammer is already up at chest/shoulder height above the strike plane.
- **Recovery (`014–040`, `0.933–2.633 s`):**
  - `014–023` (`0.933–1.533 s`): Distinct held post-cleave silhouette (`hammer high across shoulders, green chest exposed`), yielding a clear ~`0.60 s` punish tell before turning back upright in `024–027` (`1.600–1.800 s`) and settling to rest (`028–040`, `1.867–2.633 s`).

### BB-A07: `Subjugation` (`000–043`, `2.867 s`)
- **Tell (`000–011`, `0.000–0.733 s`):**
  - `000–002` (`0.000–0.133 s`): Hammer held stationary on right; left hand begins rising.
  - `003–011` (`0.200–0.733 s`): Left hand raised high above head with splayed claws (`unmistakable cast tell`), reaching peak height/coil at `010–011` (`0.667–0.733 s`).
- **Release (`012–013`, `0.800–0.867 s`):**
  - `012` (`0.800 s`): Both shoulders snap wide (`left arm sweeps left-down, hammer hand flares right`) as Sevarog slams his cast downward (**AoE delay/spawn release**).
  - `013` (`0.867 s`): Deepest forward crouch/lunge; tendrils flared wide at impact.
- **Recovery / Punish Hold (`014–043`, `0.933–2.867 s`):**
  - `014–029` (`0.933–1.933 s`): Stationary crouched channel hold (`left hand lowered, hammer held low-right`). Note for `BB-X12` AoE design: early frames (`014–020`) coincide with expected ground snare/hazard active time, leaving `021–029` + stand-up (`030–035`, `2.000–2.333 s`) as safe melee punish if out of AoE radius.
  - `036–043` (`2.400–2.867 s`): Neutral upright rest.

### BB-A08: `Soul_Siphon` (`000–028`, `1.833 s`)
- **Tell (`000–003`, `0.000–0.200 s`):**
  - `000` (`0.000 s`): Upright stance, hammer held nearly vertical on right.
  - `001–003` (`0.067–0.200 s`): Upper body leans slightly forward while lowering the hammer down-forward into cast alignment (`003` at `0.200 s` = commit boundary; short `0.20 s` startup — confirm whether `BB-X13` adds a pre-channel targeting/delay or triggers cone ticks at `0.267 s`).
- **Active Channel (`004–019`, `0.267–1.267 s`):**
  - `004–019` (`0.267–1.267 s`): Steady, nearly static `1.00 s` channel pose with hammer pointing forward-down-right (`~45°`) in front of torso. Matches a multi-tick frontal cone drain (`BB-X13`) with clear visual interrupt window.
- **Recovery (`020–028`, `1.333–1.833 s`):**
  - `020–023` (`1.333–1.533 s`): Raises hammer back up to vertical-right.
  - `024–028` (`1.600–1.833 s`): Settles back to idle rest pose.
