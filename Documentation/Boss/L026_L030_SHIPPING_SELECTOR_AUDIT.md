# Queue L Batch 6 — Shipping selector API and policy audit

## Findings and task status

| Task | Status | Finding |
|---|---|---|
| L026 | **LEAD-RUN DONE WITH LIMIT** | C++ exposes `SetSelectedDefinition` as `BlueprintCallable` without a Shipping guard. Lead's graph scan was inconclusive (zero exposed graphs); a read-only UTF-8/UTF-16 byte search found no references in 11,738 Content packages. Lead concludes there is no current Blueprint caller. |
| L027 | **DECIDED — Option A** | Owner approved the Blueprint setter as a supported Shipping selection route. |
| L028 | **DECIDED — no Source change** | J049 Option A requires no code change. The CVar and `-RPGBenchmark` selector remain non-Shipping. |
| L029 | **DEFERRED UNTIL A REAL CALLER** | No test-only caller asset is authorized now. Packaged setter proof is deferred until the first real Blueprint caller and is part of the A7-B retirement gate. |
| L030 | **DECIDED — A7 Option B, later** | Owner chose legacy retirement later, after gates close. Until then legacy remains fallback/parity control; no removal or default change now. |

## Exact source boundary

- `RPGEncounterSelectionSubsystem.cpp` wraps the `rpg.EncounterDefinition`
  console CVar and path-based resolution in `#if !UE_BUILD_SHIPPING`.
- `RPGEncounterSelectionSubsystem.h` declares `SetSelectedDefinition` and
  `ClearSelectedDefinition` as BlueprintCallable without a build guard.
- `HasSelectionRequest()` checks the stored `SelectedDefinition` before its
  nonshipping CVar branch, so a caller-set object can request selection in
  Shipping. This proves API exposure, not an actual asset callsite.
- Content callsite absence cannot be established from C++ search. Claude must
  inspect Blueprint references/callers and report exact asset/function paths.

## Owner choices recorded in J049

**A. Approve the Blueprint setter as a supported Shipping selection route.**
Requires the content caller inventory, authored dependency graph, authoritative
cook manifest, and packaged behavior proof before release claims.

**B. Exclude direct selection from Shipping.**
Requires a reviewed API guard/removal and a content migration/validation plan so
any existing Blueprint caller is found and handled. Then verify the Shipping
binary has no selector route and that empty selection preserves legacy startup.

Owner decisions recorded 2026-11-05: J049 Option A is approved; A7 Option B
means retire legacy later, only after gates close. No source policy, default,
map or Shipping behavior was changed.

## Exact Source effect of the two choices

| J049 option | Source change/effect | Current evidence |
|---|---|---|
| A — approve setter for Shipping | No source edit. Accept the existing BlueprintCallable declaration in `RPGEncounterSelectionSubsystem.h:30` and setter implementation in `RPGEncounterSelectionSubsystem.cpp:79-83`; `HasSelectionRequest` accepts that stored object in Shipping at `RPGEncounterSelectionSubsystem.cpp:95-98`. | API exposure is established. Lead's graph scan is inconclusive; UTF-8/UTF-16 byte search found no references in 11,738 Content packages, so Lead concludes there is no current caller. With no selection Shipping uses legacy. Setter proof is deferred until a real caller exists and is part of the A7-B retirement gate. H2 cook manifest remains open for the next package. |
| B — exclude direct selection from Shipping | Add a Shipping API guard/removal at `RPGEncounterSelectionSubsystem.h:30` and `RPGEncounterSelectionSubsystem.cpp:79-83`, and prevent the stored-object request branch at `RPGEncounterSelectionSubsystem.cpp:95-98`; preserve non-Shipping test access and review/migrate any callers. | No guard or caller migration has been implemented. This is only the concrete source boundary, not authorization to change it. |

The G1 benchmark argument is separate: parsing `-RPGBenchmark` and
`-H019EncounterDefinition=` and assigning the benchmark field are inside
`#if !UE_BUILD_SHIPPING` at `RPGEncounterSelectionSubsystem.cpp:58-67`; the
CVar fallback is also non-Shipping-only at `RPGEncounterSelectionSubsystem.cpp:127-129`.
The generic soft-path loader is shared, but the benchmark field has no Shipping
assignment. GATE4 runs a Development package, so this preparation does not
choose J049.
