#!/usr/bin/env python3
"""Offline source contract for the framework health/HUD/terminal integration."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class FrameworkIntegrationContract(unittest.TestCase):
    def read(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def test_native_provider_exposes_health_generation_and_terminal(self):
        source = self.read("Source/OneBossFight/Player/RPGNativeBossHealth.h")
        for token in (
            "ReadNativeHealth(bool bMax",
            "NativeEncounterGeneration() const",
            "IsNativeEncounterActive() const",
            "IsNativePhaseTwo() const",
            "NativeTerminalDelegate()",
            "FMath::IsFinite(MaxHealth) && MaxHealth > 0.0",
        ):
            self.assertIn(token, source)

    def test_framework_death_notifies_once_with_its_generation(self):
        source = self.read("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp")
        death = source.split("void ARPGFrameworkBossCharacter::Die()", 1)[1].split(
            "void ARPGFrameworkBossCharacter::Fail(", 1
        )[0]
        self.assertLess(death.index("if (bDead) return;"), death.index("NativeTerminal.Broadcast(this, GenerationId);"))

    def test_hud_binds_cleans_up_and_rejects_stale_terminal_events(self):
        source = self.read("Source/OneBossFight/UI/RPGBossHud.cpp")
        self.assertIn("NativeTerminalDelegate().AddUObject", source)
        self.assertIn("NativeTerminalDelegate().Remove(NativeTerminalHandle)", source)
        self.assertIn("RPGBossTerminalRules::ShouldAccept", source)
        tests = self.read("Source/OneBossFight/Tests/RPGNativeBossHealthTests.cpp")
        self.assertIn("stale terminal event is refused", tests)
        self.assertIn("duplicate terminal event is refused", tests)

    def test_selected_native_route_gets_hud_and_music_and_music_reads_native_state(self):
        subsystem = self.read("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp")
        self.assertIn("Participant.Slot == Definition->BossSlot", subsystem)
        self.assertIn("Native->NativeEncounterGeneration() != Binding->ParticipantGeneration", subsystem)
        self.assertIn('NewObject<URPGBossHud>(SelectedBoss, TEXT("RPGBossHud"))', subsystem)
        self.assertIn('NewObject<URPGBossMusic>(SelectedBoss, TEXT("RPGBossMusic"))', subsystem)
        hud = self.read("Source/OneBossFight/UI/RPGBossHud.cpp")
        self.assertIn('RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health")', hud)
        self.assertIn("Widget->EnableRetry(RetryText, RetryDelaySeconds)", hud)
        widget = self.read("Source/OneBossFight/UI/RPGBossHud.cpp")
        self.assertIn("UGameplayStatics::OpenLevel", widget)
        music = self.read("Source/OneBossFight/Audio/RPGBossMusic.cpp")
        self.assertIn("NativeHealth->ReadNativeHealth(false, Health)", music)
        self.assertIn("NativeHealth->IsNativePhaseTwo()", music)

    def test_existing_pack_route_and_restart_generation_guard_remain(self):
        subsystem = self.read("Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp")
        self.assertIn("AttachLegacyBossPrelude(Pawn)", subsystem)
        boss = self.read("Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h")
        self.assertIn("NewGeneration>GenerationId", boss)
        hud = self.read("Source/OneBossFight/UI/RPGBossHud.cpp")
        self.assertIn("NativeTerminalDelegate().Remove(NativeTerminalHandle)", hud)


if __name__ == "__main__":
    unittest.main(verbosity=2)
