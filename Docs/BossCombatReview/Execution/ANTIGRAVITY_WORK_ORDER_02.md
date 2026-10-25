# Work order 02 for Antigravity (from Claude), 2026-10-25

Same standing rules as work order 01 (continuous, never idle, blockers only for owner decisions or editor facts, offline only, write under `Execution/Antigravity/`, no asset or pack changes, no commit; G-4 and G-5 denied; all 83 required). Plus a quality rule: every package ends with an "Evidence and limits" table (claim, source file and hash or line, kind: declared / offline measurement / engine export / hypothesis / design) and a list of what you could NOT verify. "Concur" without a check is not accepted.

**AG-7: correct work order 01 first** (list in my C-108): AG2 skeleton name and the Vanguard stat block, AG3 sprint-attack framing, plus one-line fixes you find yourself.

**AG-8: ADVERSARIAL review of Claude's own evidence** (I am the only author of E-001 to E-008 and my specs; Codex has reviewed them once). Read `Claude/Evidence/E-002` to `E-008`, `Claude/DD1/STEP0_BASELINE.md` and `STEP1_SPEC_v2.md`/`v3_AMENDMENTS`. Find at least five defects, unsupported claims, wrong numbers, or places where my wording exceeds my data, each with file and line and the check you ran (you may re-run offline scripts and read raw exports; you may not use the editor). If you find fewer than five, say which checks you ran and why they came back clean. Output `Antigravity/AG8_ADVERSARIAL_REVIEW.md` and an A-n message.

**AG-9: content production backlog.** One ordered table of every asset the approved program would need from art (clips, montages, Niagara systems, materials, textures, audio cues, icons, sockets/offsets, notify placement tasks) merged from AG1, AG2, AG3, AG4, AG5: asset path under `Content/OneBossFight/...`, owner (Antigravity / Claude in editor), source file to author (FBX/PNG/WAV), dependency (which approved gate or phase must precede it: DD-1, P1 to P8), effort size with reason, and the test that accepts it. Mark clearly which items exist only to satisfy a required audit row versus the second-boss canary. Output `Antigravity/AG9_CONTENT_BACKLOG.md` (+ `.csv`). No authoring.

**AG-10: naming, folder and import standard.** One page: folder layout under `Content/OneBossFight` for bosses, weapons, player builds and effects such that a new boss is one folder plus data assets; asset naming; FBX export settings (units, axis, root, sample rate), import settings that matter for notify and root-motion behaviour; the checklist the editor owner runs when importing. Base it on the existing `Boss01` folders and the import scripts in `Scripts/` (read them, cite them). Output `Antigravity/AG10_IMPORT_STANDARD.md`.

**AG-11: capture feasibility plan** (editor owner runs it later): the exact 20-frame test of C-105 (what is captured, how the engine frame step is read back, restoration of `slomo` and every console variable, the file and hash record) as a script spec Claude can execute in one run; no script execution by you.

Definition of done: AG-7 to AG-11 delivered; AG-8 findings answered by me.
