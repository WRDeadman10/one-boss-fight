# BI-X16–X20 — SFX Owner Pick Intake and Path Audit

**Status:** Offline documentation proposal; no Owner choices, audio wiring, asset edits, tests, or Editor actions were performed.  
**Decision gate:** SFX remains silent/unwired until the Owner explicitly selects A/B/C or `None`; any implementation still requires Lead review and the existing integration gate.

## BI-X16 — Current manifest and Owner-pick inventory

| Scope | Source of options / evidence | Current disposition | Reel state |
|---|---|---|---|
| SFX-01..05 / GAP-1..5 | `SFX_03_AUDITION_MANIFEST.md`; wiring proposal `SFX_04_WIRING_PLAN.md`; blocker ledger `BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md` | Awaiting explicit Owner pick (including `None`); no wiring authorized | Full first reel and parry addendum reported ready off-repo; not independently checked here |
| SFX-06..10 | `QUEUE_SFX.md`; `BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md` | Awaiting picks | Priority backlog; reel export not recorded as complete |
| SFX-11..15 | `SFX_05_BATCH3_CANDIDATE_SPEC.md`; `SFX_06_BATCH3_AUDITION_MANIFEST.md`; `BB_A05...` | Awaiting explicit Owner pick | Batch 3 reel and 15 cue clips reported ready off-repo |
| SFX-16..45 | `SFX_07...SFX_12` candidate specs; `BB_A05...` | Awaiting Owner pick; later specs are not evidence of selection | Specs only or held-ready; reel/export status varies by batch |
| Sevarog card audio S1..S8 | `BB_A11_A13_SEVAROG_CARD_SFX_SPEC.md` | Spec-only; `FRPGBossCue.Sound` stays null/unassigned | No pick recorded |
| Sevarog voice barks | `BB_A14_SEVAROG_VOICE_BARKS_SPEC.md` | Spec-only; Owner selection and Lead gate pending | No pick recorded |

The blocker ledger says the explicit A/B/C-or-None gate applies to SFX-01..45. It also says Sevarog framework audio remains spec-only. A candidate marked “Preferred” in a proposal is not an Owner decision.

## BI-X17 — Intake data shape

Draft machine-readable schema: `SFX_OWNER_PICK_INTAKE_V1.schema.json`. It requires an event identity, A/B/C option records, an explicit lifecycle status, and evidence for any decision. `pending` requires a null decision; `selected` and `none` require an explicit choice plus an Owner evidence reference. `None` is a valid explicit decision, not missing data. The schema carries a constant wiring gate to prevent interpreting a pick receipt as implementation approval.

Example pending record (no choices populated):

```json
{
  "schema_version": 1,
  "event_id": "SFX-01",
  "event_name": "Player Parry Success",
  "status": "pending",
  "options": { "A": null, "B": null, "C": null },
  "owner_decision": null,
  "wiring_gate": "blocked_until_owner_pick_and_lead_review"
}
```

The example intentionally leaves options empty because this intake record is not the candidate manifest; a populated intake should copy asset paths and cited source documents verbatim from the current authoritative manifest. Do not derive an option from “Preferred,” an old summary, or an inferred aesthetic.

## BI-X18 — Path mapping audit

