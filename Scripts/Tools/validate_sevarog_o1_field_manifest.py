"""Offline source validator for C-1646's Sevarog field-manifest requirement."""
import argparse
import json
from pathlib import Path
import sys

from sevarog_boss_core_required_fields import extract_required_paths


OWNER_PATHS = {
    "Stats.MaxHealth", "Stats.MaxPosture", "Stats.PostureRegenDelay", "Stats.PostureRegenRate",
    "Phases[Phase_1].EntryHealthFraction", "Phases[Phase_1].SpeedMultiplier",
    "Phases[Phase_1].RateMultiplier", "Phases[Phase_1].AttackMultiplier",
}
CONFIG_TYPES = {
    "Stats": "FRPGBossStatsConfig", "EncounterPolicy": "FRPGEncounterPolicyConfig",
    "StaggerPolicy": "FRPGStaggerPolicyConfig", "PhaseFlow": "FRPGPhaseFlowConfig",
    "Fireball": "FRPGFireballConfig", "PhaseDependencies": "FRPGPhaseDependencyConfig",
    "StaggerProfile": "FRPGStaggerProfileConfig", "DormantWake": "FRPGDormantWakeConfig",
    "Bleed": "FRPGBleedConfig", "LowSweep": "FRPGLowSweepConfig",
    "Shockwave": "FRPGShockwaveConfig", "HealPunish": "FRPGHealPunishConfig",
    "Look": "FRPGLookConfig", "CloseClipSwap": "FRPGCloseClipSwapConfig",
    "Death": "FRPGDeathConfig", "AttackTracker": "FRPGAttackTrackerConfig",
}


def snake(name):
    import re
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def reflected_properties(root, struct_name):
    import re
    matches = []
    for header in (root / "Source/OneBossFight/Player").glob("*.h"):
        source = header.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"struct\s+" + re.escape(struct_name) + r"\b.*?\{(.*?)\n\};", source, re.S)
        if match:
            matches.append(match)
    match = matches[0] if len(matches) == 1 else None
    if not match:
        raise ValueError("reflected config struct not found: " + struct_name)
    names = set()
    for line in match.group(1).splitlines():
        if "UPROPERTY" not in line:
            continue
        declaration = line.split(")", 1)[-1].split(";", 1)[0]
        declaration = declaration.split("=", 1)[0].strip()
        pieces = declaration.split()
        if pieces:
            names.add(pieces[-1].lstrip("*").strip())
    return names


def validate(root):
    required = extract_required_paths(root)
    if len(required) != 115:
        raise ValueError("BossCore required path count is %d; expected 115" % len(required))
    if not OWNER_PATHS.issubset(required):
        raise ValueError("one or more O1-approved paths are absent from BossCore plan requirements")
    binding = (root / "Source/OneBossFight/Player/RPGEncounterBinding.cpp").read_text(encoding="utf-8")
    metadata_checks = (
        "F.FieldPath.IsEmpty()", "F.Type.IsEmpty()", "F.SourcePath.IsEmpty()",
        "!IsSHA256(F.SourceSHA256)", "F.SourceSite.IsEmpty()", "F.Origin.IsEmpty()",
        "F.Precedence.IsEmpty()", "F.Destination.IsEmpty()", "F.FirstRead.IsEmpty()", "F.Witness.IsEmpty()",
    )
    missing = [pattern for pattern in metadata_checks if pattern not in binding]
    if missing:
        raise ValueError("binding manifest metadata checks changed: " + ", ".join(missing))
    unresolved_properties = []
    for path in required - {"Phases[Phase_1].EntryHealthFraction", "Phases[Phase_1].SpeedMultiplier",
                           "Phases[Phase_1].RateMultiplier", "Phases[Phase_1].AttackMultiplier"}:
        group, prop = path.split(".", 1)
        config_type = CONFIG_TYPES.get(group)
        if not config_type or snake(prop) not in {snake(name) for name in reflected_properties(root, config_type)}:
            unresolved_properties.append(path)
    if unresolved_properties:
        raise ValueError("required path has no reflected config property: " + ", ".join(sorted(unresolved_properties)))
    return {
        "schema": "onebossfight.sevarog-o1-static-field-requirements/v1",
        "result": "PASS",
        "required_path_count": len(required),
        "owner_o1_path_count": len(OWNER_PATHS),
        "draft_preimage_path_count": len(required - OWNER_PATHS),
        "owner_o1_paths": sorted(OWNER_PATHS),
        "draft_preimage_paths": sorted(required - OWNER_PATHS),
        "field_metadata_required": ["FieldPath", "Type", "SourcePath", "SourceSHA256",
                                    "SourceSite", "Origin", "Precedence", "Destination",
                                    "FirstRead", "Witness"],
        "binding_source": "Source/OneBossFight/Player/RPGEncounterBinding.cpp",
        "plans_source": "Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.root.resolve())
    except Exception as error:
        print(json.dumps({"result": "FAIL", "error": str(error)}, indent=2))
        return 1
    text = json.dumps(result, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
