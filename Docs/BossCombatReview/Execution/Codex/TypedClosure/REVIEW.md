# X-T10 typed closure delivery — 2026-10-26

Status: staged promotion patch, NOT applied, compiled, automated, or packaged by Codex. Live source remains unchanged. Claude owns promotion/build/editor verification. Condition 1 is NOT closed by apply-check alone.

Revision after delivery: raw Claude `Saved/rebuild_typed_abi.txt` shows Resolution success but full automation40/41 (CookCoverage fail). The original negative fixture's literal absent asset path was a Codex test defect: repository CookCoverage scans tests too. Claude already split the live fixture string; Codex corrected staged snippet/mirror/patch to the same intent. Current patch SHA866627fe... replaces historical ea576df...; original preimage pins unchanged. Current live source is already promoted, so do not reapply. No new apply-check claimed after concurrent live promotion. Full rerun evidence remains pending.

## Evidence and implementation

E-011 PR4 manifest 28/28 and PR5 manifest 17/17 independently hash-matched. The patch removes concatenated ExportText membership validation and introduces a fail-closed native reflection adapter. Fixed pack roots constrain weapon item, weapon actor, ability and style independently of author data. Exact full object identities and declared item ancestry are checked. Typed Item -> Equipable Actor Class and Item -> Combat Style edges must equal the declared objects. Style -> AbilitiesSet -> F_AbilitySet -> GUID-qualified Abilities array must contain the exact declared ability class.

PR5 does not expand nested F_AbilitySet metadata. The GUID field identity comes from complete PR4 style exports; runtime reflection checks array/struct/class kinds and nested MetaClass compatibility. This is a version-pinned adapter, not a general fuzzy property search. Renamed fields or changed schema fail closed. Root loads are retained in epoch leases; existing dependency/cook policy, coverage and legacy pinning remain unchanged. Live equip and damage capability are not inferred from static references.

## Patch verification

`PROMOTION_STEP1_TYPED_ABI.patch` passed `git apply --check` against the live preimages in `PREIMAGE_AND_PATCH_SHA256.json`. No application performed. Narrow diff: catalog +6/-9, existing Resolution automation +91/-0, new header 22 lines, helper 87 lines. Mechanical builder reads live files and writes only this Codex staging folder.

## Tests staged, not executed

Existing Resolution automation retains C-140 probe and adds installed Sword typed positive; broad declared UObject base; nonweapon Actor; arbitrary ability UClass; valid but ungranted ability; mismatched actor edge; unrelated style object; missing item; full identity mismatch; transient duplicate item with decoy text but wrong real style edge. Original pack objects are never mutated. A fourth nonlegacy build sharing Sword passes full resolution, while duplicate weapon style ownership and an absent/out-of-policy dependency fail. Optional absent/wrong-type icon degrades; held epochs are exercised across GC.

Limits: the missing dependency case cannot distinguish an existing uncooked asset from a nonexistent asset; no same-leaf alternate-package fixture; no genuinely distinct supported fourth weapon; no once-only presentation diagnostic assertion; GC is not a real two-GI/travel teardown. These are not claimed closed. P03 distinct-weapon and P05 cold packaged evidence remain pending. Automation name count stays unchanged (41 expected, not observed).

## Claude promotion acceptance

Recheck preimage hashes and apply-check before promotion; stop on drift rather than force context. Review new native helper and actual UE 5.5.4 API compatibility. Close editor before building; rebuild with tests. Run Catalog.Resolution, full OneBossFight automation and existing gate. Capture actual field failures and all three shipped positives; expand nested F_AbilitySet typed dump if reflection schema differs. Re-cook/re-stage fresh Development with these binaries and cold-launch data source. Preserve raw logs/hashes. No historical automation or package result substitutes for this patch's evidence. Shipping remains separate. No P1/Step2/Step3 activation is authorized here.
