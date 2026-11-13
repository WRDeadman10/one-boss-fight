"""BM-36..40 (C, implementer; lane BM batch 8; KI-174 / KI-154 / KI-136): static source pins for framework-boss issues that need live PIE
evidence to reproduce. Nothing is compiled or run. A change to any pinned fact fails here and forces the KI to be re-triaged.
"""
import re
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "Source" / "OneBossFight"


def lines(rel):
    return (SRC / rel).read_text(encoding="utf-8-sig", errors="replace").splitlines()


def find(rel, pattern):
    return [i + 1 for i, l in enumerate(lines(rel)) if re.search(pattern, l)]


class Ki174LeashDoesNotPauseComboDeadline(unittest.TestCase):
    REL = "Boss/RPGFrameworkBossCharacter.cpp"

    def test_leash_return_precedes_the_combo_pause_check_in_tick(self):
        tick = find(self.REL, r"^void ARPGFrameworkBossCharacter::Tick\(")[0]
        leash = [n for n in find(self.REL, r"bArenaLeash\)\{HandleLeash\(\);return;\}") if n > tick][0]
        pause = [n for n in find(self.REL, r"if\(bComboPausing\)\{if\(GetWorld\(\)->GetTimeSeconds\(\)<ComboPauseUntil\)return;") if n > tick][0]
        self.assertLess(leash, pause, "the leash early-return runs before the combo pause is evaluated")

    def test_pause_deadline_is_absolute_world_time(self):
        self.assertTrue(find(self.REL, r"ComboPauseUntil=GetWorld\(\)->GetTimeSeconds\(\)\+double\(R\.PauseSeconds\)"))

    def test_leash_handler_does_not_touch_combo_pause_state(self):
        src = lines(self.REL)
        start = find(self.REL, r"^void ARPGFrameworkBossCharacter::HandleLeash\(")[0]
        end = next(i for i in range(start, len(src)) if src[i].startswith("}")) + 1
        body = "\n".join(src[start - 1:end])
        self.assertNotIn("bComboPausing", body)
        self.assertNotIn("ComboPauseUntil", body)


class Ki154JavelinParriedRouting(unittest.TestCase):
    def test_parried_outcome_finishes_as_parried(self):
        src = "\n".join(lines("Player/RPGBossJavelin.cpp"))
        self.assertRegex(src, r"case ERPGDamageOutcome::Parried:\s*(//[^\n]*\n\s*)*[^\n]*\n?\s*Finish\(ERPGJavelinResult::Parried")


class Ki136DeathCitations(unittest.TestCase):
    def test_death_lifecycle_comments_cite_ki136(self):
        """KI-136 / BQ-09: the three death-lifecycle comments (pack destroys the dead boss) cite KI-136; the PIE
        set_editor_property hazard comment keeps citing KI-083. Updated from the BM-36..40 pin when BQ-09 landed."""
        self.assertTrue(find("Player/RPGBossDeath.cpp", r"after its death \(KI-136\)"))
        self.assertTrue(find("Player/RPGBossDeath.h", r"a few seconds later \(KI-136\)"))
        self.assertTrue(find("Player/RPGBossDeath.h", r"4\.35 s later: KI-136\)"))
        self.assertFalse(find("Player/RPGBossDeath.cpp", r"\(KI-083\)"))
        self.assertTrue(find("Player/RPGBossDeath.h", r"KI-083: set_editor_property"), "the tooling hazard citation stays KI-083")


if __name__ == "__main__":
    unittest.main()
