# C-1265d: Sevarog 4-Move Live Owner Review-Clip Plan & Stitch Command

**Authority:** Claude Lead Directive `[C-1265]` (2026-11-10).  
**Owner:** Antigravity.  
**Discipline:** Reuses the existing bright PIE captures produced by [`Scripts/Editor/pie_sevarog_framework_live.py`](file:///c:/UnrealProject/OneBossFight/Scripts/Editor/pie_sevarog_framework_live.py) in `D:/FightVideo/sevarog_live/` (960x540, > 300 KB bright streak verified). Rendered MP4 output lives strictly on `D:/FightVideo/sevarog_live/` and is **never** staged or committed to git.

---

## 1. Existing Bright Capture Inputs (Reused Zero-PIE)

From Lead run `Claude/P_C1265_SEVAROGLIVE4` (`D:/FightVideo/sevarog_live/`):

| Order | Card Slot | Live Driver Still (`D:/FightVideo/sevarog_live/`) | Observed Bytes | Move Role & Live Proof Scope | Owner Review Focus |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **S1 (`Move_Sevarog_Swing1_Medium`)** | `Move_Sevarog_Swing1_Medium_216c3c13.png` | 821,864 B | Close swing 1 at 140 cm (S5 depth-2 chain hit 25 dmg at 120 cm) | Boss scale vs mannequin, silhouette, weapon readability |
| **2** | **S2 (`Move_Sevarog_Swing2_Medium`)** | `Move_Sevarog_Swing2_Medium_5c5aaed9.png` | 827,775 B | Close swing 2 at 140 cm (trace diagnosis C-1265b active) | Over-shoulder windup readability, arena contrast |
| **3** | **S3 (`Move_Sevarog_Swing3_Slow`)** | `Move_Sevarog_Swing3_Slow_5ef076af.png` | 829,066 B | Delayed heavy slam (37 cm step-in warp, HIT 55 dmg) | Ground slam impact framing, spacing & camera distance |
| **4** | **S4 (`Move_Sevarog_Speedburst`)** | `Move_Sevarog_Speedburst_f2ab7eb9.png` | 805,086 B | Gap-closer dash (330 cm ease warp, delta 0/0, chains Whiff -> S5) | Forward-lean dash silhouette, threat telegraph at standoff |

> Note: Each live driver run appends a random 8-character hex suffix (`Move_Sevarog_<Clip>_<hex>.png`). The stitch workflow selects the newest bright (`> 300,000 B`) file per move slot.

---

## 2. Reel Structure & Owner Evaluation Plan

- **Format:** 1920x1080 (Lanczos upscale from 960x540), 30 fps, H.264 `yuv420p`, `crf 18`, `+faststart`, **12.0 s total** (3.0 s hold per move with top header banner).
- **Optional Motion Companion (No Extra PIE Needed):** Append the 15 Hz sequence sheets/frames from `D:/FightVideo/sevarog_frames/<Clip>/<Clip>_*.png` (`Swing1_Medium`, `Swing2_Medium`, `Swing3_Slow`, `Speedburst`) after the live duel slate if the Owner wants full-arc motion context alongside the in-arena duel scale.
- **Owner Approval Criteria (4 Ticks):**
  1. **Scale & Stature:** Sevarog reads cleanly as a towering boss against the player capsule at 120–140 cm.
  2. **Dark-Armor Contrast:** Silhouette and glowing green hammer head separate clearly from `L_SevarogArena` stone/night sky.
  3. **Telegraph Readability:** S3 overhead slam and S4 forward-lean dash posture read unmistakably without HUD clutter.
  4. **Camera Framing:** Player-to-boss duel framing keeps both the hammer tip and the player unobstructed.

---

## 3. Verified `ffmpeg` Stitch Command (Output on `D:`, Never Staged)

Tested with `ffmpeg 9.0` against the `P_C1265_SEVAROGLIVE4` bright PNGs (`exit 0`, output `D:\FightVideo\sevarog_live\Sevarog_4Moves_Live_Review.mp4`, 909 KB, 12.0 s):

```powershell
ffmpeg -y `
  -loop 1 -t 3 -i "D:\FightVideo\sevarog_live\Move_Sevarog_Swing1_Medium_216c3c13.png" `
  -loop 1 -t 3 -i "D:\FightVideo\sevarog_live\Move_Sevarog_Swing2_Medium_5c5aaed9.png" `
  -loop 1 -t 3 -i "D:\FightVideo\sevarog_live\Move_Sevarog_Swing3_Slow_5ef076af.png" `
  -loop 1 -t 3 -i "D:\FightVideo\sevarog_live\Move_Sevarog_Speedburst_f2ab7eb9.png" `
  -filter_complex "[0:v]scale=1920:1080:flags=lanczos,drawbox=x=0:y=0:w=1920:h=84:color=black@0.72:t=fill,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='S1 - Swing1_Medium (140 cm live framing)':fontcolor=white:fontsize=34:x=40:y=24[v0];[1:v]scale=1920:1080:flags=lanczos,drawbox=x=0:y=0:w=1920:h=84:color=black@0.72:t=fill,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='S2 - Swing2_Medium (140 cm live framing)':fontcolor=white:fontsize=34:x=40:y=24[v1];[2:v]scale=1920:1080:flags=lanczos,drawbox=x=0:y=0:w=1920:h=84:color=black@0.72:t=fill,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='S3 - Swing3_Slow (Delayed Slam | 37 cm step-in | 55 dmg HIT)':fontcolor=white:fontsize=34:x=40:y=24[v2];[3:v]scale=1920:1080:flags=lanczos,drawbox=x=0:y=0:w=1920:h=84:color=black@0.72:t=fill,drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='S4 - Speedburst (Dash Gap-Closer | 330 cm warp -> S5 Chain)':fontcolor=white:fontsize=34:x=40:y=24[v3];[v0][v1][v2][v3]concat=n=4:v=1:a=0,format=yuv420p[v]" `
  -map "[v]" -c:v libx264 -r 30 -preset veryfast -crf 18 -movflags +faststart `
  "D:\FightVideo\sevarog_live\Sevarog_4Moves_Live_Review.mp4"
```

### Dynamic Latest-Capture Resolution (For Future Runs)
To rebuild automatically after any fresh `SEVAROG_LIVE_SHOTS=1` run without editing filenames:
```powershell
$dir = "D:\FightVideo\sevarog_live"
$pick = { param($pat) (Get-ChildItem "$dir\$pat" | Where-Object Length -gt 300000 | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName }
$s1 = & $pick "Move_Sevarog_Swing1_Medium_*.png"
$s2 = & $pick "Move_Sevarog_Swing2_Medium_*.png"
$s3 = & $pick "Move_Sevarog_Swing3_Slow_*.png"
$s4 = & $pick "Move_Sevarog_Speedburst_*.png"
```
(Substitute `$s1..$s4` into the `-i` arguments above.)
