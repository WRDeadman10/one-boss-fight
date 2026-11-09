import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]


class PackParryContactContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contact = (ROOT / "Source/OneBossFight/Player/RPGPackParryContact.cpp").read_text(encoding="utf-8")
        cls.rules = (ROOT / "Source/OneBossFight/Player/RPGPackParryRules.h").read_text(encoding="utf-8")
        cls.parry = (ROOT / "Source/OneBossFight/Player/RPGPlayerParry.cpp").read_text(encoding="utf-8")
        cls.resolver = (ROOT / "Source/OneBossFight/Player/RPGDamageResolver.cpp").read_text(encoding="utf-8")
        cls.posture = (ROOT / "Source/OneBossFight/Player/RPGBossPosture.cpp").read_text(encoding="utf-8")
        cls.subsystem = (ROOT / "Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp").read_text(encoding="utf-8")

    def test_observer_is_always_on_and_attached_to_pack_boss(self):
        self.assertIn("PrimaryComponentTick.bCanEverTick = true", self.contact)
        self.assertIn("PrimaryComponentTick.TickGroup = TG_PostUpdateWork", self.contact)
        self.assertIn("NewObject<URPGPackParryContact>", self.subsystem)
        self.assertNotIn("UE_BUILD_SHIPPING", self.contact)

    def test_native_window_and_invulnerability_fail_closed(self):
        self.assertIn("Parry->IsWindowOpen()", self.contact)
        self.assertIn("bWindowOpen || (bHasPreviousParrySample && bPreviousParryWindowOpen)", self.contact)
        self.assertIn("if (!bInvulnKnown)", self.contact)
        self.assertIn("if (!bHealthKnown)", self.contact)
        self.assertNotIn("Status.ParryActive", self.contact)
        self.assertIn("CanStartCandidate(bCandidateWindow, bInvulnerable)", self.contact)

    def test_contact_waits_for_100ms_without_health_loss(self):
        self.assertIn("ElapsedSeconds < RequiredSeconds", self.rules)
        self.assertIn("HealthNow < HealthBefore - LossTolerance", self.rules)
        self.assertIn("Now - Candidate.InsertedAt", self.contact)
        self.assertTrue(re.search(r"EvaluateCandidate\(bHealth(?:Now)?Known", self.contact))

    def test_wall_seed_and_carried_hits_are_ignored(self):
        self.assertIn("Guard->IsSeed(Hit)", self.contact)
        self.assertIn("Guard->GetCarriedAtOpen()", self.contact)
        self.assertIn("PreviousHitSet.Add(Carried)", self.contact)

    def test_tracked_and_untracked_keys_are_stable_and_shared(self):
        self.assertIn("GetAttackInstance()", self.contact)
        self.assertRegex(self.contact, r"StartWorld\s*=\s*WorldTime\s*-\s*static_cast<double>\(Position / Rate\)")
        self.assertIn("Montage->GetFName(), StartWorld", self.contact)
        self.assertIn("RewardDeduplicator.TryAccept(Generation, AttackKey)", self.parry)
        self.assertIn("RPGPackParry::BuildAttackKey(Payload.Generation", self.resolver)
        self.assertIn("URPGPlayerParry::NotifyParried(Target, GetOwner()", self.resolver)

    def test_reward_has_parity_effects_and_optional_deferred_posture(self):
        for effect in ("ParriedCount", "SpawnConfiguredEffect", "PlayParryRecoil", "HandlePlayerParrySlowMotion"):
            self.assertIn(effect, self.parry)
        self.assertIn("QueueParryPostureDamage()", self.parry)
        self.assertIn("ParryPostureDamage = 0.f", (ROOT / "Source/OneBossFight/Player/RPGBossPosture.h").read_text(encoding="utf-8"))
        self.assertIn("PendingParryPostureDamage", self.posture)
        self.assertIn("ApplyPostureDamage(Pending, TEXT(\"confirmed parry\"))", self.posture)

    def test_source_automation_cases_are_registered(self):
        tests = (ROOT / "Source/OneBossFight/Tests/RPGPackParryContactTests.cpp").read_text(encoding="utf-8")
        for name in ("CandidateRules", "AttackIdentityAndDeduplication", "PostureDefaultIsInert"):
            self.assertIn(f"OneBossFight.Player.PackParry.{name}", tests)

    def test_runtime_diagnostics_explain_observer_early_outs(self):
        for marker in ("observer_target", "trace_edge", "hitset_insert", "skip reason=%s"):
            self.assertIn(marker, self.contact)
        for reason in ("target_unresolved", "native_window_closed", "invulnerability_unknown", "health_unknown_at_insert", "attack_key_unresolved", "duplicate_attack_key"):
            self.assertIn(f'TEXT("{reason}")', self.contact)
        self.assertIn("WorldTime - *LastTime < 1.0", self.contact)


if __name__ == "__main__":
    unittest.main()
