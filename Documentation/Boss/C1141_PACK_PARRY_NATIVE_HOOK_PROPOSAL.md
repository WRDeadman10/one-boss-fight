# C-1141 pack parry native hook proposal

Date: 2026-11-09  
Status: Implemented locally per Claude approval C-1142; Lead BUILD-272, native automation, and parry-close runtime verification are pending. No Codex build or Unreal run.

## Finding

The pack's `SM_ImpactDecision` Blueprint owns the exact impact verdict. Native code has no callback/delegate for its `ImpactDecisionTag` or `ParriedHit` result in the checked path. The documented resolver is explicitly limited to project-authored A4/A5/A6 geometry (`Source/OneBossFight/Player/RPGDamageResolver.h:118-122`); its `Parried` branch spends the hit and calls `URPGPlayerParry::NotifyParried` (`RPGDamageResolver.cpp:187-190`). That resolver cannot be treated as the pack-trace callback.

The earliest current native-observable pack-contact boundary is the boss trace target's `HitActors` set. `RPGPackTrace::FTarget` exposes a read facade for that Blueprint target (`Source/OneBossFight/Pack/RPGPackTrace.h:12-19,24-31`). `URPGTraceAudit` sees a new player insertion after the pack sample, checks/ignores the wall-gate seed, and starts its damage-resolution observation (`Source/OneBossFight/Player/RPGTraceAudit.cpp:325-351`). Its tick is `TG_PostUpdateWork`, after the pack sample, but disabled in Shipping (`:24-32`), and its counters alone do not establish a parry verdict. Pack trace auditing is attached to pack bosses at `RPGPlayerMovesSubsystem.cpp:865-868`.

Lead's C-1141 capture gives runtime evidence that all six sampled contact markers had `Status.ParryActive=true` and no HP loss. That supports the gameplay gap; source cannot establish the precise internal order between the Blueprint decision branch and `HitActors` insertion.

## Approved native hook and flow (C-1142)

1. Added `URPGPackParryContact` and attach it to each pack boss beside `URPGDamageResolver` and `URPGTraceGuard`. It samples `TargetType.MainWeapon` through `RPGPackTrace::FTarget` in `TG_PostUpdateWork`; unlike `URPGTraceAudit`, it is not disabled for Shipping. It does not modify pack assets.
2. New player HitActors insertion captures the native `URPGPlayerParry::IsWindowOpen()` state now or from the previous sample, requires a resolvable false `Status.Invulnerable` query and known player health, and ignores wall seeds/carried actors. It waits 0.1 seconds and rejects unknown health or any measured HP loss. It never consults the mirrored `Status.ParryActive` tag as authority; a stale true tag with the native window closed cannot create a candidate.
3. Tracked keys are encounter generation + boss ID + tracker move + attack instance. Untracked keys use generation + boss ID + active montage name + inferred world start time rounded to centiseconds. The shared reward call deduplicates before side effects. The A4/A5/A6 resolver uses the same tracked-key builder and shared reward entry, avoiding a second reward for the same attack instance.
4. A confirmed contact routes through the shared reward entry, which updates grade/ParriedCount, spark VFX, slow motion, and the existing Tier 2 recoil gate. `ParryPostureDamage` is optional and defaults to `0`; confirmed parry queues the configured amount for the posture component's next tick, after the observer's pack sweep. No value was invented.

## Verification

- Offline Python contract: `python -m unittest Scripts.Tools.test_pack_parry_contact_contract -v` — 7/7 passed. `python -m py_compile Scripts/Tools/test_pack_parry_contact_contract.py` passed; scoped `git diff --check` passed (line-ending notices only).
- Native Source automation registered (not run by Codex): `OneBossFight.Player.PackParry.CandidateRules` (window now/previous, closed native window despite mirrored tag, invulnerability, 0.1 s timing, health loss/unknown/non-finite); `OneBossFight.Player.PackParry.AttackIdentityAndDeduplication` (tracked/untracked identity, generation and cross-window dedupe); `OneBossFight.Player.PackParry.PostureDefaultIsInert` (default zero).
- Additional static checks: both pack observer and A4/A5/A6 resolver call `URPGPlayerParry::NotifyParried` with `RPGPackParry::BuildAttackKey`; candidate path excludes seeds/carried contacts; source observer has no Shipping compile gate.
- Lead's A-663 source audit, items 1–2: the `now || previous` native-window rule and the untracked key's montage/start/boss parts are at `RPGPackParryContact.cpp:129-137,57-77`; the explicitly native closed-window decision (no `Status.ParryActive` lookup in the observer) is guarded at `:130-136`; both pack and A4/A5/A6 resolver paths use the exact tracked key builder and single `NotifyParried` gate at `:66-67,156-162` and `RPGDamageResolver.cpp:187-192`, with dedupe before counters/effects at `RPGPlayerParry.cpp:153-165`. Item 3 cannot be assessed before Claude's BUILD-272 parry-close log; runtime evidence is still pending.

## Review boundary

The reflected hit-set boundary remains one native sample after the Blueprint trace sample rather than an exposed Blueprint verdict callback. C-1142 approved that boundary and the 0.1-second correlation/key/posture rules. Not yet established: UHT/C++ compilation, native automation results, or the observed live parry-close outcome (exactly one reward per attack plus Tier 2 recoil). Lead owns BUILD-272/full-suite and runtime evidence. Do not interpret these static/offline contracts as runtime proof.
