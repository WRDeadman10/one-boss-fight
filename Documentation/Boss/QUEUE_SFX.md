# Queue SFX — Boss Duel Audio Implementation

**Authority:** Project Owner Order & Claude Directive `[C-1169]` (2026-11-09).  
**Owner:** Antigravity (`Art/Review/Audit [A-###]`).  
**Rules:**
- Use **ONLY** content already present in the project repository (`ParagonSevarog`, `ParagonGreystone`, `ParagonGrux`, `ParagonSteel`, `RealisticSwordSoundEffects`, `AdvancedARPGCombat`, `StarterContent`, `Vefects`). No external downloads, no external services.
- Every sound addition is strictly **optional/opt-in data** with baseline silence/existing behavior as default until approved by ear by the project owner.
- Follow `ENGINE_LOCK.json` protocols; launch editor commands with `-nosound` during wiring/verification.

---

## Batch 1 — SFX Foundation & Candidate Audit

| Task | Work | Acceptance Criteria |
|---|---|---|
| SFX-01 | **Coverage Table & Gap Audit:** Map every gameplay event (Player, Boss, World) to current audio cue/class and file:line call site; identify and categorize all missing audio gaps. | Complete audit table in `Documentation/Boss/SFX_01_GAMEPLAY_AUDIO_AUDIT.md` citing exact source and asset paths. |
| SFX-02 | **Candidate Selection (1–3 per gap):** Select high-fidelity candidate sound cues from repository asset packs for top-priority gaps (Parry Success, Boss Parry Recoil, Phase 2 Aura Ignite, Backstep Whoosh, Stance Break Shatter). | Documented candidate list with asset paths, durations, volume/pitch profiles, and design rationale. |
| SFX-03 | **Owner Audition Pack:** Compile candidate audio cues into a labeled audition reel (`.mp4` / audio showcase) in `Docs/BossCombatReview/Execution/Antigravity/SFX/` for Owner review. | Audio reel generated with on-screen/labeled cue IDs for blind A/B evaluation by the Owner. |
| SFX-04 | **Wiring Plan (No Apply):** Specify exact integration attachment points (AnimNotifies on Montages, C++ Event Dispatchers, `URPGPlayerParry`, `URPGTier2BossPresentation`, `URPGBossStagger`). | Scripted, fail-closed wiring plan with refuse-if-exists assertions and verification contracts. |
| SFX-05 | **Verification & Staged Rollout:** Implement Owner-approved audio cues under `ENGINE_LOCK`; verify playback via diagnostic log markers during Lead PIE. | Live execution logs proving cues trigger at exact frame/timestamp without clipping or hitches. |

---

## Batch 2 — Combat Impact & Reaction Audio (Upcoming)

| Task | Work | Acceptance Criteria |
|---|---|---|
| SFX-06 | Player Guard Counter clash & heavy impact sound. | Auditioned and wired to `GuardCounter` montage impact. |
| SFX-07 | Player Air Plunge crash & ground shockwave audio. | Tied to `AM_ER_Attack_Air_Heavy_Plunge` land frame. |
| SFX-08 | Boss A4 Low Sweep blade ground friction whoosh. | Wired to `AN_Boss01_A4_LowSweep` active blade arc. |
| SFX-09 | Boss A5 Javelin throw summon & release whooshes. | Resolves KI-068 audio placeholder for A5. |
| SFX-10 | Boss Stance Break / Posture Shatter heavy glass/stone impact. | Wired to `URPGBossStagger::StartStagger` entry. |
