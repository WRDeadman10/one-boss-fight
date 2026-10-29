# DD19 implementation delivery for Claude's independent review

Owner directly confirmed the role swap in this chat on2026-10-29: Claude leads; Codex implements. I took over C251/1, preserved all five received files byte-for-byte in Received_C251, and reviewed the typed record/compiler copy, validator/assignment and test source. No build, UHT, automation, engine, asset or git operation was performed.

Concrete correction: the received path predicate accepted e.g. an empty/repeated package segment or an extra dot in the asset name despite declaring malformed dependencies rejected. After the existing explicit path-shape/subobject checks, it now calls FPackageName::IsValidTextForLongPackageName and FName::IsValidXName(...INVALID_OBJECTNAME_CHARACTERS...). Both APIs and overloads were checked against installed UE5.5 source. These are text-only checks: they do not require the synthetic mount to be registered, query asset existence, load a class or certify effect/sound kind. IsValidObjectPath was deliberately not used because it also validates the mount.

Added five malformed reference cases, each exercised for both effect and sound through the existing Validation test's validator/callback/no-write checks: empty mount, repeated separator, extra object-name dot, invalid object-name character, invalid package character. Existing valid SyntheticMount references remain the positive controls. Source comments now accurately state the lexical boundary. No field domain/default/compiler-copy/plan semantics changed.

Only adapter.h/.cpp and the new Bleed test file differ from C251. Binding.h/.cpp equal received C251 bytes. The full194 manifest differs from accepted DD18 only by the exact five-file package: three additions, two Binding changes, other189 unchanged. CRLF restored for the three edited files. Received17 evidence receipts independently verified; source manifests, five Review copies/live pins, exact five_file.diff and narrow revision_from_C251.diff are under this folder.

Pins:
- adapter.h e3a55ee39c1f980edda57b7397d93ebb0861fc0f75d5a0ea748c48089fe3c1d3
- adapter.cpp 3799e43a190d93b8bf0347e9f568eb7204e7b00150ea3515b62612fa26527afe
- tests 99d5b68dcbe4358e78181e738a55242d09888f353336483bb4dfa3f269a309a4
- Binding.h 58c4e5758160abad1770aa6c04519a33648196d9d4676b4732d03adcbb948bbb
- Binding.cpp b4dc5c2654807131f18509949fba033661d2b52e8e197a5c90759f9a37520089

Review requested: exact final source/diff and194 manifest before any UHT/build release. Six test names are SOURCE expectations only, not a passing result; no compilation claim. ComponentBegunPlay guard remains source-only because Bleed BeginPlay loads assets. Registered-component and plain begun-owner fixtures exist in the inherited tests; their isolated execution must be covered by your exact verification release, not interpreted as gameplay activation.

No unrelated source, scripts, assets or runtime state changed; no insertion into the five-component preflight/preparation/registry. No Ready, legacy suppression, startup/target/reset wiring, proc, duel, networking or packaged proof. All earlier failures/warnings/provenance limits remain. No secrets. No commit/push.

The file-only prepare_delivery.py exit0 verifies integrity/delta/line endings; it is not an Unreal test. Raw script output is delivery_integrity_output.txt. Please accept or return the exact delta and issue the build/focused/full release when appropriate.
