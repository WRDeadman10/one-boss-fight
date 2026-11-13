"""Offline guard contract for the non-saving Greystone wrapper readback."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / "Scripts" / "Editor" / "verify_greystone_wrapper_readback.py"
AUTHOR = ROOT / "Scripts" / "Editor" / "author_greystone_player.py"


class WrapperReadbackContract(unittest.TestCase):
    def test_readback_uses_transient_cpp_wrapper_and_imports_author_module(self):
        source = DRIVER.read_text(encoding="utf-8")
        self.assertIn("sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))", source)
        self.assertIn("create_retarget_wrapper", source)
        self.assertIn("outer_path.endswith(\"/Transient\")", source)
        self.assertIn("compare_wrapper_notify_rows", source)
        self.assertIn("author.readback_montage(spec, wrapper, slot, source_desc, sequence, sections)", source)

    def test_driver_does_not_save_or_create_assets(self):
        source = DRIVER.read_text(encoding="utf-8")
        for forbidden in ("save_loaded_asset", "save_asset", "create_asset", "delete_asset"):
            self.assertNotIn(forbidden, source)

    def test_cpp_transient_api_and_detailed_rows_are_used(self):
        header = (ROOT / "Source" / "OneBossFightEditor" / "Public" / "RPGMontageWrapperLibrary.h").read_text(encoding="utf-8")
        source = (ROOT / "Source" / "OneBossFightEditor" / "Private" / "RPGMontageWrapperLibrary.cpp").read_text(encoding="utf-8")
        self.assertIn("CreateTransientRetargetWrapper", header)
        self.assertIn("DescribeMontageNotifies", header)
        for field in ("Event.GetTriggerTime()", "Event.GetDuration()", "Event.TrackIndex", "Slot.SlotName", "Animation->GetPathName()", "Animation->GetPlayLength()"):
            self.assertIn(field, source)

    def test_source_table_is_four_allowlisted_montages(self):
        source = AUTHOR.read_text(encoding="utf-8")
        self.assertIn('ALLOWLIST = "/Game/OneBossFight/Player/Greystone/"', source)
        self.assertIn('MONTAGES = [', source)
        self.assertEqual(source.count('"field":'), 4)


if __name__ == "__main__":
    unittest.main()
