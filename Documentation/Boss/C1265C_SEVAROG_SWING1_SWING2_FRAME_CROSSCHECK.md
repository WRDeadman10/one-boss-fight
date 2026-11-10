# C-1265c: Sevarog Frame-Sheet Cross-Check (`Swing1_Medium` & `Swing2_Medium`)

**Authority:** Claude Lead Directive `[C-1265]` (2026-11-10).  
**Owner:** Antigravity.  
**Sources Inspected (Read-Only):**
- Frame sheets: `D:/FightVideo/sevarog_frames/_sheets/Swing1_Medium_sheet.png`, `D:/FightVideo/sevarog_frames/_sheets/Swing2_Medium_sheet.png` (cross-checked with individual 15 Hz frames in `D:/FightVideo/sevarog_frames/Swing1_Medium/` and `D:/FightVideo/sevarog_frames/Swing2_Medium/`).
- Live trace reference: [`Documentation/Boss/C1262A_SEVAROG_TRACE_AND_COMBO_DIAGNOSIS.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/C1262A_SEVAROG_TRACE_AND_COMBO_DIAGNOSIS.md) and [`Documentation/Boss/C1242_SEVAROG_CONTACT_MARKING.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/C1242_SEVAROG_CONTACT_MARKING.md).

---

## 1. Body-Coordinate Reference in the Frame Sheets

