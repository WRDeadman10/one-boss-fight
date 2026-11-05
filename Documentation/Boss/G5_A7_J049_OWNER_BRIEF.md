# A7 and J049 — owner decision brief

**Owner decisions recorded 2026-11-05.** J049 Option A approves the existing
Blueprint setter route for Shipping with no Source change. A7 Option B retires
legacy startup later, after release gates close. Until then legacy stays as
fallback and parity control; no legacy removal or default change now.

## J049 — Shipping selector policy

| Option | What it removes or accepts | Proof currently available | Proof still needed |
|---|---|---|---|
| A — approve the Blueprint setter as a Shipping route (**decided**) | Accepts the existing setter as supported Shipping selection; no Source change. | Source confirms the BlueprintCallable API. Lead's graph scan was inconclusive; its UTF-8/UTF-16 byte search found no references in 11,738 Content packages, so Lead concludes the route is currently unused. With no selection, Shipping starts legacy. | Packaged setter proof is deferred until a real caller exists and is part of the A7-B retirement gate. The selected-root cook manifest remains open for the next package. |
| B — exclude direct selection from Shipping (not selected) | Would remove the Shipping setter route via a reviewed Source/API guard and handle callers. | Not selected. | Not applicable to the recorded decision. |

## A7 — legacy startup retirement

| Option | What it removes or retains | Proof currently available | Proof still needed |
|---|---|---|---|
| A — retain legacy startup (temporary current state) | Retains the fallback and parity control while selected-route gates are closed. | P15 records accepted post-D5 parity and current stochastic warnings; G2 v2 passed 13/13 in Lead PIE; G4 found no Source save-state migration path. | Close the remaining release gates below. |
| B — retire legacy startup later (**decided**) | Removes legacy fallback/control only after the remaining gates close. | Owner disposition recorded; P15 has accepted parity evidence and G2 v2 recovery pass. | Selected-route package/Shipping proof, target RTX 2060 Super performance, content/cook closure, and owner-session visual check of refusal message. |

## Gate status

- **Package/Shipping:** J049 Option A approved but currently unused; graph scan
  was inconclusive and Lead's byte search found no current caller. No test-only
  asset will be created. Setter proof is deferred until a real caller exists
  and remains an A7-B gate. H2 found all roots under the configured
  `DirectoriesToAlwaysCook` root; authoritative packaged cook manifest remains
  open for the next package.
- **Performance:** G1 expected sheet defines matched legacy/selected Development
  captures and thresholds; it is a run plan, not a result. GPU capture may need
  the owner's physical console session instead of RDP.
- **Compatibility:** G4 Source audit found no persisted selection/save state;
  content references and cook closure remain open.
- **Recovery:** G2 v2 passed 13/13 in Lead PIE: missing and invalid definitions
  fail closed, no legacy bundle leaks, and explicit clear restores fresh
  LegacyNoSelection. Refusal screenshots were black in the agent session;
  owner-session visual confirmation remains open. Packaged recovery proof also
  remains open.

Evidence inputs: `P15_A7_PARITY_SUMMARY_DRAFT.md`,
`G1_A7_BENCHMARK_EXPECTED.md`, `L026_L030_SHIPPING_SELECTOR_AUDIT.md`, and
`G4_SAVE_CONTENT_COMPATIBILITY_AUDIT.md`. This brief requests no production
change; package, Shipping, and performance proof remain open.
