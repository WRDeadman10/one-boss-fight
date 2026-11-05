# Queue Z Batch 2 — player action and input lifecycle

Status: Z006–Z010 complete locally. Static source/test inspection plus re-reading retained Claude PIE evidence; no new tests or Unreal runs. Runtime observations below are historical PIE evidence, not a packaged/Shipping acceptance claim.

## Z006 — shared input bindings and action outcomes

| Input action | Source binding and outcome | Key/mapping evidence |
|---|---|---|
| Dodge | `URPGDodgeTiming::TryBind` binds pack `IA_Dodge` on `Started` to `OnDodgePressed`; handles quick/double-tap montage selection and consumes the release for forced full roll (`RPGDodgeTiming.cpp:22–32,117–134,292–336`). Pack ability still executes movement/stamina. | Exact keyboard/gamepad mapping is not encoded in `Config/DefaultInput.ini`; it configures Enhanced Input classes only. `Content/OneBossFight/Input/IMC_Default.uasset` exists (SHA-256 `1d9c25faa48e5520a6d9e437acf0455d44e41697799f896b85759125b510ef73`) but is binary and its mappings were not independently decoded in this audit. Historical mapping table `V_A042_INPUT_MAPPING_AUDIT.md` claims Space/B; treat as prior audit, not newly verified key-level evidence. |
| Parry | `URPGPlayerParry::TryBind` binds pack `IA_Parry` to `Press`; opens timed window, sets tag and optionally spends/refunds stamina (`RPGPlayerParry.cpp:17–64,73–112`). | Input context ownership is external Blueprint/pack setup. No key-level mapping confirmed from text config or source. |
| Riposte | `URPGRiposteInput` binds pack `IA_NormalAttack` to `OnLightAttack`; scans the active boss and calls `TryRiposte` only while staggered (`RPGRiposteInput.cpp:14–19,36–72`). | No key mapping independently confirmed. |
| Light/heavy attack, move/look, jump, lock-on | Existing `V_A042_INPUT_MAPPING_AUDIT.md` supplies a proposed/previous mapping table; maintained C++ inspected here does not bind the ordinary attack/light/heavy/move/look/jump/lock-on actions. The swing tracker observes pack attack montages instead (`RPGSwingTracker.cpp:132–202,214–232`). | Actions and key assignments reside in binary `IMC_Default` and pack Blueprints; no current export/Editor inspection was available. Do not call the previous audit's “100% bound to live C++/Blueprint delegates” independently verified by this source pass. |

`DefaultInput.ini` has `DefaultPlayerInputClass=/Script/EnhancedInput.EnhancedPlayerInput` and `DefaultInputComponentClass=/Script/EnhancedInput.EnhancedInputComponent`, but no legacy `ActionMappings`. The project content tree contains local `IA_LightAttack`, `IA_HeavyAttack`, `IA_Dodge`, `IA_Block`, and `IMC_Default`; C++ references the pack's separate `IA_Parry`, `IA_Dodge`, and `IA_NormalAttack`. The current mapping asset hash is included so a future export can be tied to inspected bytes. A key-to-action census remains UNKNOWN pending asset/Blueprint export.

## Z007 — dodge montage and i-frame windows

Configured source defaults are a 0.30 s double-tap window, quick montage at 1.30 play rate, full montage at 1.0 play rate, and the pack dodge ability/input tags (`RPGDodgeTiming.h:34–77`; constructor asset paths in `.cpp:22–33`). The i-frame monitor observes the pack's `Status.Invulnerable` tag and reads each montage's `ANS_iFrames` notify window (`RPGIFrameMonitor.h:13–22`; `.cpp:184–235`); it does not author invulnerability.

Retained historical evidence `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/pie_iframes_t2b/` has 19 parity observables, all `MATCH`, no comparator issues, and result exit 0. Its legacy/data raw log hashes are respectively `147acf4cfb5d8173bb5f8d58369f972b7a7f3a0a68278b729e26bbe3ad29a591` and `d03940a203770bc3ad6b6f3d206f9144162503be1936bdbf8b0fc177256fe931`; parity report SHA-256 `eeea117bdb82e6282d4ccc3a5f064c802a75c999c63c278b51572266a4975f66`. The data log recorded quick montage `Dodge_Small_Forward_Roll_Montage`, rate 1.30, notify window 0.107–0.490 montage seconds; full montage `Dodge_To_Idle_Montage`, rate 2.00, notify window 0.000–0.700. On that PIE setup, measured tag intervals were 20/20 at each 30/60/120 FPS route for quick and full: about 0.267/0.300/0.292 s quick and 0.367/0.350/0.350 s full (legacy/data matched). Chained quick-to-full checks passed 10/10 at both 0 and 0.04 s delay; interrupted-roll cleanup passed 10/10 each; reset cleanup 5/5; watchdog 5/5; foreign tag preserved 5/5.

