# Morgott, the Omen King — 82-point combat reference

This package maps the user's exact 83-item boss audit checklist to documented Morgott combat behavior, excluding only **BOSS-QA-008**, the optional multiplayer/network-authority item. It contains:

- `Morgott_82_Point_Combat_Reference.docx` — formatted 21-page document for review.
- `Morgott_82_Point_Combat_Reference.md` — complete Markdown reference for Codex, Claude, and Antigravity.
- `requirements.json` — structured list of all 82 requirements, their evidence grades, suggested Unreal implementation, and acceptance tests.
- `diagrams/*.png` — five original design diagrams.

**Research and evidence limits:** The game’s visible behavior and detailed community observations are distinguishable from unverified internal implementation details. Neither document should be presented as FromSoftware source code, and the classifications do not reflect the state of your own Unreal boss implementation.

**Evidence labels:** O = observed encounter mechanic; R = community report; I = inference; U = unverified engine internals.

**Suggested Codex usage:** Read the markdown as a comparative reference; use IDs `BOSS-...` to cross-reference the current boss audit. Do not implement changes until a source-backed gap and relevant design approval are established.
