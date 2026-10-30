import os

citations = [
    ("Documentation/DECISIONS.md", "## Back to the pack's own player and boss (2026-10-19, later)"),
    ("Documentation/DECISIONS.md", "logged `GetMainAnimBP` Accessed None errors every frame"),
    ("Documentation/DECISIONS.md", "Revert the 60 pack assets that stage 3 re-pointed to the `_Grey` copies"),
    ("Documentation/DECISIONS.md", "The arena boss is `BP_ExampleGreatSwordBoss` with `EnemyInfoRef` set on the placed instance"),
    ("Documentation/DECISIONS.md", "the pack boss Blueprint defaults `EnemyInfoRef` to the sword mob"),
    ("Documentation/KNOWN_ISSUES.md", "| KI-040 | Greystone | Several retargeted layer Blueprints"),
    ("Documentation/KNOWN_ISSUES.md", "| KI-049 | Sevarog | Abilities granted before the controller existed"),
    ("Documentation/KNOWN_ISSUES.md", "| KI-052 | Project | Greystone and Sevarog retired"),
    ("Documentation/Boss/Morgott_82_Point_Combat_Reference/Morgott_82_Point_Combat_Reference.md", "### Example move inventory (15 attack families)"),
    ("Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow.uasset", None),
    ("Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_FAST_v2.uasset", None),
    ("Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Cast.uasset", None),
    ("Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Speedburst.uasset", None),
    ("Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Subjugation.uasset", None),
    ("Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Ultimate_Swing_120fps.uasset", None),
    ("Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Bound.uasset", None),
]

all_ok = True
for path, text_snippet in citations:
    if not os.path.exists(path):
        print(f"FAILED: Path does not exist: {path}")
        all_ok = False
        continue
    if text_snippet is not None:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        if text_snippet not in content:
            print(f"FAILED: Snippet '{text_snippet}' not found in {path}")
            all_ok = False
        else:
            for idx, line in enumerate(content.splitlines()):
                if text_snippet in line:
                    print(f"VERIFIED: {path}:{idx+1} -> {line.strip()[:70]}")
                    break
    else:
        print(f"VERIFIED ASSET ON DISK: {path}")

if all_ok:
    print("\nALL CITATIONS & ASSET TARGETS 100% VERIFIED AGAINST DISK.")
else:
    raise SystemExit("Verification failed!")
