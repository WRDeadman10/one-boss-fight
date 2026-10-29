"""Write the owner's long team queue; planning data only, never dispatches jobs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "ALL83_EXECUTION_LEDGER_2026-10-27.json"

# owner, stage, id, concrete product, dependencies, acceptance
CARDS = [
    ("Claude", "M00", "C00", "DD17 corrected world-input compiler and real-GI tests", [], "Actual lifecycle checkpoint/source review; no manufactured epoch"),
    ("Claude", "M00", "C01", "DD18 world preparation facade, owned registry, tokens and tests", ["C00"], "Whole-batch ownership, stale-token and cleanup source review"),
    ("Claude", "M00", "C02", "Frozen reviewed foundation build/focused/full raw evidence", ["C00", "C01"], "Actual exits/unique membership/log SHA/source and binary pins; stop on failure"),
    ("Antigravity", "M00", "A00", "Correct toolkit code, native-domain guards and independent regression inputs", [], "No bypassed editor guard, omitted record, fake legacy constant or shallow snapshot"),
    ("Antigravity", "M00", "A01", "Exact UE5.5 API/readback cases and dry-run support packet", ["A00"], "Source-reviewed unsupported API handling; engine branches explicitly unexecuted"),
    ("Claude", "M01", "C03", "Serialized read-only preview then separately released new-asset application", ["C02", "A01", "A02"], "Actual Details/serialization/negative results on exact outputs; original assets unchanged"),
    ("Antigravity", "M01", "A02", "Two boss/player draft inputs and additive build preview content", ["A00"], "Exact native schema, truthful dependency/manifest gaps, no fake Ready"),
    ("Antigravity", "M01", "A03", "Owner-run authoring walkthrough tied to observed preview outputs", ["C03"], "Build/weapon/boss distinctions and demonstrated versus unresolved steps explicit"),
    ("Claude", "M02", "C04", "Typed configuration/adapters for remaining actual legacy consumers", ["C03", "A04"], "All required consumer reads accounted for without default/order drift"),
    ("Claude", "M02", "C05", "Complete-bundle capability/authority validation and tests", ["C04", "A05"], "Reject incomplete bundles; server ownership contract and publication preconditions explicit"),
    ("Antigravity", "M02", "A04", "Actual remaining consumer profile/source dependency packets", ["C03"], "Project-owned content, pinned source defaults versus authored values; no invented fields"),
    ("Antigravity", "M02", "A05", "Complete-bundle negative compatibility inputs", ["A04", "C04"], "Missing/wrong-class/skeleton/phase/capability examples fail for the right reasons"),
    ("Claude", "M03", "C06", "Single-owner startup coordinator and controlled publication", ["C05", "C01", "A06"], "No incomplete Ready/duplicate consumers/legacy suppression; partial effects quarantined"),
    ("Claude", "M03", "C07", "Explicit target, reset and generation lifecycle integration", ["C06", "A07"], "Stale event/timer/actor replacement rejection and cleanup before reuse"),
    ("Antigravity", "M03", "A06", "Explicit encounter placement inputs with stable identities", ["C05"], "No player0/slot-name role inference or silently regenerated encounter identity"),
    ("Antigravity", "M03", "A07", "Multi-encounter reset/lifetime input scenarios", ["A06", "C06"], "Repeatable destruction/respawn/overlap/conflict expectations"),
    ("Claude", "M04", "C08", "Data-only canary integration and Boss01-canary-Boss01 replay", ["C07", "A08", "A09"], "Meaningfully different authored moves/phases; no bespoke second-boss C++"),
    ("Antigravity", "M04", "A08", "Actual distinct canary profile/move/phase content", ["C07", "A03"], "Compatible content changes with exact authored delta and no pack edits"),
    ("Antigravity", "M04", "A09", "Canary isolation/replay acceptance scenarios", ["A08"], "Independent encounter diagnostics; no cosmetic-only success"),
    ("Claude", "M05", "C09", "Authoritative pre-montage action identity and execution request", ["C08", "A10"], "Single executor, allocated instance before playback, server-safe correlation"),
    ("Claude", "M05", "C10", "Start rollback, explicit priority, idempotent abort/watchdog", ["C09", "A11"], "No stale callback/duplicate hit/unlock-before-cleanup across failures"),
    ("Antigravity", "M05", "A10", "Actual authored move/event/commit/recovery inputs", ["C08"], "Exact clip/rate/event identities; unknown observations explicitly unresolved"),
    ("Antigravity", "M05", "A11", "Abort/priority/watchdog adversarial input cases", ["A10"], "Real intended competing events/cleanup expectations, no simulated runtime claims"),
    ("Claude", "M06", "C11", "Reliable timelines, bounded motion and honest hit geometry", ["C10", "A12"], "ANM/HIT row-specific outcomes at FPS/time-scale/interrupt boundaries"),
    ("Antigravity", "M06", "A12", "Project-owned contact/timing/motion sources and review captures", ["C10"], "Visible geometry/contact matches declared timings; A5 visuals stay parked"),
    ("Claude", "M07", "C12", "Defense outcomes and legal conditional combo runtime", ["C11", "A13"], "Guard/parry/dodge/posture/riposte and branches match explicit per-move outcomes"),
    ("Claude", "M07", "C13", "Commitment, openings and pressure/pacing runtime", ["C12", "A14"], "Measurable intended punish windows without artificial fairness metrics"),
    ("Antigravity", "M07", "A13", "Defense and conditional-combo content scenarios", ["C11"], "Explicit legal/illegal branch and hit-defense expected outcomes"),
    ("Antigravity", "M07", "A14", "Authored opening/recovery/pacing variants", ["A13", "C12"], "Intended openings are visible and measurable, no hidden fallback tuning"),
    ("Claude", "M08", "C14", "Explicit awareness/eligibility/utility selection runtime", ["C13", "A15"], "Target validity and context-linked choices without omniscience/rival planner"),
    ("Claude", "M08", "C15", "Movement and bounded decaying adaptation runtime", ["C14", "A16"], "No stuck oscillation or stale-target motion; only legal observed inputs"),
    ("Antigravity", "M08", "A15", "Awareness/selection datasets with lawful context inputs", ["C13"], "Reproducible observations, eligibility reasons and adversarial target cases"),
    ("Antigravity", "M08", "A16", "Arena/movement/adaptation scenario inputs", ["C14", "A15"], "Geometry/reach/reset boundaries explicit and no new unapproved arena writes"),
    ("Claude", "M09", "C16", "Phase intelligence/priority/anti-cheese integration", ["C15", "A17"], "Death/break/transition precedence, monotonic phases and fair counterplay"),
    ("Claude", "M09", "C17", "Server-authoritative listen/dedicated two-client validation", ["C16", "A18"], "Real replication/latency/disconnect/reset/stale-instance proof"),
    ("Antigravity", "M09", "A17", "Meaningful phase variants and anti-cheese scenarios", ["C15"], "Authored pressure changes with counterplay; no state-reset exploit"),
    ("Antigravity", "M09", "A18", "Network scene inputs and mismatch/recovery scenarios", ["C16", "A17"], "Two distinct clients, authority roles and observable outcomes specified"),
    ("Claude", "M10", "C18", "Physical input/focus/camera/HUD/audio/readability integration", ["C17", "A19", "A20"], "QA006/007, owner feel and input feedback across supported conditions"),
    ("Antigravity", "M10", "A19", "Readability/accessibility presentation deliverables", ["C17"], "Concrete visible/audio feedback from approved scenarios; no A5 visuals"),
    ("Antigravity", "M10", "A20", "Project-owned source audio/presentation and capture assets", ["C17"], "Exact compatibility/provenance/license/import scope; no pack mutation"),
    ("Claude", "M11", "C19", "Current stable-binary all83/gameplay/network/Shipping/performance proofs", ["C18"], "Per-row evidence plus current cook/debug/soak/FPS/p99 and no inherited old gate"),
    ("Claude", "M11", "C20", "Frozen release candidate and exact batch handoff", ["C19", "A21"], "Owner feel acceptance, immutable artifacts/include-exclude pins, no secret/dirty loss"),
    ("Antigravity", "M11", "A21", "Final owner guide/capture/provenance and released batch execution", ["C19"], "Docs match demonstrated product; git only after separate exact accepted batch order"),
]


def main():
    ledger_bytes = LEDGER.read_bytes()
    rows = json.loads(ledger_bytes)["rows"]
    group_owner = {"EXE": "C09", "ANM": "C11", "HIT": "C11", "DEF": "C12", "COM": "C12",
                   "PAC": "C13", "AWR": "C14", "SEL": "C14", "MOV": "C15", "PHS": "C16"}
    requirements = []
    for row in rows:
        code = row["id"]
        group = code.split("-")[1]
        primary = group_owner.get(group)
        if group == "QA":
            primary = "C17" if code.endswith("008") else "C18" if code.endswith(("006", "007")) else "C19"
        if not primary:
            raise ValueError(f"Unmapped requirement {code}")
        requirements.append({"id": code, "feature": row["feature"], "required": True,
            "primary_card": primary, "verification_method": row["verification_method"],
            "final_acceptance": "OPEN_NOT_RECOUNTED"})
    cards = []
    for owner, stage, code, product, deps, gate in CARDS:
        cards.append({"id": code, "owner": owner, "stage": stage, "product": product, "depends_on": deps,
            "acceptance": gate, "status": "REVIEW_REQUESTED" if code == "C00" else
            "SOURCE_ONLY_RELEASED" if code == "C01" else "CHANGES_REQUIRED_REVIEW_PENDING" if code == "A00" else "QUEUED",
            "execution_released": False, "git_released": False,
            "primary_requirement_ids": [r["id"] for r in requirements if r["primary_card"] == code]})
    result = {"vision": "Data Assets/Details authored reusable boss combat with all83 and server authority; packaged fair/readable duel",
        "authority": "Planning queue only; exact source/operator/activation/git work orders gate execution",
        "current_mailbox": "X285 active source orders; C245 and A179 pending independent review",
        "source_ledger": LEDGER.name, "source_sha256": hashlib.sha256(ledger_bytes).hexdigest(),
        "current_accepted_ue_suite": 119, "overall_completion_percentage": None,
        "cards": cards, "requirements": requirements}
    (HERE / "TEAM_PIPELINE.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(cards)} work cards and {len(requirements)} required row mappings; no jobs dispatched")


if __name__ == "__main__":
    main()
