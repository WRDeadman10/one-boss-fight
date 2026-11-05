# Unreal automation registration inventory audit (D81)

Date: 2026-11-03. Ran the source-only `Scripts/Tools/list_automation_tests.py --root .` and independently counted `IMPLEMENT_(SIMPLE_)?AUTOMATION_TEST` occurrences under `Source/OneBossFight/Tests`.

- The inventory reports 332 registrations and 332 unique C++ registration identifiers.
- The independent source text count also finds 332 macro occurrences.
- Full names and exact source line locations are indexed in [AUTOMATION_REGISTRATION_INDEX_D81.md](AUTOMATION_REGISTRATION_INDEX_D81.md).
- The count matches BUILD-184's historical 332/332 executed suite. The match does not prove that the currently checked-out binary has those registrations or that all are discovered/executed; D81 did not run Unreal.

The helper is a regex scan of one-line registration macros under the Tests source directory. It does not preprocess C++, inspect build target/test flags, discover runtime filters, or confirm linker inclusion. No suite/build/editor command ran.
