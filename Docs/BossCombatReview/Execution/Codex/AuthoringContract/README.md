# Codex native authoring contract and independent probes

Implemented while Claude and AG work on their packages. New Codex-owned offline code only; no live module/script/asset edits and no Unreal import or engine operation.

`native_profile_contract.py` extracts the simple reflected property declarations of the actual RPGEncounterBinding.h records, emitting exact native names/types/initializer source and source SHA256. The CLI can validate JSON using native URPGBossDefinition field names, rejects unknown nested fields, wrong numeric/bool/container shapes and absent explicit fields when requested through its Python API. It never invents Python reflection names, default values or manifest records. It is a deliberately narrow declaration reader, not a general C++ parser or native semantic/domain validator. Zero-valued stats can be structurally valid but fail native compilation/assignment. An empty Fields array is still a draft, never production Ready.

Run from project root:

    python -B Docs/BossCombatReview/Execution/Codex/AuthoringContract/native_profile_contract.py
    python -B -m unittest discover -s Docs/BossCombatReview/Execution/Codex/AuthoringContract -p test_native_profile_contract.py -v
    python -B Docs/BossCombatReview/Execution/Codex/AuthoringContract/probe_a178.py

Latest evidence: eight unit tests pass, exit0, raw native_contract_unit_tests.txt SHA256 b4454bb30b3d68531ece1ac446095c4d9c950f1b57a2b1261ef1be8ae988bd43. Declaration JSON native_profile_schema.json SHA256 de8be3a4ef46dafea493f7968b8dcd21b4389a76d573032f029885ae2e298518. Independent probe raw a178_probe_raw.txt SHA2561540eb12e6aea6c5168f48de326af505add9879ac6b861f21728c6a5430ed5c1, exit0 means probe finished, NOT toolkit acceptance. Machine-readable results a178_probe_results.json pin actual inspected AG inputs.

The probe executes the pure shared core and selected function ASTs only, without the scripts' import/CLI side effects. A tiny recording fake exercises actual draft-writer control flow/setter calls; it cannot certify Unreal API/reflection, native semantics or saved assets. Its success-with-omitted-fields finding is Python logic evidence, not an engine reproduction. Independent quote oracle is transcribed from local UE5.5 TrimCharInline; exact Unicode casing/whitespace or FName numbering is not proven by ASCII examples.

Initial own offline failure is preserved in attempt1_failure.txt and native_profile_contract_attempt1.py.txt: extractor included a plain transport struct without reflected fields. Exact correction skips non-property-bearing records; this changed neither the project header nor AG source. These Python results do not add to the119 Unreal automation suite or close an all83 row.
