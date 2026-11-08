"""Offline source contract for the optional Tier 2 aura attach socket."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "Source" / "OneBossFight" / "Boss" / "RPGTier2BossPresentation.h"
SOURCE = ROOT / "Source" / "OneBossFight" / "Boss" / "RPGTier2BossPresentation.cpp"


class Tier2AuraAttachSocketContract(unittest.TestCase):
    def test_opt_in_socket_defaults_to_mesh_origin(self):
        header = HEADER.read_text(encoding="utf-8")
        self.assertIn("FName AuraAttachSocket = NAME_None;", header)
        self.assertIn("Optional mesh socket", header)

    def test_niagara_spawn_uses_the_configured_socket(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SpawnSystemAttached(Aura, Mesh, AuraAttachSocket,", source)
        self.assertNotIn("SpawnSystemAttached(Aura, Mesh, NAME_None,", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
