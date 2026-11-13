"""BM-31..35 (C, implementer; lane BM batch 7; KI-175 / KI-176 / KI-181): static source pins for three low, unverified issues that cannot be
reproduced deterministically offline (KI-175/176 need live lifecycle / attribute-failure evidence; KI-181 needs a compiled selector).
Nothing is compiled or run. Each test pins the exact source fact the KI depends on, so a source change that silently resolves or worsens it
fails here and forces the KI to be re-triaged.
"""
import re
import unittest
from pathlib import Path

PLAYER = Path(__file__).resolve().parents[2] / "Source" / "OneBossFight" / "Player"


def read(name):
    return (PLAYER / name).read_text(encoding="utf-8-sig", errors="replace")


class Ki175ParryStateHasNoReset(unittest.TestCase):
    def test_state_member_and_no_reset_path(self):
        header, source = read("RPGPlayerParry.h"), read("RPGPlayerParry.cpp")
        self.assertRegex(header, r"RPGParry::FState\s+State\s*;")
        # No assignment that resets the whole state (State = ... / State = RPGParry::FState()) anywhere in the component.
        self.assertIsNone(re.search(r"\bState\s*=\s*(RPGParry::)?FState\s*\(", source))
        self.assertIsNone(re.search(r"\bState\s*=\s*\{", source))


class Ki176UncappedRefundBranch(unittest.TestCase):
    def test_refund_caps_only_when_max_is_readable(self):
        source = read("RPGPlayerParry.cpp")
        capped = 'if (RPGPack::ReadAttribute(GetOwner(), TEXT("Attribute.Stamina"), true, Max) && FMath::IsFinite(Max)) After = RPGParryCost::ParryRefund(After, Max, PaidStaminaCost);'
        self.assertIn(capped, source)
        self.assertIn("else After += PaidStaminaCost * .5;", source)  # the uncapped fallback the KI describes


class Ki181SubnormalScoreUnderflow(unittest.TestCase):
    def test_score_is_a_double_product_narrowed_to_float(self):
        source = read("RPGBossMoveSelector.cpp")
        self.assertIn("T.bEligible=true; T.Score=float(C.Weight*RangeFactor*Repeat*Pattern);", source)

    def test_candidate_factors_are_float(self):
        header = read("RPGBossMoveSelector.h")
        for field in ("Weight", "KiteMultiplier", "HugMultiplier", "BackDodgeMultiplier", "GreedMultiplier"):
            with self.subTest(field=field):
                self.assertRegex(header, r"float\s+%s\s*=" % field)

    def test_underflow_arithmetic(self):
        """The product is computed in double (no underflow there), and only the float narrowing can flush it to zero: two positive
        subnormal float factors (1e-40 each) give 1e-80 in double, which narrows to 0.0f, while the candidate stays eligible."""
        import struct
        def as_float(x):  # IEEE-754 single-precision round trip
            return struct.unpack("f", struct.pack("f", x))[0]
        weight = as_float(1e-40)
        self.assertGreater(weight, 0.0)                       # a positive subnormal float
        self.assertEqual(as_float(weight * as_float(1e-40)), 0.0)


if __name__ == "__main__":
    unittest.main()