- **Landmarks on Sevarog's mesh:** Sevarog's **front torso** displays two vertical glowing green rib columns (`Frames 0–2, 11–17` of `Swing1_Medium`; `Frames 0, 8–13` of `Swing2_Medium`). His **right hand** (`weapon_r`) grips the hammer shaft near the green hammer head (with the pack's vertical greatsword hanging at his right hip in live frames), and his **left hand** grips the opposite pommel end.
- **Screen-to-body mapping when Sevarog's front chest faces the camera:**
  - **Toward camera** = **Forward** (chest-facing front plane).
  - **Away from camera** = **Backward** (back/cloak plane).
  - **Viewer's Left** = Sevarog's **Right**.
  - **Viewer's Right** = Sevarog's **Left**.

---

## 2. `Swing1_Medium` Hammer-Head Trajectory (Frame-Cited)

| Frame (`time`) | C-1242 Role | Torso / Body Orientation | Hammer Head Direction Relative to Sevarog's Body |
| :--- | :--- | :--- | :--- |
| **0–2** (`0.000–0.133 s`) | Rest / Windup start | Chest faces camera; coiling slightly left (`002`). | **Right & Down** (`viewer's lower-left`, held diagonally across body; left hand holds pommel high-left). |
| **3** (`0.200 s`) | Commit / Windup peak | Chest angled slightly left/away; arms raised overhead. | **Up & Left-Rear** (`viewer's top-right`, raised high above left shoulder). |
| **4** (`0.267 s`) | Active start | Upper torso pitches sharply **forward & down**; hood ducks low. | **Down & Right-Rear** (`viewer's bottom-left`, shaft angled downward behind/beside right hip; head low/tucked on right side). |
| **5** (`0.333 s`) | Active mid | Torso hunched **forward & angled toward his right** (`viewer's left`). | **Right & Down** (`viewer's bottom-left`, arm extended to right side at knee/shin height, hammer head angled ~45° downward into his right side — NOT thrust straight forward along chest center). |
| **6** (`0.400 s`) | Active end | Torso angled toward his right; hammer swings horizontally forward-right. | **Right / Forward-Right** (`viewer's center-left` at waist height, angled horizontally outward toward right-front). |
| **7** (`0.467 s`) | Recovery start | Torso begins straightening; follow-through rises across front-right. | **Forward-Right & Up** (`viewer's upper-left`, chest/head height, visibly closer in foreground perspective on his right side). |
| **8–17** (`0.533–1.133 s`) | Recovery | `008` reaches vertical overhead; `009–017` settle facing camera. | `008`: **Up** overhead; `012–017`: settles across chest into **Left & Up** (`viewer's top-right`) mirror stance. |

---

## 3. `Swing2_Medium` Hammer-Head Trajectory (Frame-Cited)

| Frame (`time`) | C-1242 Role | Torso / Body Orientation | Hammer Head Direction Relative to Sevarog's Body |
| :--- | :--- | :--- | :--- |
| **0–2** (`0.000–0.133 s`) | Rest / Windup start | Chest angled open toward his right/front (`viewer's left`). | **Up & Left-Rear** (`viewer's top-right`, resting/cocked above left shoulder). |
| **3** (`0.200 s`) | Active start | Torso twists **away from camera** (`back/cloak visible`). | **Up & Back-Right** (`viewer's top-left`, held high behind right shoulder — winding up behind/away from front plane). |
| **4** (`0.267 s`) | Active early | Torso hunched sharply **away** (`back facing camera`). | **Down & Back-Left** (`viewer's bottom-right`, swept low behind/beside left hip). |
| **5** (`0.333 s`) | Active mid | Torso rotates back toward front (`camera`); arm whips low-to-front. | **Forward-Left & Down** (`viewer's bottom-right foreground`, hammer head grows large/close in perspective as it enters front plane from his left). |
| **6** (`0.400 s`) | Active end | Chest turning toward camera; horizontal cleave across waist/chest. | **Forward** (`viewer's center-right foreground`, largest/closest to camera at waist/chest height, sweeping left-to-right across front of torso). |
| **7** (`0.467 s`) | Recovery start | Torso facing camera; upward cross-body follow-through. | **Forward-Right & Up** (`viewer's upper-left foreground`, still close in perspective at shoulder/head height). |
| **8–17** (`0.533–1.133 s`) | Recovery | `008–013` upright facing camera; `014–017` coils to right. | `008–010`: **Right & Up** (`viewer's top-left`) held diagonally across chest; `014–017`: rotates down-right into `Swing1` start pose (`viewer's bottom-left`). |

---

## 4. Cross-Check Against Codex Trace Data (`C-1262a`)

1. **`Swing1_Medium` (Frames 4–6, `0.267–0.400 s`):**
   - Visually, `Frame 4` keeps the hammer tucked low/back on Sevarog's right side, `Frame 5` (`0.333 s`) extends the hammer **out to his right and downward** rather than dead-center forward, and the forward-rising sweep (`Frame 6 -> Frame 7`) only reaches the front-right plane late (`0.400–0.467 s`).
   - This explains why `C-1266` hit at **120 cm** (`S5` close) while `C-1262a` at **140 cm** missed laterally/short along the weapon sweep path.
2. **`Swing2_Medium` (Frames 3–6, `0.200–0.400 s`):**
   - Visually, `Frame 3` (`0.200 s`) is still behind/above his right shoulder (`back-right`) and `Frame 4` (`0.267 s`) is low behind his left hip (`back-left`). The hammer only enters the **front-facing sweep plane** in `Frames 5–7` (`0.333–0.467 s`), peaking straight **forward** toward his chest-facing side at `Frame 6` (`0.400 s`).
   - **Critical Orientation Cross-Check for `C-1265b`:** In `Swing1_Medium` (`Frame 0`) and `Swing2_Medium` (`Frames 0, 8–13`), Sevarog's chest faces the camera, whereas in `Speedburst` (`D:/FightVideo/sevarog_frames/_sheets/Speedburst_sheet.png`) and `Swing3_Slow` (`Frame 8–10`) his torso/facing aligns differently relative to the fixed capture camera. In `pie_live.log` (`C-1262a`), `Swing2_Medium` (`0.200–0.400 s`) logged `weaponA` behind the boss root (`X = -1605` to `-1493` vs boss `-1640`, target `-1780`). Codex's full-clip trace log (`C-1265b`) will confirm whether `Swing2_Medium` root/torso orientation swings toward `+X` (behind the boss) or enters `-X` (`< -1640`) after `0.400 s`.
