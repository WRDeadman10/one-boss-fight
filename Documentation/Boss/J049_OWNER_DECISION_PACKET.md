# J049 — owner decision packet: selected encounter route

## Current evidence boundary (updated 2026-11-05)

- Claude reports BUILD-219 green at 461/461 as the current native suite baseline (C-835). BUILD-217 witnessed selected-route startup and same-world respawn/rebind in `L_SevarogArena`, with rebind generation 2; BUILD-214 validated the saved G044 draft definitions/manifest workflow. These are separate native/content/live claims.
- C-847 supersedes the prior G044 health figure: Claude's D2 asset update changed selected boss MaxHealth 1500→2000 and refreshed the manifest/selection hash; the live manifest passes validator hash checks. Q001–Q005's hash-verified historical receipts show A4 S9 FAIL, dormant-wake PASS, damage-path PASS, death-reset FAIL (pre-D2), telegraph FAIL (pre-H5), and boss-HUD FAIL 28/29 (pre-D2). Fresh BUILD-220+D2 A4/death-reset/telegraph/HUD pairs remain in progress per C-848. See `Q06_Q10_PARITY_DISPOSITION.md`.
- BUILD-219 `_r2` and five A5 pairs are captured (C-839). The BUILD-218 A4 S6 shortfall did not reproduce in `_r2` (both 14/14); A4 `_r2` still differs on S9 jump/roll observations. The selected death-reset pair records boss maximum health 1500 versus legacy 2000; HUD parity fails at selected component existence; damage path is inconclusive (0/17 selected); telegraph passes 26/26 both arms but has four exact text/value differences within the driver's stated ranges. Codex finalized telegraph receipts from closed logs after T1 and locally reran all six comparators with source-log hash verification; Lead review remains pending. Details: `P13_PARITY_MISMATCH_TRIAGE.md` and `P15_A7_PARITY_SUMMARY_DRAFT.md`.
- No authoritative selected-root cook manifest, packaged activation, complete matched A4/A5 parity set, or matched selected-route performance sample is in this handover. The read-only step sequence remains in `J041_J045_SELECTED_ROUTE_OPERATIONS.md`.
- Source audit finding for Shipping: the `rpg.EncounterDefinition` console CVar is compiled only outside Shipping, but `URPGEncounterSelectionSubsystem::SetSelectedDefinition` remains BlueprintCallable in every configuration. This source audit did not inspect Blueprint/content callers, so it cannot claim Shipping selection is impossible. Decide whether that API is an approved route or needs a guard before claiming Shipping readiness.
- Performance boundary: the project target remains packaged 1080p, average ≥60 FPS and p99 ≤16.67 ms on RTX 2060 Super; 120 FPS is stretch. Earlier benchmark runs used 5 s warmup/60 s capture, but no selected-route cold/warm sample count, matched-memory protocol or current target-adapter proof is approved. RDP remote-display readings do not support GPU claims.
- Claude owns builds, automation, Editor, PIE and cook execution. Codex has not run Unreal/build. The temporary `spawn_gate` diagnostic is nonshipping and default-off.

## Owner-only decisions

**Owner decision recorded 2026-11-05:** J049 Shipping selector policy is
**Option A**: the BlueprintCallable `SetSelectedDefinition` stored-object route
is approved for Shipping. No Source change is authorized or needed for J049.
The CVar and `-RPGBenchmark` selector remain non-Shipping. A7 is **Option B**:
retire legacy startup later, after the release gates close. Until then, legacy
remains fallback and parity control; no legacy removal or default change now.

### Shipping selector access (Queue L)

The CVar route is absent in Shipping, but the BlueprintCallable
`SetSelectedDefinition` API can create a selection request. Lead's scan found no
current Blueprint callers: the graph scan was inconclusive (zero exposed
graphs), while UTF-8/UTF-16 byte search found no hits in 11,738 Content
`.uasset`/`.umap` files. Lead concludes the approved route is currently unused.
With no selection, the current packaged startup uses legacy.

