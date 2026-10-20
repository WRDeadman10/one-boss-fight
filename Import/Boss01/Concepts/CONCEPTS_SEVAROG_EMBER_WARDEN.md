# The Ember Warden: Customization Proposals on Paragon Sevarog

Authority: `Documentation/AG/BRIEF_02.md` Task T2.
Base Mesh: `SK_Boss01_Body` (81,071 polys on `SK_CombatMannequin` skeleton, 180.5 cm native scale / 311 cm in engine).
Equipped Weapon: `SM_Boss01_Greatsword` (20,816 triangles, 184.6 cm length, grip pivot at $Z=0$).

---

## Variant 1: "The Ashen Sovereign" (Fallen Monarchy)
*A tragic ancient monarch bound to the scorched throne, whose crown has shattered into jagged cathedral spires.*

### Visual Changes Breakdown:
- **Crown Circlet & Spires (Mesh Work)**: A 6-spire jagged iron coronet fused directly into the rim of Sevarog's cowl ($Z \approx 1.62\text{ m}$ to $1.85\text{ m}$), breaking the smooth skull profile into a sharp crown silhouette.
- **Tattered Crimson Banner Cape (Mesh Work)**: Floor-length heavy crimson heraldic cloak pinned beneath the shoulder mantlets, draping to $Z=0.06\text{ m}$ with weathered antique gold border trim.
- **Sternum Ember Fissure (Mesh Work + Material Work)**: 3D recessed glowing fissure channel running vertically down the chestplate from throat to sternum ($Z \approx 1.15\text{ m}$ to $1.50\text{ m}$).
- **Emissive Seam Masks (Material Work)**: Molten orange ember glow pulsing through the armor cracks, cowl eye sockets, and fuller runic channels (driven dynamically by Phase 2 in Unreal).
- **PBR Armor Textures (Material Work)**: Weathered gunmetal iron plate with edge scratches, antique gold pauldron rivets, and scorched crimson cloth.

### Render Files:
- Front: `Variant1_AshenSovereign_Front.png`
- Side: `Variant1_AshenSovereign_Side.png`
- Back: `Variant1_AshenSovereign_Back.png`
- 25m Fog: `Variant1_AshenSovereign_25mFog.png`

---

## Variant 2: "The Scorched Inquisitor" (Flared Spire & Brazier)
*A fanatical flame inquisitor whose high needle spire and molten gauntlet channel the ancient ember pyre.*

### Visual Changes Breakdown:
- **Gothic Steeple Spire Finial (Mesh Work)**: High conical needle spire rising from the center brow of the hood ($Z \approx 1.65\text{ m}$ to $2.02\text{ m}$), dramatically increasing verticality.
- **Brazier Gauntlet Cuff (Mesh Work)**: Articulated cylindrical iron brazier cuff with glowing interior hearth fitted around the left forearm ($Z \approx 1.25\text{ m}$) specifically to telegraph the charging of the A5 Ember Javelin.
- **Liturgical Stole Ribbons (Mesh Work)**: Diagonal crimson sash draped across the breastplate from left clavicle to right hip with gold embroidery runes.
- **Runic Inscriptions (Material Work)**: Faded incandescent runes etched into the shoulder rim and vambraces.
- **Phase 2 Ignition (Material Work)**: Brazier cuff flares to blinding intensity when casting the javelin.

### Render Files:
- Front: `Variant2_ScorchedInquisitor_Front.png`
- Side: `Variant2_ScorchedInquisitor_Side.png`
- Back: `Variant2_ScorchedInquisitor_Back.png`
- 25m Fog: `Variant2_ScorchedInquisitor_25mFog.png`

---

## Variant 3: "The Pyre Bulwark" (Monumental Horns & Dual Mantle)
*An archaic colossal juggernaut reinforced with serrated horn crests and heavy split battle-mantles.*

### Visual Changes Breakdown:
- **Serrated Horn Extensions (Mesh Work)**: Heavy swept-back iron horn cowls with stepped razor spines extending Sevarog's shoulder horns outwards to $X = \pm 0.40\text{ m}, Z \approx 1.78\text{ m}$, creating an imposing wedge profile.
- **Dual Split War-Mantle Wings (Mesh Work)**: Two wide charred crimson war-mantles cascading down either side of the spine ($Z \approx 0.08\text{ m}$ to $1.42\text{ m}$), revealing the central spine ridge.
- **Ribcage Hearth Venting (Material Work)**: Deep furnace core glow visible through the intercostal ribcage seams.
- **Charred Hem Gradient (Material Work)**: Soot-stained blackening along the chainmail skirt hem.

### Render Files:
- Front: `Variant3_PyreBulwark_Front.png`
- Side: `Variant3_PyreBulwark_Side.png`
- Back: `Variant3_PyreBulwark_Back.png`
- 25m Fog: `Variant3_PyreBulwark_25mFog.png`
