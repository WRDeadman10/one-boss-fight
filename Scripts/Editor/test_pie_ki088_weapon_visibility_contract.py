"""Source contracts for C-1189: hide the pack weapon without breaking trace sockets."""

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]


class KI088WeaponVisibilityContract(unittest.TestCase):
    def test_active_look_reasserts_render_hidden_state_and_restores_it(self):
        header = (ROOT / "Source/OneBossFight/Player/RPGBossLook.h").read_text(encoding="utf-8")
        source = (ROOT / "Source/OneBossFight/Player/RPGBossLook.cpp").read_text(encoding="utf-8")
        self.assertIn("TickComponent(float DeltaTime", header)
        self.assertIn("void HidePackWeapons();", header)
        self.assertIn("PrimaryComponentTick.bCanEverTick = true;", source)
        self.assertIn("PrimaryComponentTick.TickGroup = TG_PostUpdateWork;", source)
        tick = source.split("void URPGBossLook::TickComponent", 1)[1].split("void URPGBossLook::SetEnabledForTest", 1)[0]
        self.assertIn("if (bApplied && bEnabled)", tick)
        self.assertIn("HidePackWeapons();", tick)
        hide = source.split("void URPGBossLook::HidePackWeapons", 1)[1].split("void URPGBossLook::Revert", 1)[0]
        self.assertIn('Candidate->GetName().Contains(TEXT("Weapon"))', hide)
        self.assertIn("PackWeaponWasVisible.Add(Candidate->IsVisible())", hide)
        self.assertIn("PackWeaponWasHidden.Add(Candidate->bHiddenInGame)", hide)
        self.assertIn("Candidate->SetVisibility(false, /*bPropagateToChildren=*/true)", hide)
        self.assertIn("Candidate->SetHiddenInGame(true, /*bPropagateToChildren=*/true)", hide)
        self.assertNotIn("SetStaticMesh(nullptr)", source)
        revert = source.split("void URPGBossLook::Revert", 1)[1]
        self.assertIn("Weapon->SetVisibility(PackWeaponWasVisible", revert)
        self.assertIn("Weapon->SetHiddenInGame(PackWeaponWasHidden", revert)

    def test_pack_trace_socket_fallback_remains_live(self):
        guard = (ROOT / "Source/OneBossFight/Player/RPGTraceGuard.cpp").read_text(encoding="utf-8")
        pack_trace = (ROOT / "Source/OneBossFight/Pack/RPGPackTrace.cpp").read_text(encoding="utf-8")
        self.assertIn("OriginalTraceMesh = PackMesh", guard)
        self.assertIn("OriginalTraceSockets = MoveTemp(PackSockets)", guard)
        self.assertIn("if (!bOriginalTraceCaptured)", guard)
        self.assertIn("DesiredMesh = OriginalTraceMesh.Get()", guard)
        self.assertIn("bool RPGPackTrace::FTarget::SetTraceSource", pack_trace)
        self.assertIn("Mesh->DoesSocketExist(Socket)", pack_trace)


if __name__ == "__main__":
    unittest.main()
