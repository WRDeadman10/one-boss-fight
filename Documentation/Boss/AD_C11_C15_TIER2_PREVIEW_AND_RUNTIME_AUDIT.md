# Queue AD-C11–C15 — Tier 2 preview and runtime audit

Date: 2026-11-07. Static source, test, and mailbox review only; no Editor, PIE, build, cook, package, or tests run by Codex.

## AD-C11 — `rpg.Art.Tier2` build scope

`RPGTier1VisualRules.cpp:7-36` declares the CVar only inside `#if UE_BUILD_DEVELOPMENT`, default `0`, and `IsTier2PreviewEnabled()` returns false on other builds. The pure predicate also requires Development and a nonzero CVar (`RPGPresentationRules.h:9-12`). Tier 2 hooks call this runtime predicate. Source therefore describes opt-in Development preview with default-off behavior. It does not prove compiled Shipping symbols or a packaged Development run; those remain Lead build/package evidence, as `AC_C21_C25_TIER2_READINESS_AUDIT.md` states.

## AD-C12 — parry distortion load and late enable

`URPGBossLegend::BeginPlay` synchronously loads `ParryDistortionMaterial` only if the CVar is already enabled and the optional soft reference is non-null (`RPGLegend.cpp:360-366`). `BeginParryFeedbackPulse` separately checks the CVar and uses only the retained loaded pointer; enabling the CVar after BeginPlay cannot load it (`RPGLegend.cpp:167-202`). It adds the material to the parrying actor camera, saving a preexisting weight when found. Restore returns that weight or removes only the added blendable, resets weak pointers, and restores pulse/sound state (`RPGLegend.cpp:243-262`). This is source-derived timing/cleanup behavior; no latency, first-use hitch, or actual rendering measurement is available here. C-982's accepted PPM look target is not engine material/runtime acceptance.

## AD-C13 — aura ownership and cleanup

`URPGSevarogDirector::ApplyPhaseTwoVisuals` is CVar gated, sync-loads the optional Niagara reference, spawns it attached to the boss skeletal mesh, and raises the optional MPC scalar (`RPGSevarogDirector.cpp:195-221`). The director retains and destroys the spawned component in `ClearPhaseTwoVisuals` (`:224-242`), called by component `EndPlay` (`:54-61`), encounter reset (`:453`), and the health-death branch (`:557-562`). Cleanup sets the applied MPC scalar to zero; it does not save/restore a prior scalar. Shared-writer impact is unknown. No dedicated native lifecycle test for these Tier 2 references/cleanup paths was found in the existing test inventory. Source callsites do not prove PIE visibility or cleanup timing.

## AD-C14 — recoil montage slot and failure paths

`PlayParryRecoil` returns false when Tier 2 is off, the montage is null, owner is not a character, mesh/AnimInstance is unavailable, or `Montage_Play` returns no positive duration (`RPGSevarogDirector.cpp:244-253`). The `ParryRecoilMontage` property is optional/null by default (`RPGSevarogDirector.h:58-62`). The parry caller treats this as optional presentation alongside its separate gameplay feedback (`RPGPlayerParry.cpp:142-168`). There is no explicit slot validation, alternate slot selection, or fallback montage in this helper. C-986 reports the asset is a DefaultSlot montage but also reports zero notifies; C-987 provides a HitReact_Back template notify proposal. The asset class/skeleton/length check does not demonstrate that the runtime boss AnimGraph consumes that slot, that the montage starts, or that it affects the boss. Lead's post-authoring asset readback and PIE remain necessary.

## AD-C15 — Lead Tier 2 PIE checklist

Use a fresh, identified Development build, empty-default assignment baseline, and explicit `rpg.Art.Tier2=1`; record build ID and raw logs. Keep the four cases separate:

1. **PPM material render:** verify material domain and instance, then parry with the CVar off/on. Capture camera blendable list and weight before/during/after; confirm prior weight restoration or owned-entry removal. Record that the new CVar must be enabled before component BeginPlay for the current load path.
2. **Recoil playback:** after C-987 authoring, verify montage asset identity, skeleton, length, notify readback, and slot. Trigger a successful parry; log `Montage_Play` result/current montage and capture full body/sword motion. Repeat null montage, missing AnimInstance/mesh if safely injectable, CVar off, and failed-play path; gameplay parry must continue when optional recoil returns false.
3. **Aura visibility/color:** use phase two with CVar off/on and assigned NS; capture before/after from the lit engine viewport. Check owner review of A-594 rather than treating the unlit preview as final. Confirm body armor unchanged, embers rise, and blade flame is visible.
4. **Cleanup:** after aura is active, exercise encounter reset, boss death, and component/actor teardown separately. Record Niagara component identity/validity/count and MPC scalar before/on/after; note current implementation's reset-to-zero behavior and any shared writer. Do not generalize one path to all.

## Mailbox acceptance ledger

C-982 accepts PPM as a look target only and requires Lead material/runtime verification. C-983 accepted recoil motion subject to reframe and aura shape subject to color correction. A-594 delivered the full-body recoil reframe and orange-red aura preview/MP4s. C-985 accepted those previews **for owner review**; owner appearance judgment and Lead runtime checks remain outstanding. C-986 found five montages have zero notifies; C-987 gives table data, but this audit has no Antigravity authoring/readback or Lead rerun receipt. No asset assignment, owner approval, runtime success, or cook proof is claimed.

## Later evidence update — A-597

The earlier C-11–C-15 statement that no authoring/readback existed is historical. A-597's five Lead lines now show the C-988 target notify rows on all five montage assets; AA-A08's GuardCounter FootStep row remains absent from that readback. This does not change the Tier 2 preview/runtime findings above and does not establish any PIE, owner approval/assignment, or cook result.
