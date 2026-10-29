import json
from pathlib import Path
import unittest
from validate_team_pipeline import validate

HERE = Path(__file__).resolve().parent


class PipelineContractTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((HERE / "TEAM_PIPELINE.json").read_text())
        self.rows = json.loads((HERE / self.data["source_ledger"]).read_text())["rows"]

    def test_current_queue(self):
        result = validate(self.data, self.rows)
        self.assertEqual((result["work_cards"], result["required_rows"]), (43, 83))

    def test_cycle_rejected(self):
        self.data["cards"][0]["depends_on"] = ["C20"]
        with self.assertRaisesRegex(ValueError, "cycle"):
            validate(self.data, self.rows)

    def test_unknown_dependency_rejected(self):
        self.data["cards"][0]["depends_on"] = ["UNKNOWN"]
        with self.assertRaisesRegex(ValueError, "Unknown dependency"):
            validate(self.data, self.rows)

    def test_waiver_and_missing_row_rejected(self):
        self.data["requirements"][0]["required"] = False
        with self.assertRaisesRegex(ValueError, "Waived"):
            validate(self.data, self.rows)
        self.data["requirements"].pop()
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate(self.data, self.rows)

    def test_blanket_execution_rejected(self):
        self.data["cards"][0]["execution_released"] = True
        with self.assertRaisesRegex(ValueError, "blanket-release"):
            validate(self.data, self.rows)


if __name__ == "__main__":
    unittest.main()
