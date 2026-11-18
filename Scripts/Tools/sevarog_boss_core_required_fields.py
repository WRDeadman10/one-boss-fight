"""Static extractor for Sevarog's required typed manifest paths.

This deliberately understands only the current BossCore plan factories. A source
shape change that cannot be resolved fails closed so an editor authoring run
cannot silently omit a required field.
"""
from pathlib import Path
import re


PLAN_FILES = (
    "RPGBossStaggerClusterAdapters.cpp", "RPGBossPhasesClusterAdapters.cpp",
    "RPGBossEncounterClusterAdapters.cpp", "RPGBossDormantWakeAdapters.cpp",
    "RPGBossStatsAdapters.cpp", "RPGBossBleedAdapters.cpp",
    "RPGBossLowSweepAdapters.cpp", "RPGBossShockwaveAdapters.cpp",
    "RPGBossHealPunishAdapters.cpp", "RPGBossLookAdapters.cpp",
    "RPGBossCloseClipSwapAdapters.cpp", "RPGBossDeathAdapters.cpp",
    "RPGBossAttackTrackerAdapters.cpp",
)
PHASE_VALUE_SUFFIXES = ("AttackMultiplier", "EntryHealthFraction", "RateMultiplier", "SpeedMultiplier")


def extract_required_paths(project_root):
    player = Path(project_root) / "Source" / "OneBossFight" / "Player"
    constants = {}
    for header in player.glob("*.h"):
        source = header.read_text(encoding="utf-8", errors="replace")
        namespace = re.search(r"namespace\s+(\w+)", source)
        if not namespace:
            continue
        for name, value in re.findall(
            r"(?:inline\s+)?constexpr\s+const TCHAR\*\s+(\w+)\s*=\s*TEXT\(\"([^\"]+)\"\)", source
        ):
            constants[(namespace.group(1), name)] = value

    paths = set()
    unresolved = []
    for filename in PLAN_FILES:
        cpp = player / filename
        source = cpp.read_text(encoding="utf-8", errors="replace")
        namespaces = set()
        for included in re.findall(r'#include\s+"Player/([^\"]+\.h)"', source):
            header = player / included
            if header.exists():
                contents = header.read_text(encoding="utf-8", errors="replace")
                namespace = re.search(r"namespace\s+(\w+)", contents)
                if namespace:
                    namespaces.add(namespace.group(1))
        blocks = re.findall(r"Plan\.RequiredFields\s*=\s*\{(.*?)\};", source, re.S)
        if filename == "RPGBossPhasesClusterAdapters.cpp":
            blocks += re.findall(r"const TArray<FString> Rest\s*=\s*\{(.*?)\};", source, re.S)
        for block in blocks:
            for qualifier, name in re.findall(r"(?:(\w+)::)?\b(Field\w+)\b", block):
                if name == "FieldPath":  # suffix of PhaseFieldPath(...)
                    continue
                if qualifier:
                    value = constants.get((qualifier, name))
                    if value is not None and qualifier == "RPGBossPhaseAdapters":
                        paths.add("Phases[Phase_1]." + value)
                    elif value is not None:
                        paths.add(value)
                    else:
                        unresolved.append(filename + ":" + qualifier + "::" + name)
                else:
                    candidates = {constants[(namespace, name)] for namespace in namespaces
                                  if (namespace, name) in constants}
                    if len(candidates) == 1:
                        paths.add(next(iter(candidates)))
                    else:
                        unresolved.append(filename + ":" + name)

    if unresolved:
        raise ValueError("unresolved required manifest symbols: " + ", ".join(sorted(set(unresolved))))
    return frozenset(paths)
