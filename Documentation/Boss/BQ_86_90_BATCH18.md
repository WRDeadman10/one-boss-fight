# BQ-86..90: Queue BQ batch 18, SFX and aura scaffolds, shake and music knobs

C (implementer), 2026-11-13. Queue: `QUEUE_BQ.md`. Batch 17 (BQ-81..85) **stays blocked on O1** (X-1991; no owner decision found), as the queue specifies and X-2395 confirms.

**Scaffold only.** No asset, card, engine or commit. Owner, art and ENG hookups are marked as blocked below. Tests ran in-process: 4/4.

| Task | Result | Files |
|---|---|---|
| **BQ-86** (E1) SFX wiring scaffold, O2 | **new, awaiting review.** The engine side already exists: each move card's `FRPGBossCue` has a `TSoftObjectPtr<USoundBase> Sound` (`RPGBossMoveCard.h:40`), fired by the executor at `TimeSeconds`. The missing piece was the plan for **which** slots each card gets and a safe fill path. `Scripts/Tools/sevarog_sfx_cue_plan.py` is a library only. `cue_slots(rows)` derives slots from each card's own timings: windup at commit for every card; swing at active start for cards with hit windows; area release and resolve for S7; channel start for S8. Every `sound` is None, pending O2. `validate_picks(slots, picks)` checks an owner pick table before anything is authored. It refuses unplanned slots, non-`/Game` object paths and pack or Ref source roots, and it **reports** missing slots without filling them | `Scripts/Tools/sevarog_sfx_cue_plan.py` (new), `Scripts/Tools/test_sevarog_sfx_cue_plan.py` (new, 4/4 against the real authored rows) |
| **BQ-87** (E3) aura hookup, O3 | **reconciled: O3 is already decided and live.** DECISIONS 2026-11-09 (C-1168): the owner chose **Boost Lite**. C-1209 verified the authored copy (BUILD-280, 494/494, paired capture), and production `URPGTier2BossPresentation::PhaseTwoAuraEffect` points at `NS_Boss_PhaseTwoAura_BoostLite_Authored` (`RPGTier2BossPresentation.cpp:19`). The data route also carries `PhaseTwoAuraEffect` on the encounter binding (`RPGEncounterBinding.h:360`). **The queue's O3 gate is stale**; the Lead should drop O3 from QUEUE_BQ's pending list. Nothing to scaffold | none |
| **BQ-88** (E8) shake tuning knobs | **reconciled, already exists.** The final shake scale is `RPGLegend::ShakeScale(distance, InnerRadius, OuterRadius, Falloff) * GlobalShakeScale * rpg.LegendShakeScale` (`RPGLegend.cpp:475`). The per-shake settings, `GlobalShakeScale` and the accessibility CVar (clamped 0-1) are all tuning knobs today. Values are tuning, owner/M14 (O7) | none |
| **BQ-89** (E8) music tuning knobs | **reconciled, already exists.** `URPGBossMusic` exposes `Volume` 0.55, `PhaseTwoVolume` 0.40, `FadeInSeconds` 2.5, `FadeOutSeconds` 4 and `VictoryFadeOutSeconds` 3 as clamped UPROPERTYs, with pure intensity rules (`RPGBossMusicIntensityRules.h`, two test files). The music assets are O2/ART | none |
| **BQ-90** | this report | |

## Blocked actions (explicit)

- **O2 (owner):** the SFX picks. Then ENG: fill the cards' `cues` in `author_sevarog_draft_cards.py` from the validated pick table (today `cues: []`), run the transient dry run under C-1155, save, and read back.
- **O7 (owner/M14):** the shake and music values.
- **Lead:** stale O3 gate removed from `QUEUE_BQ.md` after A-981. Batch 17 remains blocked on O1.

## Note

`cue_slots` reads card rows through the author script's `build_candidate_specs`, the same path as the BQ-44 drift guard. If card timings are retuned, the slots follow automatically.

## Review disposition

Accepted at source/planning level after Antigravity independent review A-981 (2026-11-13). O3 was already resolved and the stale queue gate has been removed; O2 picks, O7 tuning values, and any ENG/ART authoring remain gated as listed above.
