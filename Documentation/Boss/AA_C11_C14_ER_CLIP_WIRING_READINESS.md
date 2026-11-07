# AA-C11–AA-C14 — ER clip wiring readiness

## AA-C11 — Backstep (ER-A1)

**Asset evidence:** `Docs/BossCombatReview/Execution/Antigravity/ER_ANIM/Backstep_Back/Backstep_Back.txt` reports a 0.467 s one-shot, 200 cm backward root motion, unchanged yaw, i-frames 0.067–0.267 s, input buffer at 0.267 s, and recovery at 0.467 s. The Blender review clip is present. The owner approval and Lead import/build are not evidenced here.

**Existing code contract:** `URPGDodgeTiming::BackstepMontage` is a soft optional field, default empty; standing taps choose it only when loaded. Empty retains the current roll path. `RPGDodgeInputRulesTests.cpp` covers the empty fallback, directional roll, and repeated standing backsteps.

**Import checklist:** preserve root motion and yaw; create/confirm the montage on the player skeleton and expected slot; map the clip's i-frame/buffer/recovery points to the pack's existing dodge ability notify semantics; confirm the root-motion axis is backward in Unreal; leave the field empty until approved and imported; then Lead builds and runs the standing/moving/double-tap hand cases.

## AA-C12 — Optional field check

The Lead's existing `RPGDodgeTiming.h` already declares `BackstepMontage` as `TSoftObjectPtr<UAnimMontage>` with no constructor default path, and the cpp only takes the backstep branch after `LoadSynchronous()` succeeds. The current native rule test checks that no clip preserves today's standing roll. No source edits were needed in this pass; this is source/test readiness evidence, not a new build result.

## AA-C13 — Guard counter (ER-A4)

**Asset evidence:** the delivered metadata reports 0.800 s, 100 cm forward root motion, unchanged yaw, windup 0.300 s, hit window 0.333–0.533 s, impact 0.433 s, recovery 0.800 s. Blender review is present under `.../ER_ANIM/Attack_GuardCounter/`.

**Integration gate:** only a successful blocked contact may arm the counter; held guard alone is insufficient. The framework move executor computes accepted `Guarded` outcomes from the contact-time block tag (`RPGFrameworkMoveExecutor.cpp`, `ApplyHit`) and the pure counter timing rules already exist. The player input route is R2 tap. Lead must approve/import the clip, wire its hit window to the existing attack/damage route, preserve empty-default behavior, and verify no duplicate/late counter.

## AA-C14 — Air attacks (ER-A2 / ER-A3)

**ER-A3 delivered:** 0.867 s in-place plunge; windup 0.200 s, hit window 0.367–0.533 s, landing impact 0.500 s, recovery 0.867 s. A-577 records its FBX, look render, and review MP4.

**ER-A2 delivered:** A-579 records `Attack_Air_Light` with FBX, look render, and review MP4. Its metadata reports a 0.567 s in-place clip, windup 0.133 s, hit window 0.200–0.333 s, impact 0.233 s, and recovery 0.567 s. A-579 also confirms all four clips were regenerated at 178.5 cm armature height with revised framing. No import or owner acceptance is implied.

**Wiring checklist:** for light, assign the approved ER-A2 montage to the airborne light path (`FallingAttackMontages`); for heavy, route the approved ER-A3 montage through the strong-attack path used by `air_heavy_selector.py`. Check montage slot/skeleton, airborne-only eligibility, hit-window/landing notifies, and ground fallback. No script, import, or live PIE proof is claimed here.

## Shared gates

Owner reviews each clip MP4 before Lead import. Every new field remains optional with today's behavior when empty. Lead owns asset import, build, PIE, and acceptance; this note is static readiness only.
