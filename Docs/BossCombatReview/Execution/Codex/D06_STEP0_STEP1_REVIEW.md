# D06 — DD-1 step 0 / step 1 independent review

Codex, 2026-10-25. C-98/2. Verdict: **CHANGES REQUIRED before step 1**. This is a specification review, not an implementation review or a test pass. Claude retains implementation/editor/build ownership. Reviewed STEP0_BASELINE.md, STEP0_MANIFEST.json and its complete generator, STEP1_SPEC.md, the native consumers below, test sources and RunDrivers.ps1. No engine tools were run.

## Step 0: useful pin, acceptance still pending

Independently hashed all 1,077 listed file records: 136 source, 5 config, 605 project assets, 330 Editor Python files and one editor DLL. All matched the current files at review time. This confirms those records, not an atomic snapshot, dependency closure, runtime test result, or absence of newly added files. The advertised combined digest excludes scripts and DLL by design.

STEP0_BASELINE.md:26-28 correctly leaves the current gate and automation results pending. The named `Saved/rundrivers_dd1_step0_baseline.txt` was not accessible (Test-Path false) at this review. Missing output is not a failed gate. Prior 37/37 and 37 static registrations are not a current automation pass. Do not advance until the actual baseline run, failures/classifications and current-binary automation artifacts are available and independently reviewable.

### R1 — high: the fourth build cannot traverse the specified existing consumers

STEP1_SPEC.md:13 limits loadout work to fixed-table indexing; :33 permits unknown IDs to become Starter through the enum facade. The real selection/loadout path is enum-based, not merely indexing: RPGBuildSelectRules.h:16/27, RPGBuildSelect.cpp:401-436, RPGBuildLoadout.h:184/203, RPGBuildLoadout.cpp:383-409/492-530/637 onward. An in-memory fourth-row enumeration test (:22) does not demonstrate selection, deferred application, verification, equipped style or HUD identity. Silent Starter is a wrong successful selection, not compatibility.

Required correction: stable BuildId through parse, chosen/requested/equipped state, same-choice detection, queue/defer, CallEquip lookup, verification and HUD. Enum adapters may expose only the three pinned legacy slots; an unrepresentable ID must return an explicit failure, never an existing build. Preserve the old invalid-enum clamp separately: RPGBuildRules.h:54 and RPGCodexTests.cpp:124-130 currently require enum 99 to resolve Dex. Do not change that legacy API while inventing a new ID fallback. Pin legacy-slot mapping independently of data UiOrder.

Proof: fourth data-only build and weapon through the same selector and loadout path, actual resolved item/class/ability/style and attack-table row, delayed in-fight choice, reset/reapply, HUD and invalid-ID rejection. The three shipped builds retain their exact old behavior. A synthetic resolver test is useful but insufficient for end-to-end capability; a later real canary is still required.

### R2 — high: freeze one complete registry source/epoch, not per-lookup fallback

STEP1_SPEC.md:7/11/13 leaves “delegate first, then legacy” ambiguous. Validation must construct a complete immutable snapshot, then publish either that snapshot OR the complete legacy snapshot once per startup/explicit safe lifecycle boundary. Every related operation carries that epoch; no valid data entry may be combined with a missing legacy weapon/alias/icon row. Unknown ID in an accepted catalog is an error, not a fallback. No reload or fallback transition mid-fight/equip transaction. Include provenance and rejection field path in diagnostics.

Specify UObject strong ownership and snapshot lifetime; FBuildEntry currently holds const TCHAR* and returns references. Never return pointers into temporary FString values or a reclaimed/replaced asset. Explicitly define shutdown/world teardown and test-injected catalogs so a test cannot contaminate later worlds. Validate whole-reference closure before publication: item object type, actor/ability class and compatibility, styles/aliases and attack-table coverage, cooked soft dependencies, schema version, case-normalized unique IDs/console names/aliases, reserved empty/none/off handling, deterministic UI order/ties. “Nonempty string” alone is not a usable reference test.

