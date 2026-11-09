import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class VisualWeaponTraceContract(unittest.TestCase):
    def test_pack_facade_can_switch_trace_source_and_expose_live_source(self):
        header = (ROOT / "Source/OneBossFight/Pack/RPGPackTrace.h").read_text()
        source = (ROOT / "Source/OneBossFight/Pack/RPGPackTrace.cpp").read_text()
        self.assertIn("bool SetTraceSource(UPrimitiveComponent* Mesh, const TArray<FName>& Sockets)", header)
        self.assertIn("FTarget::SetTraceSource(UPrimitiveComponent* Mesh", source)
        self.assertIn("UpdateTraceLocations", source)
        self.assertIn("Current Collision Mesh", source)
        self.assertIn("CollisionSockets", source)

    def test_guard_routes_to_visual_weapon_and_keeps_pack_fallback(self):
        header = (ROOT / "Source/OneBossFight/Player/RPGTraceGuard.h").read_text()
        source = (ROOT / "Source/OneBossFight/Player/RPGTraceGuard.cpp").read_text()
        self.assertIn("GetTraceSourceComponent", header)
        self.assertIn("GetTraceSocketNames", header)
        self.assertIn("GetFallbackTraceSourceComponent", header)
        self.assertIn("GetFallbackTraceSocketNames", header)
        self.assertIn("URPGBossLook", source)
        self.assertIn("GetSwordComponent", source)
        self.assertIn('Trace_', source)
        self.assertIn("OriginalTraceMesh", header)
        self.assertIn("OriginalTraceSockets", header)

    def test_pie_probe_covers_idle_and_attack_moves_with_world_transform_rows(self):
        probe = ROOT / "Scripts/Editor/pie_ember_visual_weapon_trace.py"
        self.assertTrue(probe.exists())
        text = probe.read_text()
        for marker in ("IDLE", "A1", "A2", "A3", "hand_component", "hand_r", "grip_socket", "tip_socket", "get_socket_location", "WORLD", "OFFSET_CM"):
            self.assertIn(marker, text)
        self.assertIn('tracker.play_move_montage_for_test(move)', text)
        self.assertIn('tracker.start_move(move, True)', text)
        self.assertIn('encounter.wake()', text)
        self.assertIn('encounter.hold_for_test(True)', text)
        self.assertIn('encounter.is_dormant() or encounter.is_waking()', text)
        self.assertIn('tracker.enter_combat()', text)
        self.assertIn('sword.get_all_socket_names()', text)

if __name__ == "__main__":
    unittest.main()
