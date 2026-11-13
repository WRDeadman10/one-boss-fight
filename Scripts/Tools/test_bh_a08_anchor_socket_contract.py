import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUTHOR_SCRIPT = REPO_ROOT / "Scripts" / "Editor" / "author_sevarog_draft_cards.py"
ANCHOR_DOC = REPO_ROOT / "Documentation" / "Boss" / "BH_A06_A10_SIGNATURE_ANCHORS.md"
QUEUE_DOC = REPO_ROOT / "Documentation" / "Boss" / "QUEUE_BH_AG.md"

EXPECTED_SLOT_BY_INDEX = {
    2: ("S3", "DA_Move_Sevarog_Swing3_Slow_C1247"),
    3: ("S4", "DA_Move_Sevarog_Speedburst_C1247"),
    5: ("S6", "DA_Move_Sevarog_Ultimate_Swing_120fps_C1277"),
    6: ("S7", "DA_Move_Sevarog_Subjugation_C1277"),
    7: ("S8", "DA_Move_Sevarog_Soul_Siphon_C1277"),
}


class BhA08AnchorSocketContractTest(unittest.TestCase):
    def test_documented_slot_to_card_ids_and_sockets_match_author_script(self) -> None:
        script_text = AUTHOR_SCRIPT.read_text(encoding="utf-8")
        doc_text = ANCHOR_DOC.read_text(encoding="utf-8")
        queue_text = QUEUE_DOC.read_text(encoding="utf-8")

        tree = ast.parse(script_text, filename=str(AUTHOR_SCRIPT))
        card_names = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CARD_NAMES" for t in node.targets
            ):
                card_names = ast.literal_eval(node.value)
                break
        self.assertIsNotNone(card_names, "CARD_NAMES constant missing from author_sevarog_draft_cards.py")

        for idx, (slot_id, card_name) in EXPECTED_SLOT_BY_INDEX.items():
            self.assertEqual(card_names[idx], card_name, f"Slot {slot_id} index {idx} drifted in authoring script")

        expected_pairs = (
            "`S3` — Swing3_Slow",
            "`S4` — Speedburst",
            "`S7` — Subjugation",
            "`S8` — Soul Siphon",
            "S6=Ultimate_Swing_120fps",
            "DA_Move_Sevarog_Swing3_Slow_C1247",
            "DA_Move_Sevarog_Speedburst_C1247",
            "DA_Move_Sevarog_Subjugation_C1277",
            "DA_Move_Sevarog_Soul_Siphon_C1277",
            "weapon_r",
            "root_weapon_end_r",
            "HitGroup_ScytheBlade",
            "area_effect",
            "channel_drain",
        )
        for token in expected_pairs:
            self.assertIn(token, doc_text, f"Missing ID-to-card / socket token in anchor doc: {token}")

        self.assertIn("(`S3`/`S4`/`S7`/`S8`", queue_text)
        self.assertIn("`Subjugation_sheet.png` (`S7`) & `Soul_Siphon_sheet.png` (`S8`", queue_text)
        self.assertIn("`Swing3_Slow_sheet.png` (`S3`) & `Speedburst_sheet.png` (`S4`", queue_text)
        self.assertIn("BLOCKED", doc_text)
        self.assertIn("LevelStart", doc_text)


if __name__ == "__main__":
    unittest.main()
