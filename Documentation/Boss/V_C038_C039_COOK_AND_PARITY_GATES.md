# V-C038–V-C039: Optional Asset Cook and Default-Parity Gates

## V-C038 — Cook coverage

Every new optional runtime load path must resolve under an explicit `DirectoriesToAlwaysCook` root and pass `OneBossFight.Content.CookCoverage` in the Lead build. The new A2 preview path is `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2.AM_Boss01_A2`; `Config/DefaultGame.ini` already cooks `/Game/OneBossFight/Boss01`, which covers it. The new Tier 2 aura, MPC, sound mix and recoil fields have no asset path/default assigned yet, so there is no additional content dependency to cook. When the owner approves and assigns any of those assets, add or verify its cook root before use; do not add a speculative content directory now.

## V-C039 — Default behavior parity

Offline static checks cover all 31 registered A5 parity drivers and ensure the new switches/fields default to no change. Lead should run the following five representative pairs with `rpg.AttackTracker.A2PreviewClip 0` and `rpg.Art.Tier2 0`, keeping raw logs and comparing typed gameplay observables to the BUILD-229 baseline:

| Driver | Default path covered |
|---|---|
| `pie_authored_close_clips` | A2 uses the pack montage; authored tracker timing and A1/A3 swap behavior |
| `pie_legend` | Parry slow motion, no MPC pulse or audio mix |
| `pie_phase_reset` | Phase/encounter reset, no aura retained |
| `pie_boss_death` | Death/cleanup, no recoil presentation |
| `pie_iframes` | Player defensive timing unaffected |

Acceptance: both routes complete each pair; all typed gameplay observables pass the existing parity comparator; no optional presentation counters/assets activate; cook coverage is green. Then the Development-only preview can be tested separately with approved assets. Codex did not run these pairs or Unreal.
