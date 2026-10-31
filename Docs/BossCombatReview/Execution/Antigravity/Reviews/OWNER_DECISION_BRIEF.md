# Owner Decision Brief

> **Purpose:** Single-page summary of every pending item waiting on an Owner decision, compiled strictly from repository records.  
> **Rule:** Every claim cites an exact `file:line` in repository documentation with verified verbatim text.

---

### 1. Cook Scope for ParagonSevarog (`KI-143`)
- **What is blocked:** First packaged build containing the boss character. `Content/ParagonSevarog` (1.4 GB) is excluded from `DirectoriesToAlwaysCook`, so packaged builds will not cook the boss mesh or animations.
- **Options:**
  - *Option A:* Add the entire `Content/ParagonSevarog` folder (~1.4 GB) to `DirectoriesToAlwaysCook` in `Config/DefaultGame.ini`.
  - *Option B:* Audit and cook only the specific subset of needed assets/subfolders required for the boss.
- **Lead Recommendation:** "Decide the cook scope (whole folder or the needed assets) before the first Sevarog packaged build."
- **Repository Citations:**
  - `Documentation/KNOWN_ISSUES.md:254`: `Decide the cook scope (whole folder or the needed assets) before the first Sevarog packaged build.`
  - `Documentation/TASKS.md:45`: `Decision 1: Cook scope for ParagonSevarog`
  - `Documentation/DECISIONS.md:1233`: `shipping the Sevarog boss needs its content in DirectoriesToAlwaysCook (owner decision, about 1.4 GB, not made)`

---

### 2. NullRHI Headless Actor Spawning (`KI-144`)
- **What is blocked:** Headless commandlet execution (`UnrealEditor-Cmd -nullrhi`) for automated level authoring and PIE proofs (`unreal.EditorLevelLibrary.spawn_actor_from_class` crashes with `EXCEPTION_INT_DIVIDE_BY_ZERO`).
- **Options:**
  - *Option A:* Accept engine behavior and execute level authoring / proof drivers in the windowed editor (`Claude/run_editor_script.ps1 -NullRhi 0`).
  - *Option B:* Re-architect actor spawning in native C++ to bypass `EditorLevelLibrary` in commandlet modes.
- **Lead Recommendation:** "Run level authoring and proof drivers in the windowed editor (Claude/run_editor_script.ps1 -NullRhi 0 [-PyCmd 1])."
- **Repository Citations:**
  - `Documentation/KNOWN_ISSUES.md:255`: `Run level authoring and proof drivers in the windowed editor (Claude/run_editor_script.ps1 -NullRhi 0 [-PyCmd 1]).`
  - `Documentation/DECISIONS.md:1235`: `EditorLevelLibrary spawns crash (INT_DIVIDE_BY_ZERO) in -nullrhi UnrealEditor-Cmd`

---

### 3. Phase-2 and Stagger Animations
- **What is blocked:** Visual presentation for boss stance break / stagger (currently logic-only; the boss breaks and recovers but freezes in place) and dedicated Phase 2 transition presentation (currently uses proof cards and logic-only latching without roar/transition montage).
- **Options:**
  - *Option A:* Author or source dedicated skeletal animations / montages for stagger (hit reaction, kneel, recovery) and phase 2 transition (roar / power-up).
  - *Option B:* Retarget existing Paragon Sevarog animations.
  - *Option C:* Retain freeze-in-place placeholders for framework proof verification.
- **Lead Recommendation:** no recorded recommendation
- **Repository Citations:**
  - `Documentation/DECISIONS.md:1258`: `No stagger animation yet (the boss freezes in place): known limit.`
  - `Documentation/TASKS.md:695`: `Open: break in neutral, regen-to-full, stagger animation.`
  - `Documentation/DECISIONS.md:627`: `The roar, transition montage and immunity dependencies are still open for a later reviewed package`

---

