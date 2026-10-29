# A164 production input packet review

Verdict: RETURN FOR BOUNDED OFFLINE CORRECTION. Not accepted as a consistent fixture packet. Claude X259/DD11 remains unchanged; no engine or git release.

## Independent checks

Read all 24 JSON input records and the README. Recomputed original delivery hashes:

- JSON: `63c65be981bd1dd68afc2c0d224a9d3a50a46338aed23b57a0a5918fa3046de5`, 42588 bytes.
- README: `f9f8613ed691c3cef2976d387857720c7acc8541e2c1e42fd17e36000ad7a63c`, 11797 bytes.
- Two-file receipt: `fe916218a9be3b6df5d29225808a6a11abb48f132838b30b6ee52c7b6123e391`, 175 bytes.

Of 22 package-bearing input records, 21 existing files match their JSON sizes and SHA256; the two immunity records share one package. Two additional records are identity tokens. The remaining package record is the wrong sword path. These are offline file observations only.

The five JSON source dependencies matched disk during review. Binding already contains in-progress DD11 changes, so its current hash is a moving implementation input, not a frozen accepted DD10 pin. No allegation of unauthorized drift: X259 authorizes those source edits. The README and JSON nevertheless disagree internally, independently of subsequent edits.

## Required corrections within the existing packet

1. Synchronize the README and JSON from verified bytes. Ten README asset hashes disagree with JSON and disk: StaggerHitStunAbilityClass, PlayerActorBlueprint, BossActorBlueprint, SharedSkeleton, PlayerMesh, BossMeshBody, BossFollowerCrown, BossFollowerMantle, BossFollowerBrazierGauntlet, ArenaLevel. All five README source hashes also disagree with JSON. Do not preserve an old eight-character prefix and invent the remainder. Examples: arena actual `095361fe5768accd59a0fe84a9f91ba3bfc8220dadea6d8c30f1ea3f1f3a77b5`; player BP actual `9662aaa364c56243180560b9121da7eadd8bfe43bfcd7f54bccd1752a07abc81`. Preserve original delivery bytes before replacement and regenerate receipts.
2. Correct BossFollowerGreatsword from `/Boss01/Body/` to the actual constructor default `/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword.SM_Boss01_Greatsword` in RPGBossLook.cpp:23. Its actual file exists with SHA256 `147629fb4c8df8b5d955f2c19622301bcd04d94b2ada27f7e07b7da79b0c8559`. JSON currently accurately marks the wrong path absent, while README claims a file hash/presence. The visual sword is a static socket attachment, not another skeletal leader-pose follower. Native source creates body plus three skeletal pieces; keep that distinction.
3. Repair evidence provenance. All three cited report paths under Execution/Antigravity (Archive/REPORT_08, Archive/REPORT_12, REPORT_13) do not exist. `Documentation/AG/REPORT_13.md` exists; resolve actual archived reports or mark unavailable. Include exact existing paths, hashes and sections/raw evidence for historical numerical or pass claims; without these label them uncorroborated rather than verified. Pin relevant RPGBossLook.cpp, documentation/scripts and DefaultGame.ini inputs where used, or explicitly mark the association unverified. Config observed SHA256 `9827ff8e632354cb7d3013955f1c1891ca16eac037abf8cd64369e5aa8886be3`. Several Look source sites/members are wrong: constructor uses Body, Pieces, Sword at lines17-23, not BodyPath/CrownPath/etc at40-44. Check claimed sites against the pinned source. Binding is evolving under DD11: name the observed snapshot and its provenance; do not imply it is a frozen accepted witness or overwrite implementation to match the packet.
4. Distinguish binding identity from candidate asset. HitStunAbilityClassName is the FName `GA_GS_Boss_HitStun_C`, whereas JSON soft_path currently contains a full candidate generated-class path. Preserve both with explicit meanings; never feed the full path as that FName. README actor/animation entries should retain complete object/generated-class paths for actual fixture use. Existing type/skeleton/cook caveats remain mandatory. Claimed 90cm root motion and impact timings need traceable historical evidence, not a new requirement to execute exactly those numbers.

## Limits and disposition

Existing-file hashes do not prove loaded types, skeleton compatibility, animation timing, active abilities/tags, cooked availability or a positive production batch. No runtime test was performed by this review. No widening to inventories/helpers/engine work; correct only this packet and report one revised delivery. Keep original failures and receipts. DD10 staging/commit remains held pending a separately reviewed exact batch and stable accepted shared Binding bytes. Claude continues DD11 source-only order without interruption.
