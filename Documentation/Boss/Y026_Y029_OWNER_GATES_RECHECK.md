# Queue Y Y026–Y029 — owner-gated tuning and art recheck

Date: 2026-11-06. Read-only decision/source reconciliation. No owner decision was inferred and no gameplay, config, or art value was changed.

## Y026 — KI-190 owner response

Mailbox review through A-563 and `KNOWN_ISSUES.md` show no owner answer resolving whether Freeze's “35 stamina per swing” applies to Strength Light. KI-190 remains OPEN.

## Y027 — Strength Light cost proposal and evidence

`Source/OneBossFight/Player/RPGWeaponAttackTable.cpp:41-62` describes the intended 35 stamina as applying per heavy swing and authors the Strength `Light` row with `StaminaCost=-1`. `Source/OneBossFight/Player/RPGSwingTracker.cpp:251-262` uses the row cost only when nonnegative; the pack's base 15 is already paid, so a -1 row applies no extra cost. `Scripts/Editor/pie_stamina_cost.py:151-157` checks 15 for no-row-cost starter swings; lines 162-172 use explicit test overrides for 35 on Strong/JumpHeavy. The script and receipt do not show a real Strength Light loadout consuming 35. The W-C039 decision sheet offers A (retain pack 15), B (set 35 if owner confirms), or C (new explicit build-specific row with owner-selected value); none is selected. Preserve the current table and KI-190 until the owner clarifies scope and a real Strength loadout is observed.

## Y028–Y029 — Tier 2 art choice and safe defaults

The mailbox contains no A/B/C choice or deferral after the latest owner/Lead references. `TIER2_ART_OWNER_BRIEF.md` lists Option A (full approval, recommended by the author), Option B (parry visuals only), and Option C (defer Tier 2); recommendation text is not owner authorization. The brief specifies opt-in Development wiring with empty defaults preserving D5 parity. With no chosen option, there is no selected art set to reconcile to production or Development defaults. Keep the current baseline and existing default behavior; do not create, import, wire, or tune Tier 2 art.

## Y030 — batch status

KI-190 remains OPEN; Tier 2 art choice remains OWNER DECISION OPEN; A7/J049 decisions are unchanged. No code, config, or Content changes. Continue Queue Y Y031–Y035, with P35 candidate removal still owner-gated and no cleanup authorized by this batch.
