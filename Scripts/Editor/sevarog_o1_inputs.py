"""Load the separately approved O1 values without promoting the historical PENDING manifest."""
import hashlib
import json
import math
from pathlib import Path


MANIFEST = Path(__file__).with_name("sevarog_o1_inputs.json")
EXPECTED_SCHEMA = "onebossfight.owner-approved-sevarog-o1/v1"
EXPECTED_VALUES = {
    "Stats.MaxHealth": 1500.0,
    "Stats.MaxPosture": 100.0,
    "Stats.PostureRegenDelay": 6.0,
    "Stats.PostureRegenRate": 13.0,
    "Phases[Phase_1].EntryHealthFraction": 0.6,
    "Phases[Phase_1].SpeedMultiplier": 1.0,
    "Phases[Phase_1].RateMultiplier": 1.0,
    "Phases[Phase_1].AttackMultiplier": 1.0,
}


def approved_float_matches(actual, expected):
    """Compare reflected Unreal float32 readbacks to approved Python values."""
    try:
        actual_number = float(actual)
        expected_number = float(expected)
    except (TypeError, ValueError, OverflowError):
        return False
    return (math.isfinite(actual_number) and math.isfinite(expected_number)
            and abs(actual_number - expected_number) <= 1e-4)


def load_approved_values(repo_root=None):
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema") != EXPECTED_SCHEMA or data.get("decision") != "O1":
        raise ValueError("O1 approved-values manifest schema/decision mismatch")
    source = data.get("source", {})
    if source.get("path") != "Documentation/DECISIONS.md":
        raise ValueError("O1 source must be the recorded DECISIONS.md excerpt")
    excerpt = source.get("excerpt")
    if not isinstance(excerpt, str) or not excerpt:
        raise ValueError("O1 source excerpt is missing")
    digest = hashlib.sha256(excerpt.encode("utf-8")).hexdigest()
    if source.get("sha256") != digest:
        raise ValueError("O1 excerpt hash mismatch")
    if repo_root is not None:
        source_path = Path(repo_root) / source["path"]
        if excerpt not in source_path.read_text(encoding="utf-8"):
            raise ValueError("O1 excerpt is not present in the cited decision record")
    values = data.get("values")
    if values != EXPECTED_VALUES:
        raise ValueError("O1 values differ from the approved decision set")
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v)
           for v in values.values()):
        raise ValueError("O1 values must all be finite numbers")
    return values