This is historical Editor/PIE data, not live packaged contact verification. In particular `AN1_AN4_ART_AND_ANIMATION_INVENTORY.md:57` says a 0.8 s forward roll with 12 i-frames from 0.00–0.20 s. That description does not match the currently configured quick montage and retained measured notify window above; label the older inventory row STALE pending asset re-export/review, rather than using it as current timing. The PIE log also has Blueprint pending-kill errors during forced-dodge cleanup near the end of the run; the parity result passed, but those errors remain a run-quality caveat for any claim about cleanup under teardown.

## Z008 — parry-to-riposte eligibility

Contact path: `RPGDamageResolver` resolves alive/generation/duplicate/i-frame/parry gates in that order and calls `URPGPlayerParry::NotifyParried` only for a `Parried` result (`RPGDamageResolver.cpp:151–185`; `RPGDamageResolver.h:96–104`). A parry records its grade and pending half-refund; tag closes when the rule window expires, then charged parries refund half and whiffs keep the full cost (`RPGPlayerParry.cpp:142–155,158–185`). The parry itself does not directly trigger riposte; the player's `IA_NormalAttack` press drives the separate riposte binding.

Riposte gates (`RPGBossStagger.cpp:497–550`): boss must be down (reject if still in fall clip), riposte unused, player not dead when health is readable, and horizontal geometry must pass configured range/cone/facing (`RPGBossStagger.h:46–57`; math helper in `RPGBossMath.h`). Accepted input runs paired clips if enabled and successfully loaded; otherwise it arms the next hit for a critical within `RiposteArmSeconds`. Shared pure tests cover parry window/cooldown/priority, cost arithmetic, and grade boundaries (`RPGParryTests.cpp`, `RPGParryCostTests.cpp`, `RPGParryGradeTests.cpp`, `RPGParryAdjacentWindowBoundaryTests.cpp`). Stagger adapter tests cover binding and profile validation, but no live Enhanced Input or integrated contact-to-riposte route is established by those tests. Negative gaps include unreadable player health behavior (source proceeds to geometry), exact geometric boundaries at the component gate, teardown during paired execution, and press occurring after stagger exit; no defect inferred.

## Z009 — stamina payment and regeneration ordering

Pack melee ability pays its own baseline, assumed 15 by `URPGSwingTracker` (`RPGSwingTracker.h:53–59`). On observed montage start, tracker classifies weapon/kind, finds a table row, then applies only `max(0, wantedCost - baselinePaid)`; row cost `-1` leaves pack cost unchanged (`RPGSwingTracker.cpp:214–266`; `RPGSwingRules.h:45–56`). Its extra payment is limited to readable current stamina; successful writes are clamped to readable max. Failed attribute operations do not retry or roll back the differential. A missing row leaves the pack baseline. `LoadOrDefault` prefers the configured table asset and otherwise uses `FillDefaults` (`RPGWeaponAttackTable.cpp:110–119`), so the following are code defaults, not proof of the selected runtime asset values:

| Weapon row | Source cost | Effective tracker behavior relative to 15 pack baseline |
|---|---:|---|
| Claymore Strength light | -1 | preserve 15; Freeze target 35 remains KI-190 discrepancy |
| Sword starter Strength light | -1 | preserve 15; same discrepancy |
| Claymore Strength Strong/Charged/JumpHeavy/Knockdown | 35 | add 20 extra |
| Sword starter Strength heavy rows | -1 | preserve 15 |
| Dexterity light/strong/charged/jump light/jump heavy/knockdown | 10 | refund 5 after pack's assumed 15 |
| no matching row/fallback | -1 | preserve pack value |

Parry has separate optional direct cost (default 0), precharged before the timing rule, rollback on cooldown rejection, half-refund on confirmed parry and bounded retries; its CVar is a Development-only test hook (`RPGPlayerParry.cpp:13–15,73–112,147–185`). No code-level stamina regeneration ordering was found in `RPGSwingTracker`; recovery is pack-owned and beyond this C++ audit. Prior retained `PLAYER_STAMINA_SPEND_REFUND_AUDIT_D27.md` documents remaining attribute failure and baseline assumptions. `RPGAutomationTests.cpp:568–578` tests pure differential arithmetic; `RPGParryCostTests.cpp` tests pure direct-cost arithmetic. They do not establish current asset row overrides, pack baseline for every montage class, or timing against real regeneration.

## Evidence boundary and next review

Static source, docs, assets presence/hash, and retained historical PIE receipts only; no tests, Editor, build, or package run in this batch. Lead/Editor mapping export is needed to close the actual key-to-action map and current asset-value questions. Receipt: Z001–Z004 findings linked in the prior report; this report closes Z006–Z009 and the batch receipt Z010.
