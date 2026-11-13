#!/usr/bin/env python3
"""Offline guard and definition-parity contracts for test-only UFUNCTIONs."""
from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HEADER_PATHS = tuple(sorted((path for path in (ROOT / "Source/OneBossFight").rglob("*.h")
                            if re.search(r"(DamageResolver|Framework|Dodge|Parry)", path.name, re.IGNORECASE)),
                           key=lambda path: path.as_posix()))
EXPECTED_TEST_UFUNCTIONS = {
    "RPGFrameworkBossCharacter.h": [
        "InitializeSelectedEncounterForTest", "InitializeWithProfileForTest", "StartCardForTest", "SetBossHealthFractionForTest", "StartSelectedCardForTest",
        "GetOutcomeForTest", "GetCurrentPhaseForTest", "GetNavigationResultForTest", "StartComboForTest",
        "SpawnFrameworkBossForTest",
    ],
    "RPGFrameworkProofFixture.h": ["RestartEncounterForTest"],
    "RPGDamageResolver.h": ["ResolveForTest", "NoteOverlapForTest"],
}


def test_ufunctions(text):
    """Return (name, editor_only_data_guarded) for test-only reflected methods."""
    lines = text.splitlines()
    stack = []
    found = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#if "):
            stack.append(stripped[4:].strip())
        elif stripped.startswith("#ifdef "):
            stack.append("defined(" + stripped[7:].strip() + ")")
        elif stripped.startswith("#ifndef "):
            stack.append("!defined(" + stripped[8:].strip() + ")")
        elif stripped.startswith("#else") and stack:
            condition = stack[-1]
            stack[-1] = "!" + condition if not condition.startswith("!") else condition[1:]
        elif stripped.startswith("#endif") and stack:
            stack.pop()
        if "UFUNCTION(" not in line:
            continue
        declaration = " ".join(lines[index + 1:index + 5])
        match = re.search(r"\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:const\s*)?;", declaration)
        if not match:
            continue
        name = match.group(1)
        if "Test" in name or "test" in line:
            found.append((name, any(condition in ("WITH_EDITORONLY_DATA", "!UE_BUILD_SHIPPING",
                                                   "WITH_DEV_AUTOMATION_TESTS") for condition in stack)))
    return found


class ShippingReflectionContract(unittest.TestCase):
    def test_scoped_test_only_reflected_declarations_are_guarded(self):
        declarations = {}
        for path in HEADER_PATHS:
            declarations[path.name] = test_ufunctions(path.read_text(encoding="utf-8"))
        for path in HEADER_PATHS:
            actual = [name for name, _ in declarations[path.name]]
            self.assertEqual(actual, EXPECTED_TEST_UFUNCTIONS.get(path.name, []), path.name)
        self.assertTrue(all(guarded for rows in declarations.values() for _, guarded in rows))

    def test_reflected_declarations_have_cpp_definitions(self):
        pairs = (
            ("RPGFrameworkBossCharacter.h", ROOT / "Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp"),
            ("RPGFrameworkProofFixture.h", ROOT / "Source/OneBossFight/Boss/RPGFrameworkProofFixture.cpp"),
            ("RPGDamageResolver.h", ROOT / "Source/OneBossFight/Player/RPGDamageResolver.cpp"),
        )
        for header_name, cpp_path in pairs:
            header = next(path for path in HEADER_PATHS if path.name == header_name).read_text(encoding="utf-8")
            source = cpp_path.read_text(encoding="utf-8")
            for name, _ in test_ufunctions(header):
                if header_name == "RPGFrameworkBossCharacter.h" and name in {
                        "InitializeSelectedEncounterForTest", "InitializeWithProfileForTest", "StartCardForTest", "SetBossHealthFractionForTest", "StartSelectedCardForTest",
                        "GetOutcomeForTest", "GetCurrentPhaseForTest", "GetNavigationResultForTest", "StartComboForTest",
                        "SpawnFrameworkBossForTest"}:
                    self.assertIn("ARPGFrameworkBossCharacter::" + name, source)
                elif header_name == "RPGFrameworkProofFixture.h":
                    self.assertIn("ARPGFrameworkProofFixture::" + name, source)
                else:
                    self.assertIn("URPGDamageResolver::" + name, source)

    def test_deliberately_unguarded_fixture_is_rejected(self):
        fixture = """UCLASS()\nclass AFixture : public AActor {\nGENERATED_BODY()\npublic:\nUFUNCTION(BlueprintCallable, Category=\"Test\")\nbool RestartEncounterForTest(int32 Generation);\n};\n"""
        with tempfile.TemporaryDirectory(prefix="bf_reflection_fixture_") as temp:
            path = Path(temp) / "Fixture.h"
            path.write_text(fixture, encoding="utf-8")
            findings = test_ufunctions(path.read_text(encoding="utf-8"))
            self.assertEqual(findings, [("RestartEncounterForTest", False)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
