"""Generate a header, automation-test, and designer-reference skeleton for a pure rule."""
import argparse
import re
import sys
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))  # BP-01/02: sibling imports work as a script or as `python -m Scripts.Tools.*`
from atomic_io import atomic_create_text


NAME_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def header_text(name, namespace):
    return f'''// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"

/** TODO: state units, valid domain, and invalid-input behavior. */
namespace {namespace}
{{
    // TODO: define explicit configuration/state only when the rule needs it.
    struct FConfig {{ }};

    // TODO: implement a deterministic, side-effect-free rule with a documented fallback.
}}
'''


def test_text(name, namespace):
    class_name = "FBoss" + name + "RulesScaffold"
    automation_name = "OneBossFight.Framework." + name + ".RulesScaffold"
    return f'''// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBoss{name}Rules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST({class_name}, "{automation_name}", EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool {class_name}::RunTest(const FString&)
{{
    using namespace {namespace};
    // TODO: replace this placeholder body with assertions that fail for a wrong rule.
    // This empty scaffold test is not evidence of rule correctness.
    return true;
}}
#endif
'''


def reference_text(name, requirement_id):
    header = "RPGBoss" + name + "Rules.h"
    tests = "RPGBoss" + name + "RulesTests.cpp"
    return f'''# Designer reference: {requirement_id}

TODO: one-sentence purpose and whether the rule is wired to runtime behavior.

| Input / output | Unit | Default | Valid domain / behavior |
|---|---|---|---|
| TODO | TODO | TODO | TODO |

Document the exact threshold inclusivity, invalid-input fallback, and caller-owned state/reset behavior. Do not claim the rule is live-proven without a cited PIE log.

Source: [`{header}`](../../Source/OneBossFight/Player/{header}:1), unit tests: [`{tests}`](../../Source/OneBossFight/Tests/{tests}:1).
'''


def write_new(path, content):
    atomic_create_text(path, content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True,
                        help="PascalCase rule name without the RPGBoss prefix")
    parser.add_argument("--requirement-id", required=True,
                        help="stable uppercase requirement ID, for example BOSS-EXE-123")
    parser.add_argument("--slug", required=True,
                        help="lowercase hyphenated topic for the reference filename")
    parser.add_argument("--output-root", required=True, type=Path,
                        help="project root or a temporary root; existing target files are refused")
    args = parser.parse_args()

    if not NAME_RE.fullmatch(args.name):
        parser.error("--name must be PascalCase alphanumeric and omit RPGBoss")
    if not ID_RE.fullmatch(args.requirement_id):
        parser.error("--requirement-id must be uppercase words separated by hyphens")
    if not SLUG_RE.fullmatch(args.slug):
        parser.error("--slug must be lowercase words separated by hyphens")

    root = args.output_root.resolve()
    stem = "RPGBoss" + args.name
    namespace = "RPGBoss" + args.name
    destinations = {
        root / "Source/OneBossFight/Player" / (stem + "Rules.h"): header_text(args.name, namespace),
        root / "Source/OneBossFight/Tests" / (stem + "RulesTests.cpp"): test_text(args.name, namespace),
        root / "Documentation/Boss" / ("RULES_REFERENCE_%s_%s.md" % (args.requirement_id, args.slug)): reference_text(args.name, args.requirement_id),
    }
    existing = [str(path) for path in destinations if path.exists()]
    if existing:
        print("Refusing to overwrite existing scaffold target(s):", file=sys.stderr)
        for path in existing:
            print("- " + path, file=sys.stderr)
        return 2

    for path, content in destinations.items():
        write_new(path, content)
        print(path)
    print("Scaffold created. Replace every TODO; the generated test is intentionally not a correctness test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
