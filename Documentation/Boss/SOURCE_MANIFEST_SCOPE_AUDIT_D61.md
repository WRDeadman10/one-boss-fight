# Source-manifest scope audit (Queue D D61)

## Inclusion and exclusions

`Scripts/Tools/make_source_manifest.py:14-24` sets the scan root to `<root>/Source`, recursively selects every path for which `is_file()` is true, sorts paths, hashes raw bytes with SHA-256, and writes root-relative POSIX path rows. There is no extension, VCS, generated-file, hidden-directory, or build-artifact filter inside `Source`; any present regular file found by the traversal is part of the manifest. The manifest does not include files outside `Source`.

Accordingly, normal project `Content/` assets, `.uproject`, `Config/`, plugins outside `Source`, scripts/docs, `Intermediate/`, `Saved/`, `Binaries/`, packaged outputs, and engine binaries are not covered by this snapshot. Plugin code under `Source/` is included if traversed; plugin content/config outside `Source/` is not. The S187 checklist accurately states the tool is Source-only and calls for separate content/config/build/run identities. A Source digest alone does not identify the complete project or prove which build/run consumed it.

## Operational edges

- A missing `<root>/Source` tree is silently an empty iteration and can produce an empty manifest; S173's CLI inventory flags this behavior. Therefore `files=0` is not a successful whole-project fingerprint.
- Output is not excluded from traversal. If a caller places the output file inside `Source/`, an existing manifest may be hashed as an input on subsequent invocations, making the snapshot self-referential and unstable. Keep output outside the scanned tree.
- The script hashes the bytes reached through file paths; it does not record file type, symlink metadata, untracked status, revision, build ID, or artifact provenance. A symlinked file's target-byte behavior and directory-link traversal depend on `pathlib` traversal semantics and are not specified as a stable scope contract in the script.
- `atomic_write_text` protects destination replacement per file; it does not make the manifest a complete repository snapshot or preserve a prior copy automatically.

Conclusion: describe the result as a sorted SHA-256 inventory of files found under `Source/` at capture time. Treat content/config/plugins outside that tree, build/package artifacts and run evidence as separate identities. Static source/docs review only; no manifest was generated.