### R3 — high: rollback test is mutating and does not exercise load-once absence

STEP1_SPEC.md:23 calls renaming the catalog “read-only”; :28 proposes delete/rename and restoring edited files from hashes. A loaded-once registry retains its loaded asset; rename after load does not prove startup fallback. Rename/delete is an asset mutation with dependency and interruption risks. A hash cannot reconstruct a file, especially in this owner's dirty tree.

Replace with an explicit startup/test resolver override or isolated test context selecting absent/invalid/valid complete catalog, no asset rename/delete and no global live reload. Prove each in a fresh instance/session. Specify recorded preimages/owned patch reversal and previous complete binding; rollback only at a safe lifecycle boundary. Never reset/stash/checkout user work. Any future code/config/asset claims remain Claude's, not authorized by this review.

### R4 — medium: parity witnesses and fourth-row input are underspecified

STEP1_SPEC.md:17/21 promises exact text but omits DescribeStyle's distinct SwordAndShield and Twinblade labels (RPGBuildRules.h:257-294), actual versus chosen build HUD, Unknown/off-build messages, equipping/next-fight/not-equipped suffixes, invalid choice not changing state, parser quote/case/whitespace/reserved-value behavior, and alias canonicalization. RPG Boss HUD consumes GetBuildLine (RPGBossHud.cpp:488-491); it is a witness even if its source need not change. Preserve quickslot call ordering, same-choice semantics, startup delay/retries, fight lock and failed equip classification, not merely fields.

RPGBuildSelect.cpp:131/141-173/191-197 also hardcodes row count, hit-testing, keys 1-3 and icon order. Define mouse, keyboard/focus navigation, viewport bounds and fourth-row icon fallback with unchanged first-three placement/input. List these consumers explicitly; no assumption that dynamic row count fixes input or persistent Chosen enum. Retain BuildCount=3 only for legacy callers/tests, not dynamic UI/runtime loops.

### R5 — medium: strengthen the baseline closure and reproducibility record

Generator dd1_step0_manifest.py:37-38 does not check git return codes; :47 onward parses RunDrivers.ps1 but does not hash that file or retain K/T/Setup, actual invocation/Full selection, expanded commands, preset files or outputs. It hashes Editor Python sources but not the wrapper/bridge/bootstrap dependencies. Pin these plus relevant pack assets and external skeleton/style/material dependencies read by the test, project/plugin/engine identity and effective harness settings; pack unchanged is a claim to hash, not a reason to omit it. No pack edits are requested.

Preserve this first manifest; add versioned supplemental records instead of rerunning its overwrite-capable generator over the pin. Include generator hash, explicit coverage/exclusions, checked git errors, file-list additions/removals, run start/end source/dependency digests and result/log hashes. Record actual default and driver cvars, preset state, restored-window/tick cadence, map/instance overrides, startup/cleanup and current binary. Source hash does not identify a driver's effective preset. `no_throttle.py` disables background throttling but does not itself prove a minimized window is restored. Timing validity should be evaluated per evidence type, not invalidate a static inventory because a timing run was slow.

Current RunDrivers.ps1 hash independently read: CDEDAD68B4AF79504E278BFCCF2029F4ADB6F5A6839F961291BD45E351729535. This is a supplemental observation, not proof of the command currently running.

## Acceptance requested from Claude

Revise the specification against R1-R4 and supplement step 0 per R5; provide the current gate/automation artifacts when available. Codex can then review the corrected scope and evidence. Do not classify the pending run as a defect solely because its named output is absent. Step 0's behavior table also needs the E-005/E-008 wording corrections in the separate C-98/3 review: preserve mechanisms and sampled outcomes, not a hardcoded statistical 10/11 invariant or an unproven visible-floor interpretation.

No source, config, asset, script, pack, editor, build, PIE, commit or push action by Codex. No P1 change is approved here.
