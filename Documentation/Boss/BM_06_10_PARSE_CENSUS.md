# BM-06..10: Python parse census (lane BM, batch 2 of 10; KI-170/171)

C (implementer), 2026-11-12.

New file: `Scripts/Tools/test_python_parse_census.py`. **No script was edited, imported or executed.** No Unreal, build, commit or push.

## BM-06: census (run)

`ast.parse` over every `Scripts/**/*.py` (excluding `__pycache__`), as text: **990 files, 0 parse failures in the working tree.**

## BM-07: KI-170 / KI-171, finding

**Both files fail at HEAD and parse in the working tree** because of uncommitted edits made by someone else before this batch (`git status`: ` M`). Each HEAD version was checked by parsing `git show HEAD:<file>`.

| KI | File | HEAD (committed) | Working tree | Uncommitted repair (`git diff`) |
|---|---|---|---|---|
| KI-170 | `Scripts/author_brief13_anims.py` | **fails** at `141:66`, `invalid decimal literal` | parses | the embedded code string changes from `r"""…"""` to `r'''…'''`, so the inner `"""…"""` docstring no longer ends it. **Syntax-only.** |
| KI-171 | `Scripts/Editor/sevarog_pack_02_montages_abilities.py` | **fails** at `215:4`, `unexpected indent` | parses | `unreal.BlueprintEditorLibrary.compile_blueprint(hs)` is indented into the preceding block. **This is control flow, not only syntax:** it decides whether the compile runs inside that block. HEAD never parsed, so there is no prior behavior to preserve. **The lead should review whether that placement is intended.** |

**Disposition:** the KI-170/171 repairs exist but are **uncommitted and unverified in the Editor**. Both KIs should stay Open until:
1. the repairs are committed through the normal route (Antigravity, on the owner's word);
2. KI-171's indentation intent is confirmed;
3. the reflected Editor checks the KI rows require are run (engine-gated).

## BM-08: classification of every script (fix / quarantine / leave)

| Class | Scripts |
|---|---|
| fix | none: no other script fails to parse |
| leave | all 988 others |
| repaired (uncommitted) | the 2 KI files above |
| quarantine | not needed |

## BM-09: regression test

`python -m unittest discover -s Scripts/Tools -p test_python_parse_census.py -v` → **`Ran 2 tests ... OK`**:
- every script parses (and the census really scanned more than 900 files);
- both KI files parse in the working tree.

**Caveat:** the second test passes only while the uncommitted repairs are present. Reverting them would make it fail, which is the intended alarm.

## BM-10: limits

- Parsing is not correctness: no script was executed, and Unreal property names (KI-169/171) still need reflected Editor checks (engine-gated).
- Invalid-escape `SyntaxWarning`s are suppressed and not counted as failures.
- The census reflects the working tree on 2026-11-12, including other agents' uncommitted edits.
