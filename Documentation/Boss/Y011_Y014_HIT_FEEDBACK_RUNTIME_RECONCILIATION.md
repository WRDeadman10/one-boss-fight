# Queue Y Y011–Y014 — hit feedback runtime reconciliation

Date: 2026-11-06. Reconciled the W-C037 source matrix with retained Lead BUILD-231 paired receipts and raw logs under `Docs/BossCombatReview/Execution/Claude/B_C835_PARITY/pie_legend_t2/`. No new Editor, PIE, build, game, or audio playback was run.

## Receipt identity and overall outcome

`identity.json` identifies BUILD-231 and `pie_legend`; legacy and selected-data receipts each report 25/25 checks, and `parity_report.json` reports identity, final marker, terminal, and observables all MATCH with zero issues. The evidence is a retained instrumented Lead PIE run, not a new package run or external video/audio capture.

| Artifact | SHA-256 |
|---|---|
| `identity.json` | `18db5c2aa42554fdb74db791cc82a8566a3ac626fcdf81d70f71cae952f5fd4b` |
| `parity_report.json` | `4250f704d32f4b6cdb33df1e8604ffbfa597e25bb9c42fdd22f5b23f32c8885e` |
| `legacy/editor_raw.log` | `60bd49aa323233ff00e719d8b2be6f283803d8fb952b5454547de72a859a61db` |
| `data/editor_raw.log` | `c55cdd17db7ea69a5cdff68ab1c38a851318a909dfac445f9a398d4c41b4a2eb` |
| `receipt_legacy.json` | `0487305908269894f3d5fb37155a6c9bebf96b13a4bc00f1641f6218264c1cfb` |
| `receipt_data.json` | `8ac4388b2e9ed0a92e74f520c5831dbae2378bf714ac151724998dac801cf70a` |

## Y011 — shake behavior versus authored settings

| Event/check | Raw-log result (each route) | What it supports | What remains unknown |
|---|---|---|---|
| A2 slam at 600 cm | One shake per swing, camera motion/rest; 5/5 | Instrumented runtime behavior at this distance | Exact serialized active Blueprint amplitude/frequency overrides |
| A2 slam at 1500 cm | One shake per swing, weaker distance-scaled camera motion/rest; 2/2 | Distance scaling and camera response | Same authored-value gap |
| A2 interrupted before active | No shake; 3/3 | Stance-break interruption behavior | Other attack interruption cases |
| A2 beyond outer radius (2800 cm) | Counted too far, no shake; 2/2 | Range refusal behavior | Exact active Blueprint settings |
| Phase-two roar | One shake per fight, camera moves/rests; 2/2 fights | Instrumented runtime behavior | Exact active Blueprint settings |
| A6 leap landing in phase two | One slam shake per leap; 3/3 | A6-linked shake event behavior | Visual readability/reaction response |

The source matrix remains accurate that `FRPGShakeSettings` fields are configurable and the active serialized values were not read back. These runtime assertions do not establish every authored amplitude/frequency value.

## Y012 — hit-stop evidence

L4 logs three measured riposte hit-stop durations per route:

| Route | Measured real durations (s) | Driver assertion |
|---|---|---|
| Legacy | 0.093370, 0.094613, 0.093948 | 3/3 pass; duration allowed 0.04–0.20 s |
| Selected data | 0.094032, 0.098086, 0.093614 | 3/3 pass; duration allowed 0.04–0.20 s |

The source-configured target is 0.08 s, so the observed values are approximately 0.013–0.018 s above target even though they satisfy the driver's broad interval. Preserve that distinction; this is measured Lead PIE timing, not evidence that the nominal 0.08 s duration is exact. The logs include the hit-stop exercise and result, not a synchronized external camera capture.

## Y013 — audio source-to-capture map

The retained `M0` check only confirms the Phase 2 music track is imported and assigned. It does not confirm audibility, mix levels, SFX onset, or which sound plays for a hit/parry/bleed event. W-C037's source mapping remains: bleed invokes its configured `LoadedSound`; the generic move cue executor may play a cue's authored `Sound`; the Legend parry slow-motion SoundMix is optional and null by default. No raw audio/video capture or event-to-asset playback receipt was found. Per-hit audio attribution remains unverified.

## Y014 — parry/riposte route reconciliation

| Route/event | Retained evidence | Limit |
|---|---|---|
| Nonlethal riposte hit-stop | L4 measured values above; source asks for 0.08 s at 0.05 dilation | Driver accepts 0.04–0.20 s; actual samples exceed target modestly |
| Perfect parry slow-motion | L8 raw logs report 0.30 world dilation, onset within two frames, restoration after about 0.35 real seconds; both route receipts are part of the passing pair | This is world-time feedback evidence; no SoundMix audibility proof |
| Gate-off control | L8 `rpg.Legend 0` control reports contact succeeds with no world dilation | Does not establish unrelated SFX behavior |
| Reset cleanup | L6 passes 3/3 restoration checks | Does not prove every external Blueprint effect/audio resource |

`pie_legend_t2/data/editor_raw.log` also records that a second perfect-parry contact before the 0.70 s parry cooldown is unreachable despite the 0.60 s feedback policy cooldown; no second feedback scope is claimed. This preserves the known criterion limitation.

## Disposition

This receipt upgrades specific instrumented PIE behavior and timing evidence over the earlier source-only X-C034 summary. It does not provide serialized shake property readback, per-event audio playback evidence, synchronized cinematic footage, or an owner's sensory/readability acceptance.
