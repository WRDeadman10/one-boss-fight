# 05 — Timelines, Delayed Strikes, Telegraphs, Rhythm, Neutral Pauses

![Attack timeline](../diagrams/05_attack_timing.png)

## Segment each attack explicitly

`Anticipation/Wind-up → Optional Hold → Commit/Tracking Lock → Active Hit(s) → Follow-Through → Recovery → Neutral`

All values in the provided example are **designer-authored**, not sourced from Elden Ring. The animation can be one montage with annotated notifies, or multiple labeled sections. Prefer the actual animation play position as timing authority instead of timers that drift from playback rate.

### Telegraph phases

- **Early pose:** communicates attack family (overhead vs thrust vs radial blast).
- **Direction clue:** shoulders, weapon path, stance, step direction communicate geometry.
- **Release cue:** acceleration, sound accent or VFX spike communicates imminent damage.
- **Active hit:** weapon/ground/projectile volume is damaging — only when authorized.
- **Aftermath:** follow-through communicates safe or conditional recovery.

### Delayed attacks without cheating

A fixed long wind-up is different from a dynamically variable hold. Dynamic holds are fair only when (1) their min/max durations are bounded, (2) release has a reliable observable cue, (3) release timing is not chosen after reading the player's dodge input in an impossible way, and (4) their duration does not make player action futile. Recommended first prototype: **fixed** authored hold variants selected before commitment.

Example: attack has `HoldShort 0.35s`, `HoldLong 0.75s`; choice made at wind-up start and visibly communicated by pose/audio. Never directly truncate the hold to hit an already-rolled player unless move design deliberately includes an intelligible release trigger.

## Timing budget at 60 FPS

Frame duration is ~16.67 ms. An attack that has an 80 ms active window spans roughly 5 frames at 60 FPS; it may be missed if collision detection relies on a single overlap sample per frame. Use swept traces and/or sub-sampled socket path; test at 30 FPS. Animation notifies can cross over multiple frames with different blend behavior; log actual fired events.

### Illustrative durations

| Move | Wind-up | Hold | Active | Recovery | Feel |
|---|---:|---:|---:|---:|---|
| Quick poke | 0.25s | 0 | 0.13s | 0.38s | Pressure, low reward |
| Heavy overhead | 0.68s | 0.38s | 0.18s | 0.95s | Read, dodge, punish |
| Delayed hook | 0.42s | 0.65s | 0.15s | 0.62s | Roll timing test |
| Wide sweep | 0.55s | 0 | 0.25s | 0.60s | Position test |
| Radial bell shock | 1.05s | 0 | 0.40s ring traversal | 1.00s | Area recognition |

The true time to hit is wind-up + hold + time to first contact within active window; the exact contact time depends on geometry and victim position.

## Neutral and pacing

Neutral should not mean brain-dead idling. The boss can circle, feint position, walk, face the player, defend, or briefly reset. Use aggression tokens: a long combo spends budget, recovery and positioning replenish it. Caps prevent continuous pressure. In phase 2, budget and replenish rates can change without deleting punish windows.

### Proposed pressure budget

`PressureBudget max=100`: quick poke costs 12; sweep 22; heavy 35; advancing lunge 28; shockwave 45. Replenish 18/s in neutral, 5/s while recovering, 0 during active. Attack eligible only if enough budget; always reserve enough capacity for a safe emergency disengage action. Numbers are examples.

### Rhythm motifs

- **Short-short-long** combo challenges fast double-roll habits.
- **Long-fast** teaches not to dodge on first movement alone.
- **Heavy recover** invites a charged attack.
- **Quiet positioning** makes the next move legible and avoids animation noise.
- **Fast pressure followed by obvious reset** rewards mastery and prevents exhaustion.

## Animation damage timing

Weapon contact time is not necessarily the montage notify start. Analyze the actual bone path and place active spans at the physical overlap. For a large weapon, sweep may last ~0.3s with the player's contact instant varying with side and distance. Damage should be resolved against traced intersection time, not a global moment of animation.

## Slow motion, hitstop, and time dilation

If hitstop pauses animation, pause trace sampling safely and avoid repeated overlap damage during the freeze. Time dilation can scale montage and timer systems differently if implemented inconsistently. QA must test pause/resume, play rate 0.75x/1.25x, and low FPS. Keep cooldown time base explicit: game time vs unscaled real time.
