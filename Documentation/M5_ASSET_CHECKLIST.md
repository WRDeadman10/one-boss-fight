# M5 asset checklist
> Superseded by `ENVIRONMENT_ASSET_REQUEST.md`.

M5 work that needs files only you can download. Free assets first; check the license on each Fab listing at download
time and record it in `ASSET_LICENSES.md`. Nothing here is a purchase decision for me to make.

## Done in M5 (no new assets needed)

- Three weapons as data only (Sword, Quick Blade, Greatblade) with weapon switching (R / D-pad up).
- Hit feedback system: pain, death, block and dodge sounds, impact effects, hit-stop, victory slow motion.
- Voice sounds and Cascade effects wired from the Greystone and Sevarog packs.

## Needed from you

| Need | Why | What to search for on Fab (any listing you prefer) | Notes |
|---|---|---|---|
| Arena kit | Replace the greybox with a real arena | "modular ruins", "stone arena", "dungeon modular" | UE 5.5 compatible, Nanite or low-poly (120 FPS target), Standard License. Bring me 1 or 2 candidates and I will check pieces fit the 6000 cm round arena |
| Weapon impact and swing sounds | The packs have voice only (KI-017) | "sword impact sounds", "melee combat sound effects" | WAV, royalty free |
| Footsteps | None exist | "footsteps stone", "armor footsteps" | |
| Boss telegraph and big-hit sounds | Readable attacks | "boss roar", "heavy impact", "thunder" | |
| Music | Fight and victory themes | "dark fantasy boss music" | Check loop points and license |
| Dodge roll animation | None in any pack (KI-007) | "roll animation set" for the Greystone skeleton or UE5 mannequin | A mannequin roll needs retargeting to Greystone, which I can set up |
| Niagara lightning | Replace the Cascade placeholder (KI-018) | "Niagara lightning", "lightning strike" | Niagara, not Cascade |

## When you have them

Put them in `Content/` (or tell me where Fab put them), tell me the listing URLs, and I will:
register the licenses, wire sounds and effects into the existing data assets (no code changes), place the arena kit,
and re-run the benchmark.