### 4. HUD and Boss Health Bar Integration
- **What is blocked:** Final HUD presentation and native framework boss health bar display in shipping play (legacy custom C++ `RPGHUD.cpp` was deleted; the pack's HUD replaced it but framework boss health is only read via `RPGPack::ReadAttribute` and HUD bar remains unverified in proof maps).
- **Options:**
  - *Option A:* Retain the Advanced ARPG pack's UMG HUD and boss bar, wiring native framework boss health reading into it.
  - *Option B:* Restore and maintain custom C++ canvas/UMG HUD (`RPGHUD.cpp`).
- **Lead Recommendation:** "Confirm with the owner before building or committing"
- **Repository Citations:**
  - `Documentation/KNOWN_ISSUES.md:45`: `Confirm with the owner before building or committing`
  - `Documentation/KNOWN_ISSUES.md:54`: `the pack's menus, input and HUD replace ours and have not had a controller playtest`
  - `Documentation/DECISIONS.md:258`: `The pack's HUD and boss bar; its own menus`
  - `Documentation/TASKS.md:691`: `physics-asset coverage, double OnHit per sweep and the HUD bar stay UNVERIFIED.`

---

### 5. Blood Effect and Sound
- **What is blocked:** Audio-visual feedback on boss bleed procs on the native framework boss (legacy `URPGBossBleed` effect/sound are not ported to the framework boss; realistic blood pack `Content/BloodPack` spawns nothing visible in UE 5.5).
- **Options:**
  - *Option A:* Delete `Content/BloodPack` or find a working UE 5.5 replacement Niagara blood effect and port impact sound/VFX to the native framework boss.
  - *Option B:* Leave bleed procs as numerical attribute loss without visual/audio VFX for proof lane.
- **Lead Recommendation:** "Delete Content/BloodPack or find a replacement"
- **Repository Citations:**
  - `Documentation/KNOWN_ISSUES.md:28`: `Delete Content/BloodPack or find a replacement`
  - `Documentation/DECISIONS.md:1264`: `No blood effect or sound yet (the legacy component's effect/sound are not ported): known limit.`

---

### 6. Whether Any D3 Reference Numbers May Enter Ember Warden Cards
- **What is blocked:** Injection or application of measured reference timings (Windup, Active, Recovery, Total) from the reference video study (`D3_MEASURED_LEDGER.json`) into runtime Ember Warden combat cards (`Content/OneBossFight/FrameworkProof/Cards/`).
- **Options:**
  - *Option A:* Strictly maintain "DESIGN INPUT" status only; prohibit direct injection into runtime cards without explicit owner direction and validation.
  - *Option B:* Author candidate Ember Warden cards based on selected reference timings subject to formal owner approval and proof verification.
- **Lead Recommendation:** "Under NO CIRCUMSTANCES may any data from this study be copied, pasted, or injected into shipped gameplay assets or runtime cards located in Content/OneBossFight/FrameworkProof/Cards/ without explicit, formal direction and sign-off from the project Owner."
- **Repository Citations:**
  - `Docs/BossCombatReview/Execution/Antigravity/Reviews/D3_FINDINGS.md:67`: `Under **NO CIRCUMSTANCES** may any data from this study be copied, pasted, or injected into shipped gameplay assets or runtime cards located in Content/OneBossFight/FrameworkProof/Cards/ without explicit, formal direction and sign-off from the project **Owner**.`
  - `Documentation/TASKS.md:26`: `D3 (Footage Measurements): IN PROGRESS (Claude; 0 of 8 clips filled in D3_MEASURED_LEDGER.json).`
  - `Documentation/DECISIONS.md:1258`: `Values 100 / 60 / 1.0 s / 6 s / 13 per s are proof values, proposed.`

---

### 7. Push of Unpushed Commits
- **What is blocked:** Remote synchronization of recent commits to `origin/main`.
- **Commit Count & Subjects:** Exactly 10 unpushed commits ahead of `origin/main`:
  1. `3d9debd4 docs: D3 findings fix`
  2. `409ba526 docs: D3 findings 2/9`
  3. `2d4bf763 docs: D3 ledger 1/9 + ingest --partial`
  4. `7dee334d docs: D2 template: mace slam entry`
  5. `6fedcae0 docs: Track D reference measurement dashboard and BUILD-95 test plan update`
  6. `acc88060 docs: D5 ledger fill tool, ingest integration, and test suite`
  7. `0620a775 docs: D4 contact sheet tooling, HUD-safe relative font sizing, and test suite`
  8. `bb04eb95 docs: D2 measurement ledger template, ingest script, and test suite`
  9. `cb9826e3 docs: D1 reference measurement protocol (82-row classification, ffmpeg 59.94 fps method, test 11/11, Morgott reference video link)`
  10. `b455740b proof: KI-146 dodge i-frame (inject_action IA_Dodge), notes, test 38/38, Claude/KI146 runs, KNOWN_ISSUES/TASKS/TEST_PLAN/gitignore`
- **Options:**
  - *Option A:* Owner executes `git push origin main` directly, or explicitly instructs Claude to push.
  - *Option B:* Keep commits local on development machine until Track D study is fully completed.
- **Lead Recommendation:** "The user commits on their own; never commit or push unless asked."
- **Repository Citations:**
  - `Documentation/PROJECT_STATE.md:89`: `The user commits on their own; never commit or push unless asked.`
  - `Documentation/TASKS.md:44`: `pushed to origin/main by Claude on the owner's explicit word; Antigravity still never pushes on its own.`

---

### 8. Optional `git gc --prune=now` of `.git` Garbage
- **What is blocked:** Reclamation of disk space from stale interrupted git write artifacts.
- **Size / Measurement:** Exactly 66 files summing to 152,566,102 bytes (~145.5 MB) matching `*tmp_obj*` in `.git/objects/`.
- **Options:**
  - *Option A:* Execute `git gc --prune=now` to clean up the 145 MB of temporary object files.
  - *Option B:* Leave temporary object files untouched until a scheduled repository maintenance window.
- **Lead Recommendation:** "please run git prune / git gc --prune=now only after the owner agrees (not now)"
- **Repository Citations:**
  - `Documentation/TEAM_MAILBOX.md:11383`: `please run git prune / git gc --prune=now only after the owner agrees (not now)`
