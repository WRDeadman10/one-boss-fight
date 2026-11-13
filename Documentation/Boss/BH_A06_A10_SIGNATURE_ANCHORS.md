# BH-A06..BH-A10: Sevarog Signature Sheet (`S3`/`S4`/`S7`/`S8`) Visual Anchor Notes

**Authority:** [`QUEUE_BH_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BH_AG.md) Batch 2 (`BH-A06..BH-A10`; slot labels hotfixed per `[X-1893]`: `S3=Swing3_Slow`, `S4=Speedburst`, `S6=Ultimate_Swing_120fps`, `S7=Subjugation`, `S8=Soul_Siphon`)  
**Source Media Inspected (Read-Only):** `D:/FightVideo/sevarog_frames/_sheets/{Subjugation,Soul_Siphon,Swing3_Slow,Speedburst}_sheet.png` (`15 Hz` capture grid)  
**Source Authoring Script:** [`Scripts/Editor/author_sevarog_draft_cards.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Editor/author_sevarog_draft_cards.py)

---

## 1. `BH-A06`: Signature Cast Visual Anchor Notes (`S7` Subjugation / `S8` Soul Siphon)

| Slot & Card / Clip | Sheet Frames (`15 Hz`) | Visual Anchor Site & Posture | Card Alignment (`author_sevarog_draft_cards.py`) |
|---|---|---|---|
| **`S7` — Subjugation** (`DA_Move_Sevarog_Subjugation_C1277`) | `0..43` (`44` frames) | **Left-hand summon & plunge:** Frames `0..11` raise left claw overhead while `weapon_r` warhammer stays braced upright; Frames `12..14` plunge left hand downward toward target ground zone; Frames `15..43` recover smoothly to idle guard. | `commit_seconds=0.733` (`~F11`), `active_start=0.800` (`F12`), `active_end=0.867` (`~F13`), `recovery_end=2.836`, `windows=[]`, `area_effect` (`release=0.800`, `delay=0.750`, `radius=225.0`, `damage=35.0`, `snare_seconds=2.50`). |
| **`S8` — Soul Siphon** (`DA_Move_Sevarog_Soul_Siphon_C1277`) | `0..28` (`29` frames) | **Left-hand forward drain aperture:** Frames `0..3` coil inward; Frames `4..19` extend left arm/claw straight forward at chest height for drain channel while `weapon_r` stays held low on right flank; Frames `20..28` lift hammer back to idle guard. | `commit_seconds=0.200` (`F3`), `active_start=0.267` (`F4`), `active_end=1.267` (`F19`), `recovery_end=1.803`, `windows=[]`, `channel_drain` (`start=0.267`, `end=1.267`, `tick=0.200`, `tick_damage=8.0`, `cone_range_cm=650.0`). |

---

## 2. `BH-A07`: Scythe Swing Span & Gap-Closer Clearance (`S3` `Swing3_Slow` / `S4` `Speedburst`)

| Slot & Card / Clip | Sheet Frames (`15 Hz`) | Visual Socket Span & Camera Framing | Card Alignment (`author_sevarog_draft_cards.py`) |
|---|---|---|---|
| **`S3` — Swing3_Slow** (`DA_Move_Sevarog_Swing3_Slow_C1247`) | `0..26` (`27` frames) | Frames `0..6` chamber hammer overhead (`weapon_r` handle -> `root_weapon_end_r` head cleanly framed); Frames `7..12` sweep wide low arc above floor tiles with zero mesh-floor clipping; Frames `13..26` settle to right-flank low guard. Full `weapon_r` -> `root_weapon_end_r` span stays inside camera frustum across all `27` frames. | Melee window `HitGroup_ScytheBlade`, `socket_a="weapon_r"`, `socket_b="root_weapon_end_r"`, elevated sweep `radius_cm=25.0` (`index == 2`). |
| **`S4` — Speedburst** (`DA_Move_Sevarog_Speedburst_C1247`) | `0..19` (`20` frames) | Frames `0..5` tuck hammer low-right while torso pitches forward; Frames `6..15` carry forward glide with cloak trailing behind and clear camera standoff; Frames `16..19` pull upright cleanly for whiff-combo followup. | Non-damaging defensive gap closer (`index == 3`, no melee `windows`), `warp_start=0.267` (`F4`), `warp_end=0.800` (`F12`), `warp_max_distance_cm=450.0`, `warp_standoff_cm=120.0`, whiff combo to `S5` (`Move_Sevarog_Swing1_Medium`). |

---

## 3. `BH-A08..BH-A10`: Contract Verification, Blockers & Batch 2 Manifest

- **`BH-A08` Contract Test:** [`Scripts/Tools/test_bh_a08_anchor_socket_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a08_anchor_socket_contract.py) parses `CARD_NAMES` via AST in `author_sevarog_draft_cards.py` and verifies exact `S3`/`S4`/`S6`/`S7`/`S8` card-to-ID associations (`Subjugation=S7`, `Soul_Siphon=S8`), `weapon_r` -> `root_weapon_end_r` sockets, and payload matches against this note and `QUEUE_BH_AG.md`.
- **`BH-A09` (`BLOCKED`):** `LevelStart` tail capture (`Frames 41–74`) and `D:/FightVideo/greystone_review/` inspection remain **`BLOCKED`** awaiting Lead Unreal Editor / PIE slot (`[C-1286+]`).
- **`BH-A10` Batch 2 Owner-Ready Manifest (`0` commits, `0` media staged):**
  - [`Documentation/Boss/BH_A06_A10_SIGNATURE_ANCHORS.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/BH_A06_A10_SIGNATURE_ANCHORS.md)
  - [`Scripts/Tools/test_bh_a08_anchor_socket_contract.py`](file:///C:/UnrealProject/OneBossFight/Scripts/Tools/test_bh_a08_anchor_socket_contract.py)