| Candidate scope | Current specific path evidence | Older/competing path text | Finding |
|---|---|---|---|
| GAP-1 parry | `SFX_03` gives `.../Wavs/Sword_Attack/Sword_Attack_Short_1`; addendum uses `.../Wavs/Sword_Attack/Sword_Attack_Short_2`; sword-impact options use complete `.../DemoAssets/SoundFX/Combat/SwordImpacts/SwordImpact1|3` paths | `SFX_02` and `SFX_04` use shortened root-level names; `SFX_03` explicitly marks its 7.62 s sharpening option defective, while `SFX_04` still lists a 0.35 s cue by that name | Stale/inconsistent. Do not present the old sharpening candidate as equivalent or preferred; verify exact runtime wrapper separately before wiring. |
| GAP-2 recoil | `SFX_03` source paths are `.../Sounds/SoundWaves/Sevarog_Effort_Block_01`, `...PainHeavy_01`, `...Frustration_01`; `BB-A11..13` documents runtime wrappers under `.../Sounds/SoundCues/...` | `SFX_02`/`SFX_04` list SoundCue paths (without `_01` on names) | These are different asset kinds, not interchangeable paths. Candidate source and runtime wrapper must be explicitly paired in a revised spec. |
| GAP-3 ignite | `SFX_03` specifies waveform sources under `/Audio/Waves/`; `SFX_05/06` SFX-13 option A uses runtime wrapper `/Audio/Cues/SFX_Vefects_Shockwave_01_1s_Cue`; StarterContent option B uses `/Audio/Explosion_Cue` | `SFX_02`/`SFX_04` cite abbreviated `/Audio/SFX_Vefects..._Cue` without `Waves` or `Cues` folder | Stale/incomplete path. Distinguish source Wave from runtime Cue. |
| GAP-4 backstep | `SFX_03` uses Wave paths under `/Wavs/Sword_Swoosh/` or `/Wavs/Sword_Unsheathe/`; `BB-A11..13` runtime examples use `/Cues/Sword_Swoosh/..._Cue` | `SFX_02`/`SFX_04` omit `/Wavs` or `/Cues` and event subfolders | Stale/incomplete path; exact runtime wrapper remains to be confirmed for each candidate. |
| GAP-5 stance break | `SFX_03` lists StarterContent `Collapse01`, ARPG `A_Guardian_Impact01`, and Sevarog `.../SoundWaves/Sevarog_ProfileDizzy_010`; `BB-A11..13` gives a runtime `A_Guardian_ImpactL_Cue` example | `SFX_02`/`SFX_04` cite `Collapse_Cue`, `A_Guardian_ImpactL_Cue`, and Sevarog `SoundCues/...ProfileDizzy_010` | Name, folder, and asset-kind drift; do not merge these into one path. Resolve wrappers against disk before any implementation. |
| SFX-11..15 | `SFX_05` candidate spec and `SFX_06` audition manifest use matching full Cue paths for the 15 listed clips, including the SFX-13 `/Audio/Cues/..._Cue` path | Not applicable to older GAP summaries | The two Batch 3 documents match for the reviewed option paths. Reel presence is reported in manifest, not verified as media in this review. |

`BB-A11..13` and `BB-A14` are detailed Sevarog-specific specs, not authority to wire: both expressly retain null/unassigned defaults and await Owner/Lead gates. `SFX_04` itself labels the wiring plan proposed/plan-only and says no apply/asset edits until a pick.

## BI-X19 — Safe authoring/wiring gate map

1. Owner decision record names event ID and explicit A/B/C or `None`, with a mailbox/document reference. If `None`, keep that event silent and close no unrelated cue.
2. Reconcile the selected candidate's exact on-disk asset kind and full runtime path. If auditioned Wave differs from runtime Cue wrapper, document the pairing and confirm wrapper exists; do not substitute a similar name.
3. Lead reviews event hook, timing, routing, default-off/null behavior, `-nosound` behavior, pack-asset boundary, and diagnostic/verification plan.
4. Only after those gates: schedule authorized authoring under the engine lock, change project-native source/assets only, run offline contract checks, then Lead owns native build/runtime acceptance as assigned.
5. Preserve the distinction between an Owner's sound preference and approval to implement; a pick alone does not authorize wiring.

## BI-X20 — Disposition and blockers

- No Owner choice is recorded in the reviewed specifications; all listed SFX remain blocked on explicit Owner disposition.
- `SFX_02` and parts of `SFX_04` contain shortened/stale paths and outdated preference/duration claims relative to `SFX_03` and the later batch manifests.
- SoundWave source paths and SoundCue runtime wrapper paths are mixed across docs. Specific selected assets need a disk-backed path/type reconciliation before authoring.
- The schema is a proposal only. No options have been transcribed into a decision record, and no Owner selection is inferred.
- Scope was static document comparison. No asset registry, D: audition media, or Editor was inspected, so existence/media readability claims are not newly certified here.

**Result:** BI-X16..X20 complete as offline static audit and intake proposal. No test or engine operation was run; no audio or runtime change made. Continue to BI-X21..X25, checking Claude feedback and hotfix requests on the next cycle.
