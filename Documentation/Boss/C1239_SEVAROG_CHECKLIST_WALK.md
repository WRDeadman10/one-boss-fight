# C-1239: Sevarog walk through the new-boss checklist

**Status:** Historical paper walk plus follow-up. No Sevarog definition, montage, annotation, or runtime wiring was created. A-720 has since supplied the proposed move list; the requested data-only definition plan is in `C1239_SEVAROG_DEFINITION_DATA_PLAN.md`.

## 1. Definition asset: not ready

The checklist requires a unique definition/presentation identity and source-backed values for required stats, phases, presentation, and component configs. No Sevarog definition asset or Sevarog source manifest was supplied with the accepted probe. C-1237a established the generic timing opt-in: keep `bUseMontageNotifyTimings` false until annotations pass strict audit, then enable it on this boss with a source-manifest field. No values or asset path are proposed here.

**Gate:** wait for the inventory and move list; then select only values supported by source/readback and identify what is represented by existing adapters. Run definition/preflight plus native binding coverage after a concrete plan is authored.

## 2. Animation inventory and annotation: probe passed, authoring not ready

Claude reports the guarded Sevarog probe completed with exit 0, no Python errors, no missing assets, and no Content changes (C-1239). The log confirms these Category A montage facts:

| Montage | Readback | Source |
|---|---|---|
| `Swing1_Medium_Montage` | 1.133317 s; one `Default` section; root motion `n/a`; two notify classes `Unknown` | `Docs/BossCombatReview/Execution/Claude/P_C1239_SEVAROGPROBE/probe_sevarog.log:1154-1155` |
| `Swing2_Medium_Montage` | 1.133317 s; one `Default` section; root motion `n/a`; two notify classes `Unknown` | `Docs/BossCombatReview/Execution/Claude/P_C1239_SEVAROGPROBE/probe_sevarog.log:1156-1157` |
| `LevelStart_Montage` | 5.000000 s; one `Default` section; root motion `n/a`; one `AnimNotify_PlayParticleEffect` | `Docs/BossCombatReview/Execution/Claude/P_C1239_SEVAROGPROBE/probe_sevarog.log:1158-1159` |

The probe enumerates 28 Category B melee sequences at `probe_sevarog.log:1161-1188` and 11 Category C signature sequences at `probe_sevarog.log:1190-1200`. Those sequence rows report lengths, `root_motion=False`, and zero notifies. The probe does not report a sequence section count, so this walk does not infer one. Candidate combat roles in the earlier inventory plan are hypotheses, not verified move mappings.

The initial probe's two swing montage notify classes were unresolved. C-1240 reports that the guarded v2 rerun identified `SaveAttack` and `ResetCombo` on both montages; these are combo-chain markers and do not supply timing values. Until an authored move/timing table is reviewed, do not author timing annotations or enable the timing flag. No strict timing audit has been run for Sevarog.

**Current gate:** the inventory and proposed move list now exist with source citations. Lead still needs to rerun the guarded notify-name probe, then review the move contracts and produce source-backed timing evidence. Only then adapt the authoring workflow for Sevarog's own assets and run strict audit. Never retarget another boss's animation assets for Sevarog.

## 3. Timing parity PIE: not eligible yet

The C-1239a parity driver now logs per-tick deltas, discards attempts with any delta above 0.1 s, retries up to three times, and compares only complete clean trials. Offline contracts pass 13/13; no Sevarog PIE result exists. The checklist's Sevarog parity gate still requires a source-backed definition with timing opted in, passing annotations/strict audit, a fresh run-specific log, and Lead review of the off/on comparison for representative common moves.

**Gate:** do not call the third-boss pipeline proven until the Lead accepts that PIE receipt. Keep pack parry/collision-trace evidence separate from tracker-timing parity.

## 4. Code-only add-ons: initial walk deferred; follow-up plan available

The initial walk preceded the move list and did not classify individual moves. The follow-up plan maps each proposed move to the typed definition/tracker shape and lists mechanics that need a verified reusable ability or code add-on, including the root-displacement decision. Those classifications remain provisional until Lead reviews the move behavior and confirms whether an existing runtime route implements each contract.

**Follow-up:** `Documentation/Boss/C1239_SEVAROG_DEFINITION_DATA_PLAN.md` is plan-only. It excludes all A-720 estimated timing ranges from runtime values and leaves the definition asset, source manifest, stat/policy values, and timing windows TBD.

When the move list arrives, mark each move against the existing schema. Any unique decision rule, custom target selection, custom phase behavior, new interaction/contact semantics, new runtime component/adapter, or timing semantics the tracker cannot represent must be listed as a bounded code add-on with its own native tests before implementation.

## Current next steps

1. Finish the cited asset inventory and resolve the unknown montage notify names with the guarded probe rerun.
2. Produce the Sevarog move list with candidate sequences and readback lengths; distinguish proposed roles from confirmed runtime behavior.
3. Draft the source-backed definition plan from that move list and identify data-only versus code-required moves.
4. Continue through authoring, strict audit, and Lead-owned parity PIE only after the earlier gates pass.
