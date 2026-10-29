"""Validate planning dependencies/coverage, not implementation or runtime behavior."""
import hashlib
import json
from pathlib import Path


def validate(data, rows):
    cards = data["cards"]
    by_id = {c["id"]: c for c in cards}
    if len(by_id) != len(cards):
        raise ValueError("Duplicate work card")
    visiting, done = set(), set()
    def visit(code):
        if code not in by_id:
            raise ValueError(f"Unknown dependency {code}")
        if code in visiting:
            raise ValueError(f"Dependency cycle at {code}")
        if code in done:
            return
        visiting.add(code)
        for parent in by_id[code]["depends_on"]:
            visit(parent)
        visiting.remove(code)
        done.add(code)
    for card in cards:
        if card["owner"] not in {"Claude", "Antigravity"}:
            raise ValueError("Unrecognized implementation owner")
        if card["execution_released"] or card["git_released"]:
            raise ValueError("Roadmap must not blanket-release execution/git")
        visit(card["id"])
    expected = {r["id"] for r in rows}
    actual = [r["id"] for r in data["requirements"]]
    if len(actual) != len(set(actual)) or set(actual) != expected or len(actual) != 83:
        raise ValueError("Required83 coverage mismatch")
    assigned = [rid for card in cards for rid in card["primary_requirement_ids"]]
    if len(assigned) != 83 or set(assigned) != expected:
        raise ValueError("Missing or duplicate primary ownership")
    for row in data["requirements"]:
        if row["required"] is not True or row["primary_card"] not in by_id:
            raise ValueError("Waived or unowned requirement")
        if row["id"] not in by_id[row["primary_card"]]["primary_requirement_ids"]:
            raise ValueError("Inconsistent requirement mapping")
    return {"scope": "Planning structure only, NOT project completion/UE proof", "work_cards": len(cards),
        "claude_cards": sum(c["owner"] == "Claude" for c in cards),
        "antigravity_cards": sum(c["owner"] == "Antigravity" for c in cards),
        "required_rows": len(actual), "dag_acyclic": True, "future_execution_blanket_released": False}


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    data = json.loads((root / "TEAM_PIPELINE.json").read_text())
    raw = (root / data["source_ledger"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != data["source_sha256"]:
        raise SystemExit("Source ledger drift")
    print(json.dumps(validate(data, json.loads(raw)["rows"]), indent=2))
