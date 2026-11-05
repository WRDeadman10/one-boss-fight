# H047 — Lead and owner decision register

**Reviewed:** 2026-11-04 against C-800 through C-803 and current Queue H evidence. This lists actual gates only; it does not request or imply approval.

| Decision | Authority | Current safe state | Impact / next action |
|---|---|---|---|
| Same-world selected-route respawn rebind implementation and measured order | Claude / Lead (C-804) | Reset multicast and Step A log tokens are approved; only instrumentation is implemented. Interim fail-closed behavior stays. | Claude measures live spawn/reset/broadcast/release order; then Step B may add the separately scoped begun-world compiler/rebind path. No rebind implementation before that run. |
| Production default encounter definition and Shipping selection provider | Human owner (C-800) | No definition is default. `rpg.EncounterDefinition` exists only outside Shipping; no Shipping selection API has been approved. | Owner must choose product default/scope or authorize a separate Shipping-safe selection mechanism before any default or packaged data-route success claim. |
| Main-map/binary-map edits and A7 legacy retirement | Human owner (C-800/Queue H) | No `.umap` change and no legacy attach retirement. | Keep the selected route opt-in and preserve no-selection legacy behavior until explicit owner authorization. |
| Definition asset content and canonical manifest values | Asset author/Lead review; product choices remain owner-owned | G044 script refuses because typed boss/player definitions and a manifest receipt are absent. | Provide sourced typed asset values and receipt; do not fabricate values or overwrite assets. Claude performs Editor/PIE validation. |
| Framework witness ledger JSON reconciliation | Antigravity | JSON remains v3.36 75/7/0; Claude's later 80/82 verdict exists in Codex-owned reports. | Antigravity updates the authoritative ledger; Codex leaves it untouched. |

No other owner decision is needed to continue offline documentation or comparator fixture work. H048–H050 record actual statuses and the next queue.
