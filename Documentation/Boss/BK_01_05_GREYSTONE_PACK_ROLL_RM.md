# BK-01–05 — Greystone pack roll root-motion retarget

## Source-derived inventory

The current Greystone player readback and `C1259_GREYSTONE_SOURCE_INVENTORY.md` identify exactly two pack roll montage/sequence pairs used by `URPGDodgeTiming`:

| Route | Mannequin source sequence | Current Greystone sequence | Current Greystone montage | Consumer |
|---|---|---|---|---|
| Quick roll | `/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll` | `/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Grey` | `/Game/OneBossFight/GreystonePack/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage_Grey` | `URPGDodgeTiming.QuickMontage`, `GA_Player_Dodge.DodgeMontage` quick entry |
| Full/recovery | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Grey` | `/Game/OneBossFight/GreystonePack/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage_Grey` | `URPGDodgeTiming.FullMontage`, `GA_Player_Dodge.DodgeMontage` full entry |

The current child readback names the two `_Grey` montages. The exported `GA_Player_Dodge` CDO snapshot only exposes the full/recovery map entry; the quick route is confirmed by the live child readback and `URPGDodgeTiming` substitution path. C1259 separately inventories weapon ability montage arrays for attacks, guard, flask, hit, death, equip and sheath; those are not consumers of these two roll sequences and are excluded from this roll-only selection. No broader weapon array is retargeted.

## Tool and safety behavior

`Scripts/Editor/retarget_greystone_pack_rolls_rm.py` is read-only by default. `--write` is required for changes. It:

- accepts only the two inventory rows above;
- refuses if any output asset path already exists;
- uses a duplicated target IK rig and a new retargeter with the `Root -> Root` FK mode `GLOBALLY_SCALED`;
- writes new `_RM` sequences and montage wrappers under `/Game/OneBossFight/Player/Greystone/RootMotion/`;
- creates montage copies through `URPGMontageWrapperLibrary`, preserving montage structure/notifies and replacing the copied segment references;
- proves each source/output root XY displacement and ratio, requires root motion enabled and a nonzero output displacement, and writes a JSON manifest in `Saved/`;
- never edits the existing `_Grey` sequences/montages, pack assets, child properties, or deletes assets. If a write fails partway, it reports partial outputs for inspection and does not automatically delete them.

## Verification and remaining gate

Offline contract: `python Scripts/Tools/test_bk1_greystone_roll_rm_contract.py` — **5/5 passed**. Python compilation passed for the new Editor tool and contract.

No Unreal Editor execution, asset creation, save, build, PIE, or root-motion measurement was performed in this batch because Claude owns the engine for X26. Therefore BK-01 inventory and BK-05 offline contract are complete; BK-02–04 tool source is authored but awaiting Lead's editor window and asset readback. The existing `_Grey` montage routes remain untouched, and the player default remains the mannequin pending the separate gate/owner switch.
