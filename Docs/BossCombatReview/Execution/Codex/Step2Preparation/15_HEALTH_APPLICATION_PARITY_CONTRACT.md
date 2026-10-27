# Health application: structural hydration versus effective pack values

Codex,2026-10-27. Source-only refinement of PacketD0/09. No live change, new activation delay, test threshold, gameplay fix, UE run or integration release. This preserves the existing compatibility behavior while specifying independent future observations.

## Six checked source boundaries

1. `RPGEncounterBinding.cpp:333–340` registers components and sets bHydrated from registration success. `URPGCombatParticipant::IsReady` consults that context state. Neither path reads actual pack maximum/current health. Structural readiness is not evidence that asynchronous pack attributes have reached intended effective values.
2. `RPGBossEncounter.cpp:65–73` captures HomeTransform and calls Sleep only with GateRadius>0. `:79–108` applies desired health from Tick, not Configure/BeginPlay. It waits for readable positive maximum AND current. Default tick interval is0.1s; do not replace the condition with a fabricated elapsed-time promise. A zero/dead/unreadable current does not satisfy the application branch.
3. `:90–108` checks BossMaxHealth>1, whereas scaffold Stats accepts any finite MaxHealth>0. Thus a typed value in(0,1] can compile yet not execute this native override. Values<=1 are a legacy bypass domain, not a general positive health assignment. Explicit native-adapter capability/range handling remains a design gate; this document approves neither a clamp nor changed behavior.
4. `:96–106` sets bMaxHealthApplied if the existing maximum is already within0.5 of the target, without proportional current rewrite. Otherwise it calls WriteMaxAttribute, verifies maximum readback within0.5, sets applied=true, and attempts a proportional current write. It does not verify the final current write or its readback. Therefore the flag alone cannot prove desired current health, and0.5 is an existing implementation comparison, not a new general audit tolerance.
5. `:80–88` startup compatibility restoration requires already-applied, dormant, StartupTime<4, target-matching maximum, positive current and a deficit>0.5. It rewrites CURRENT only; it does not repair a maximum overwritten later. With GateRadius0 the component does not initially Sleep; the synthetic GateRadius0 fixture therefore omits the ordinary dormant restoration branch. Actual wake timing also matters. Do not treat that fixture as evidence of identical Boss01 startup health behavior.
6. `:297–382` reset can refuse a dying boss; otherwise it advances generation, resets phase/stagger and writes current Health from the currently readable pack MAXIMUM. It does not reapply BossMaxHealth or reset bMaxHealthApplied/StartupTime. Sleep resets DormantTime/HealthBaseline (`:225–230`), not startup enforcement lifetime. Reset-to-configured2000 cannot be inferred merely from generation advance or ResetCount.

`Pack/RPGBlueprintCall.h:222–275` helpers dispatch reflected current/max setters. Current setter locates named Value; maximum setter uses first nonreturn numeric parameter. A dispatch success is not an independent attribute readback. This audit does not prove a pack ABI failure; it names the witness needed if the adapter promises effective health.

## Unrun independent witness matrix

| Situation | Observe separately / preserve current behavior |
|---|---|
|Normal gated startup|Configured typed value, component property, readable pack max/current, actual application/write/readback, dormant/wake state, accumulated startup time and generation. Capture actual pack delayed initialization; do not fake missing reads as zero/default values.|
|Maximum already target|Full and partially depleted current cases; distinguish branch that sets applied flag from proportional-write branch. A flag/property check cannot close both.|
|Zero/unreadable/dead attributes|Explicit not-applied state and existing death/reset refusal behavior. Do not heal a dead participant to make hydration look successful.|
|Late current versus late maximum changes|Before/after startup enforcement boundary and before/after wake. Determine which current implementation branches run; do not silently extend the4s policy or add a retry loop during extraction.|
|GateRadius0 fixture|Record omission of initial dormancy and compare only the behavior actually exercised; retain ordinary gated boss witness as separate evidence.|
|Repeated encounter reset|Read actual max before and current after reset, with trace/generation/phase/posture ordering. Do not assert StartupTime restarts or configured maximum reapplies when code does neither.|
|Typed range boundary|MaxHealth in(0,1], >1 and invalid/nonfinite values: record compiler versus native application capability distinctly. Unsupported general data must not silently count as applied health.|

Binding may remain structurally ready while effective values are pending; naming/activation policy for future adapters must be explicit and reviewed. This is not permission to hold the existing boss longer, change first-attack timing, bypass failed pack reads or enable two-duel/network claims. A future full gate still requires exact binary and runtime evidence from the resumed operator.

## Raw source pins

- Encounter.cpp `dc149393f2fff1788ea22daf42db0b14f85ac36f58ad59c459b44ee94600c96d`
- Encounter.h `4f3ab203562ef2d3a2d18828feaf5f437a5a7eaff1054e9b6ce60e9150cae9d6`
- Pack/RPGBlueprintCall.h `08ca6403cb85eef36ed15c755a2163fb17f8bcfdb81043b640765d5145b8e19c`
- Binding.cpp `2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc`

Pins establish inspected bytes only. Existing failed attempts and bounded accepted runs remain unchanged; no newly reproduced health failure is claimed.