- **A — Approve the setter as a supported Shipping route.** First retain the
  selected-root graph/cook manifest, and packaged behavior proof once a real
  caller exists. The setter proof is deferred until the first real caller and
  is part of the A7-B retirement gate. **Source effect:** no code change; accept the
  existing all-config BlueprintCallable `SetSelectedDefinition` declaration
  (`RPGEncounterSelectionSubsystem.h:30`) and stored-object request path
  (`RPGEncounterSelectionSubsystem.cpp:79-82,95-98`) as supported Shipping API.
- **B — Exclude direct selection from Shipping.** Review a source/API guard and
  caller migration/validation plan, then verify the Shipping binary has no
  selector route and empty selection still uses legacy startup. **Source
  effect:** add a Shipping guard/removal to the BlueprintCallable declaration
  (`RPGEncounterSelectionSubsystem.h:30`) and its implementation
  (`RPGEncounterSelectionSubsystem.cpp:79-83`), and ensure
  `HasSelectionRequest()` cannot accept the stored-object branch in Shipping
  (`RPGEncounterSelectionSubsystem.cpp:95-98`). Preserve internal test access
  in non-Shipping builds. The actual guard shape and any Blueprint caller
  migration remain to be reviewed before implementation.

The G1 benchmark command-line parse/assignment is compiled only in non-Shipping
builds (`RPGEncounterSelectionSubsystem.cpp:58-67`), and the CVar fallback is
non-Shipping-only (`RPGEncounterSelectionSubsystem.cpp:127-129`). The generic
soft-path loader is shared, but the benchmark path remains empty in Shipping
because its only assignment is compiled out. This is not a source change or
policy decision for either J049 option.

Option A is selected for J049; no API or default was changed. See
`L026_L030_SHIPPING_SELECTOR_AUDIT.md`.

### A7 — retain or retire legacy startup

The owner selected Option B: retire the legacy startup route later, after the
release gates close. Until then, keep legacy as fallback and parity control;
make no legacy removal or default change now. Package/Shipping, performance,
content/cook closure, and recovery evidence remain in the gate table below.

- **A — Keep the legacy startup route available.** Continue using it as the
  control and empty-selection behavior while parity gaps and release gates are
  resolved.
- **B — Retire the legacy startup route later.** Consider only after Lead
  accepts complete matched parity (including an explicit disposition of the
  telegraph exact-value differences), selected-route package/Shipping and
  performance evidence, compatibility review, and a tested recovery path.

**Recorded decision: B, later after the release gates close.** No route/default
changed now. See
`P15_A7_PARITY_SUMMARY_DRAFT.md` for current findings and `P14_PARITY_PRODUCTION_CHANGE_PROPOSAL.md`
for the flagged test-first proposal.

| Decision | Current position | Evidence needed before deciding |
|---|---|---|
| Production default encounter definition | No default change now; legacy remains fallback until A7 Option B gates close. | Current typed asset readbacks, successful and refusal selected-route PIE, paired legacy/data evidence, rollback evidence. |
| Shipping selector | J049 Option A approved: existing Blueprint setter is an approved but currently unused Shipping route; with no selection the packaged game starts legacy. CVar and benchmark command-line selector stay non-Shipping. | Lead byte search found no callers; graph scan was inconclusive. Packaged setter proof is deferred until the first real caller and is part of the A7-B retirement gate. Selected-root cook manifest remains to be retained at the next package. |
| Arena map or binary-map scope | No production map/root change authorized by this queue. | Specific product scope and explicit approval. |
| Legacy startup retirement | A7 Option B decided: retire later after release gates close; keep legacy now as fallback and parity control. | Package/Shipping proof, target performance, content/cook closure, and recovery proof. |

## Current execution order

1. Claude captures current CDO values and source identity in the open Editor.
2. Author and read back the two typed definitions from that snapshot; generate and independently validate the canonical manifest; create and validate the G044 selection asset.
3. Claude runs the empty-selector control, selected startup, then selected H019 respawn/rebind PIE and retains raw logs/identities.
4. Resolve the trusted runtime-to-driver capture bridge, then run paired parity controls.
5. Export and verify the real cook graph and target-binary load; measure cold/warm cost on the agreed target hardware before any budget decision.

No route/default changed now. The recorded choices do not claim package, Shipping-behavior, or performance proof.
