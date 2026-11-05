# Queue N Batch 2 — G044 tool static review

## Task disposition

| Task | Status | Evidence / boundary |
|---|---|---|
| N006 | **DONE — source contract** | Exporter labels the artifact as CDO-only, writes boss/player source inventory, uses UTC timestamped names and exclusive-create output. No Editor invocation. |
| N007 | **DONE — refusal-path hardening** | Static review found malformed `properties`, `field_sources`, `$struct.fields`, and enum type/value shapes could escape as raw Python errors in `load_specs`/`materialize`. Added explicit object/type/path-line checks before any asset creation/save. |
| N008 | **PARTIAL — supported encoding review** | Recursive comparison handles arrays, struct leaves, enum values, soft-object/class paths and finite scalar values. Engine-specific reflected results remain unverified without Editor readback. |
| N009 | **DONE — canonical serialization review** | Writer and offline validator both hash UTF-8 JSON with `ensure_ascii=False`, sorted keys, compact separators and `allow_nan=False`; validator removes only `manifest_sha256` before recomputing. |
| N010 | **DONE — read-only source review** | Selection validator loads assets/receipt, invokes the offline validator and emits diagnostics; it has no asset setter/save path. No assets exist to invoke it against. |

## Change and checks

The creator now validates that `properties`, `field_sources` and tagged struct
fields are objects, and that citation paths/positive line numbers and enum/
struct type names are well-formed. These checks run before asset creation.
Python AST parsing and `git diff --check` passed. No tests, Editor, asset save,
build or Unreal execution was performed.
