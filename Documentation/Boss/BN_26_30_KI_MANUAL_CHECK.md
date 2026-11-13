# BN-26..30: manual check of the heuristic-O KIs (lane BN, batch 6 of 10, per X-2213)

C (implementer), 2026-11-12.

**Not done:** no code, asset, engine, build, PIE or test work. No KNOWN_ISSUES status changes and no commits.

| Task | KI | Row | Evidence checked | Manual class | Offline follow-up? |
|---|---|---|---|---|---|
| BN-26 | KI-065 | `KNOWN_ISSUES.md:132`: the A6 wave has no visual and no player hit reaction (health is written directly); the leap landing is not checked against the arena bounds | The fixes are a VFX request (art), a hit-reaction call (code; behaviour needs PIE) and a landing check (code plus PIE) | **E** (code+PIE) + D (VFX/art is parked) | No: these are code changes that need runtime proof, outside this lane |
| BN-27 | KI-067 | `:134`: the A4 sweep does damage only; the behaviour tree never picks it; the jump-clear window of 0.05-0.60 s may be too generous; the clip poses are under review | The action is weights with G2-11 and tuning after a hand test; `DECISIONS.md:491` explicitly says the A4 selection weight is not built | **O** (selection-weight implementation can be done offline) + E (hand-test/tuning) + D (pose review) | **Yes:** implement the G2-11 A4 selection weight offline; hand-test/tuning and pose review remain gated. No implementation in this read-only lane |
| BN-28 | KI-068 | `:135`: the A5 javelin is a placeholder (no impact effect or sound); it leaves from `hand_l` (no `JavelinSpawn` socket); there is no flinch; any potion montage counts as a heal | Needs a VFX request, a socket from the final body (asset) and a hit-reaction call | **E** (asset/code+PIE) + D (art) | No |
| BN-29 | KI-070 | `:137`: open Report 09 art defects (A3a/A3b length, greatsword sockets and polygons, javelin slot names, crown, grey `M_Boss01_*` slots). The action is "Brief 10" | Art pipeline; art is parked by the owner | **D** (art is parked) + E (import) | No |
| BN-30 | KI-074 | `:141`: 4 s hit-stun immunity against a 3.9 s stance break; with a riposte, by code arithmetic the break can last about 5.5 s. "Code reading, not measured, not seen" | Needs a PIE timing measurement; the fix is a runtime effect re-apply | **E** (PIE timing) | No |

**Batch 6 result:** 1 true O (KI-067). Running total: 2 O (KI-026, KI-067) out of 29.

**Limits:** row reads only. The KI-074 arithmetic was not re-derived from the current source.
