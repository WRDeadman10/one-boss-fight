# BB-A14: Sevarog Voice-Bark Candidate Specification (`DialogueWaves` & `SoundCues`)

**Queue Lane:** `QUEUE_BB` Task `BB-A14` (Antigravity)  
**Authority:** `Documentation/Boss/QUEUE_BB.md`, `[C-1267]`  
**Status:** SPEC-ONLY (Zero Blueprint/C++ wiring, zero asset edits; awaits Owner selection and Lead gate)  

---

## 1. Purpose & Isolation Rule

Per `SFX_07_BATCH4_CANDIDATE_SPEC.md` (`[C-1175]`/`[C-1208]`), Sevarog's native Paragon vocal library under `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/` belongs exclusively to the Sevarog encounter and must never share barks with Boss01 (Ember Warden). All assets below are verified physically on disk under `Content/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/DialogueWaves/` and `SoundCues/`.

---

## 2. Encounter Event Voice-Bark Candidate Matrix

| Encounter Event | Trigger Context | Primary `SoundCue` Wrapper (Multi-Line Random) | Verified `DialogueWave` Variations (On Disk) | Cooldown / Priority Guidance |
|---|---|---|---|---|
| **Arena Intro / Dormant Wake** | `URPGSevarogDirector` gate opens (`EntranceHoldSeconds`) or boss spawns | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Intro_Boast` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/DialogueWaves/Sevarog_Intro_Boast_010_Dialogue`<br>`.../Sevarog_Intro_Boast_020_Dialogue`<br>`.../Sevarog_Intro_Boast_030_Dialogue`<br>`.../Sevarog_Intro_Statement_010_Dialogue`..`040` | Play once per encounter start (`bPlayedIntroBark = true`); duck ambience `-4 dB` |
| **Phase 2 Escalation / Ultimate Cast** | Phase 2 transition threshold (`URPGSevarogDirector`) or `Ultimate_Swing_120fps` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Ability_Ultimate_Self` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/DialogueWaves/Sevarog_Ability_Ultimate_Self_010_Dialogue`<br>`.../Sevarog_Ability_Ultimate_Ready_010_Dialogue`<br>`.../Sevarog_Ability_Ultimate_Ready_020_Dialogue`<br>`.../Sevarog_Ability_Ultimate_Ready_030_Dialogue` | Phase-transition trigger fires unconditionally once; card trigger gated by `>= 18 s` bark cooldown |
| **Ability Engage / Spectral Hex (`Subjugation` / `Soul_Siphon`)** | Ranged or special hex engage (`E` / `RMB`) | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Ability_E_Engage`<br>`.../Sevarog_Ability_RMB_Engage` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/DialogueWaves/Sevarog_Ability_E_Engage_010_Dialogue`..`030`<br>`.../Sevarog_Ability_RMB_Engage_010_Dialogue`..`030` | Optional flavor (`<= 25%` chance or `>= 15 s` cooldown so barks stay sparse vs effort grunts) |
| **Posture Break / Heavy Pain / Parry Recoil** | Boss staggered or receives heavy critical stagger | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_SufferedCrit` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/DialogueWaves/Sevarog_Health_SufferedCrit_010_Dialogue`<br>`.../Sevarog_Effort_PainHeavy_01_Dialogue`..`03`<br>`.../Sevarog_Effort_Frustration_01_Dialogue`..`03` | Hard cooldown `>= 10 s`; never interrupt death/phase barks |
| **Low Boss Health / Phase 2 Desperation** | Boss enters critical HP (`< 30%`) | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Health_Critical` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/DialogueWaves/Sevarog_Health_Critical_010_Dialogue`<br>`.../Sevarog_Health_Low_010_Dialogue` | Play at most once per duel |
| **Player Kill / Boss Victory** | Greystone HP reaches `0` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Kill_Enemy` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/DialogueWaves/Sevarog_Kill_Enemy_010_Dialogue`..`070`<br>`.../Sevarog_Catchphrase_010_Dialogue`..`050`<br>`.../Sevarog_Status_Victory_010_Dialogue`..`050` | Play 1 random kill/catchphrase line after player death hitstop settles (`+0.5 s`) |
| **Boss Defeat / Death** | Sevarog HP reaches `0` (`Death_front` window) | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Death` | `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/DialogueWaves/Sevarog_Death_010_Dialogue`<br>`.../Sevarog_Death_020_Dialogue`<br>`.../Sevarog_Death_030_Dialogue`<br>`.../Sevarog_Status_Defeat_010_Dialogue`..`030` | Highest voice priority; cancels queued non-death barks immediately |

---

## 3. Excluded Pack Cues (Do Not Wire)

- **MOBA/Draft Callouts:** `Sevarog_DraftLock*`, `Sevarog_DraftSelect*`, `Sevarog_Level_BoughtItem*`, `Sevarog_Level_CardPoints*`, `Sevarog_Status_OrbPrimeActivated*`, `Sevarog_Status_Recall*`, `Sevarog_Status_TeamDead*`, and hero-specific MOBA lore (`Sevarog_Lore_Cassiel*`, `Countess*`, `Serath*`) break Soulslike duel immersion and are **explicitly excluded**.

---

## 4. Audition & Opt-In Contract

1. All bark fields remain unassigned (`nullptr` default) in C++ and DataAssets until Owner auditions and picks preferred `SoundCue` / `DialogueWave` items.
2. Under `-nosound` automation runs (PIE harness / headless verification), zero audio components spawn and bark triggers must remain non-blocking no-ops.
3. No Paragon pack assets under `/Game/ParagonSevarog/` are modified.
