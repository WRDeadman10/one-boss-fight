# BOSS-MOV-001: range-band partition and live proof

The ledger bands overlap. This maps a card to each band whose closed range intersects the card's authored `[MinRangeCm, MaxRangeCm]`; it does not assert that a card is well tuned throughout the whole band.

| Ledger band | Existing F5/F7 cards with an overlapping authored range | Assessment |
|---|---|---|
| Melee, 0–220 cm | `SwingSlow` 100–200; `SwingMedium` 90–180; `AntiGreed` 90–185; `HeavySlam` 90–180. F5 source ranges: [move_cards_f5_set.json:25-26](../Antigravity/MoveCards/move_cards_f5_set.json:25), [63-64](../Antigravity/MoveCards/move_cards_f5_set.json:63), [101-102](../Antigravity/MoveCards/move_cards_f5_set.json:101), [139-140](../Antigravity/MoveCards/move_cards_f5_set.json:139). | Populated; all four ranges lie inside this band. |
| Close, 150–350 cm | All four cards above overlap 150–200, 150–180, or 150–185 respectively. F7 baked ranges confirm the same values: [move_cards_f7_baked.json:20-21](../Claude/F7/move_cards_f7_baked.json:20), [308-309](../Claude/F7/move_cards_f7_baked.json:308), [492-493](../Claude/F7/move_cards_f7_baked.json:492), [637-638](../Claude/F7/move_cards_f7_baked.json:637). | Populated only at the near edge of the band; no current card reaches beyond 200 cm. |
| Medium, 200–400 cm | `SwingSlow` has `MaxRangeCm: 200` in F5 line 26 and F7 line 21. | Technically populated at the single inclusive boundary point 200 cm. There is no card covering any distance greater than 200 cm in this band. |
| Gap-Closer, 400–950 cm | None. The largest maximum among these cards is 200 cm (F5 lines 26, 64, 102, 140; F7 lines 21, 309, 493, 638). | Empty. |

## Animation reuse for the empty band

AG-12 names `Dodge_To_Idle_Montage` as a pack dodge montage and gives its notify duration and rate scale at [AG12_PACK_REUSE_INVENTORY.md:89](../Antigravity/AG12_PACK_REUSE_INVENTORY.md:89). It is the only named movement montage in that inventory that might be investigated as a distance-closing motion reference. The inventory classifies it as a dodge and supplies no evidence that it is a boss greatsword forward charge, so it is not yet a verified gap-closer backing montage. AG-12's four `Idle_Turn_Left/Right_90/180` montages are turn-in-place only ([line 28](../Antigravity/AG12_PACK_REUSE_INVENTORY.md:28)); they cannot fill a translational gap-closing role. The F5/F7 attack JSON points at animation Sequences, with `Montage: null` (e.g. [move_cards_f5_set.json:14-15](../Antigravity/MoveCards/move_cards_f5_set.json:14)); those are not evidence for an existing gap-closing montage. Before authoring this card, inspect the pack's boss attack-montage entries for forward root travel. The inventory does not identify a suitable named montage, so none is asserted here.

## Live PIE proof

For each observation, log the planar boss-to-target distance, the selected card ID (or `INDEX_NONE`), every candidate's min/max range and range-refusal reason, and whether movement/repositioning started or the boss failed closed. Capture distances just below, at, and just above each relevant authored boundary, especially 180, 185, 200, 220, and 400 cm. The expected selection evidence is:

- At 150–180 cm: all four current cards pass the range filter; other filters may still reject them.
- Above 180 through 185 cm: `SwingSlow` and `AntiGreed` pass; the two 180 cm cards are refused by range.
- Above 185 through 200 cm: only `SwingSlow` passes; above 200 cm and below 400 cm, all current cards are refused by range.
- At and above 400 cm: no current card passes; until a gap-closer is authored, the trace must show the explicitly intended fallback (reposition/approach) and no attack selection outside a card's range.

Run the test at matching distances with all non-range gates held eligible, and log at least one live encounter crossing from 400+ cm into the current attack ranges. A claimed gap-closer proof must additionally show its selected card inside 400–950 cm, movement closing the measured range, and a transition into its attack window without a no-candidate failure. Current cards' ranges do not prove that behavior.
