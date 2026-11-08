# AN-C26–C30: Tier 2 Aura and Parry Evidence

Status: offline source/evidence reconciliation complete through C-1075. Codex made no VFX asset or presentation Source changes. Antigravity A-646 reports candidate-only boost values; Claude accepted that as asset readback, while the paired capture failed. Codex's capture-driver hotfix is implemented and awaits Lead rerun. Owner visual approval is still separate; Lead owns live PIE/cook.

## Source lifecycle

- `Source/OneBossFight/Boss/RPGTier2BossRules.h:8-22` keeps the preview CVar on, boss non-dormant, finite positive health, and health at or below 60% as the aura show gate; spawn is once until cleared.
- `RPGTier2BossPresentation.cpp:14-19` sets the system path and enables ticking only in Development. `:22-58` checks the preview flag and health/dormancy, clears when hidden, loads the Niagara system and attaches it at `NAME_None` on the pack mesh when the one-per-phase rule permits. This confirms an attached component is requested; it does not establish camera visibility or owner approval.
- `RPGTier2BossPresentation.cpp:71-84` destroys the component and resets the one-per-phase bit when gated off or on EndPlay. `RPGBossEncounter.cpp:328-368` resets phases during encounter reset; the live C-1042 probe separately witnesses that route.
- `RPGTier2BossPresentation.cpp:60-68` gates parry recoil on Tier 2 plus a successful parry and plays the configured montage. The parry screen effect has separate pulse/weighted-blendable lifecycle in `RPGLegend.cpp:167-216,259-301`; keep it separate from the boss aura.

## Two-route evidence matrix

| Evidence layer | Legacy/data status | What it establishes |
|---|---|---|
| C-1042 `P_C1042_AURA` lifecycle | Lead reports 6/6 each | No aura at full HP; one active aura at 50%; off removes it; re-enable restores it; encounter reset removes it; next phase can spawn it again. |
| C-1042 parry/PPM | Lead reports real contact and recoil; r5 stable frame means and visible RGB split | Runtime path and visual response in the focused capture; no full-fight appearance conclusion. |
| `FIGHT_VIDEO_REVIEW2_AG.md`, A-637 | Antigravity says aura is not discernible in the full-fight video at the cited Phase 2 samples, including open-silhouette shots | Camera-visible presentation was not established by that video; this does not contradict PIE component lifecycle. |
| Owner visual approval | No disposition for the boosted candidate recorded through C-1075 | C-1073 authorized candidate-only technical changes; this does not approve the visual result or change the original. Owner disposition remains open. |
| Cook/package | Open under KI-191 | PIE component evidence is not staged content or packaged runtime proof. |

`Scripts/Editor/pie_tier2_aura.py` and `test_pie_tier2_aura_offline.py` already provide the two-route lifecycle matrix and test exact component count/activity, including duplicate and inactive failures. No additional test is warranted by this review. The focused PIE probe mutates only the test encounter health/CVar/reset state and ends PIE; it makes no asset save. The full-fight report remains a separate visual observation.

## Current disposition

Keep KI-191 PARTIAL: aura lifecycle, parry recoil and PPM capture have focused PIE receipts; full-fight aura visibility is NOT VISIBLE; first-use and cooked/package proof remain open. A-645 reported baseline-identical candidate values; A-646 reports candidate-only boosts (accepted by Claude in C-1075). The paired comparison still failed: data PNGs were black, and the legacy transient candidate did not read back active. Codex hotfixed capture retry, activation, game-time settle, three discarded frames, complete-PNG decoding, mean-gray logging and a threshold on retained images. Lead rerun is pending; there is no visual verdict or owner approval. Antigravity's corrected A-637 result supersedes A-636 for visibility wording. Codex did not run Editor, PIE, build or package.
