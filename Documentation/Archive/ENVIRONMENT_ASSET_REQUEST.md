# Environment and content asset request

Everything below is what the finished game still needs from outside the project. It replaces the older
`M5_ASSET_CHECKLIST.md`. Free first. Check the license on every Fab listing at download time (Standard License
or better, no AI-training restriction on the assets we ship from), send me the listing URLs, and I record them in
`ASSET_LICENSES.md` and wire them in. Nothing here is a purchase I would make for you.

## Status after M7 (2026-10-18): what is still missing

Done with the packs you downloaded: arena kit (Blender meshes plus Deadly Ruins stone), sword swing and impact sounds,
shield block and parry sounds, roll animation, Niagara shockwave, lightning and sparks, Cinzel font.

Still needed (everything else below is covered or optional):

| What | Why it matters | Notes |
|---|---|---|
| Player footsteps on stone (walk and run, 4 variants each) and armor foley | The player moves in silence | Hook is not built yet: needs an anim notify or a footstep component, then data assets |
| Boss footsteps (2 to 3 heavy variants), ground slam, thunder crack for the lightning, roar, boss death | The boss attacks have voice only | The attack data assets take sounds already |
| Arena ambience loop and boss music (phase 1 and 2 or one track that builds), victory and death stings | No music or ambience at all | Needs a small music component (not built yet) |
| Menu sounds (move, select, back) | Pause menu is silent | Optional |
| Fire for the braziers (a Niagara fire and a point light) | Braziers are unlit props | The arena already places them between the pillars |
| A hit-spark or blood Niagara system that works in UE 5.5 | The Blood VFX pack imported for weapon impacts shows nothing (KI-024) | Weapons still use the Paragon Cascade impact |
| Shield guard hold loop, boss roar and boss lightning-cast animations | Placeholders reuse other animations | Optional |

## The arena I have to dress

Round arena, 6000 cm across (radius 3000), flat floor at Z = 0, 12 pillars (radius 120, height 900) on a ring at 90 % of
the radius, a 300 cm ring wall (48 segments, 80 cm thick). Player starts at the west edge, the boss at the center, the
trigger line is 700 cm inside the west edge. The boss is 3.1 m tall and sweeps about 4 m; nothing may block its moves.
The greybox pieces keep their collision, so any mesh I swap in keeps the same footprint.

## 1. Environment art (must have)

| What | Quantity and spec | Notes |
|---|---|---|
| Stone floor | Tileable PBR material set or floor tiles that cover 60 m diameter, plus 2 to 3 damage and rubble variants | Material instance friendly; no world-aligned tricks that cost a lot |
| Wall pieces | 4 to 6 straight and curved wall segments, about 300 cm tall, a broken and an intact variant | Low poly or Nanite; collision included |
| Pillars or columns | 3 to 4 variants around 900 cm tall (intact, cracked, broken) | Must be a cylinder-like footprint of about 240 cm diameter |
| Entrance | One arch, gate or fog-gate style threshold, roughly 8 m wide | Marks where the fight starts |
| Props | 8 to 12 small and medium props: braziers or torches, statues, fallen columns, rubble piles, banners, bones | Braziers need a light source slot |
| Ground detail | Rubble or crack decals, blood or scorch decals | Decals are cheap |
| Sky | Optional sky dome or cloud material; the engine sky and fog already work | Only if it matches a dark fantasy mood |

Budget rule: all meshes together should stay under about 150 000 visible triangles in the arena, with few unique
materials (the characters already use many).

Search terms on Fab: "modular ruins", "stone arena", "dungeon modular kit", "fantasy ruins environment", "temple ruins".
Bring me one or two kits; I will check them against the footprint above before you download more.

## 2. Audio (must have; the packs have voice only)

| What | Quantity | Used for |
|---|---|---|
| Sword swing whoosh | 3 to 4 variants | Weapon swing sounds |
| Melee hit impacts | 4 to 6 variants (flesh/armor, heavy) | Weapon impact |
| Shield block and parry | 3 to 4 variants, one sharp "ring" for parry | Block and parry |
| Footsteps on stone | walk and run sets, 4 variants each; armor foley | Player movement |
| Boss footsteps | 2 to 3 heavy variants | Sevarog |
| Boss scythe swing, ground slam, shockwave | 1 to 3 each | Boss attacks |
| Thunder and lightning | 2 to 3 | Phase 2 lightning |
| Roar | 1 to 2 | Phase transition |
| Boss death | 1 | Victory |
| UI | menu move, select, back | Pause menu |
| Music | ambient arena loop, boss theme (phase 1 and phase 2 or one that builds), victory sting, death sting | Encounter flow |

Search terms: "sword combat sound effects", "melee impact sounds", "medieval footsteps", "dark fantasy boss music",
"fantasy ambience". WAV or OGG, loopable where it says loop.

## 3. VFX (must have for lightning; the rest improves it)

All as **Niagara** (the pack effects are Cascade, which is deprecated).

| What | Notes |
|---|---|
| Lightning strike or ground bolt | Boss phase 2 attack: a telegraph on the floor, then the bolt. Cheap fallback required |
| Shockwave ring | The boss Shockwave attack, 5 m radius |
| Hit sparks and blood or dust impact | One for armor, one for flesh |
| Dodge dust and footstep dust | Small |
| Ambient embers or dust motes | Low spawn rate |
| Boss entrance and death effect | Optional |

## 4. Animation (strongly recommended)

| What | Why |
|---|---|
| Player roll or dodge, forward and backward (and left and right if possible) | None of the four packs has one (KI-007). Needs to fit the Greystone skeleton, or the UE5 mannequin so I can retarget |
| Shield guard hold loop (Greystone) | Today the guard plays a one-shot raise and then holds the pose |
| Boss roar for the phase change and a leap or lunge | Today the roar reuses `Ultimate_Targeting` |
| Boss lightning cast with a raised hand or weapon | Today it reuses `Cast` |

Search terms: "roll animation set", "dodge roll", "souls like animation pack". Check the skeleton and retarget notes
in the listing.

## 5. Optional polish

- A display font for the HUD and menu (a serif or blackletter style, OFL or free).
- UI icons (weapon icons for the three weapons).
- A second boss skin from the Sevarog pack (the pack already contains Chronos and Bloodred skins).

## What I do once I have the files

1. Register licenses and sizes in `ASSET_LICENSES.md`.
2. Replace the greybox meshes with the kit (same footprint and collision), set up materials and baked lighting where
   it helps, add fog.
3. Hook sounds and effects into the existing data assets (weapons, feedback, boss attacks); no code changes needed.
4. Retarget or import the roll, guard and roar animations and wire them into the dodge, guard and phase montages.
5. Run the full automation suite, the PIE checks and the fight benchmark again.
