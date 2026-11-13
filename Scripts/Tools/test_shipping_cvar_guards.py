"""BM-21..25 (C, implementer; lane BM batch 5; KI-168 / KI-185): static census of console variables/commands in Source/OneBossFight.

Source-only (nothing compiled or run). Pins:
  1. exactly the six intentionally Shipping-visible controls of KI-168 are declared outside any non-Shipping guard;
  2. the KI-185 failure pattern is absent: no CVar declared under a non-Shipping guard is referenced from code that a Shipping build
     compiles (which broke BUILD-222).
A region counts as non-Shipping when it is inside `#if !UE_BUILD_SHIPPING`, inside `#if UE_BUILD_DEVELOPMENT`, or in the `#else` of
`#if UE_BUILD_SHIPPING`. Comments are ignored. The binary-level Shipping proof of KI-168 stays engine-gated.
"""
import re
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2] / "Source" / "OneBossFight"
DECL = re.compile(r"(?:TAutoConsoleVariable<[^>]+>|FAutoConsoleCommand\w*)\s+(\w+)\s*\(")
SHIPPING_VISIBLE = {"rpg.BossOverlay", "rpg.CloseTelegraph", "rpg.Build", "rpg.CameraDebug", "rpg.Legend", "rpg.LegendShakeScale"}


def non_shipping(frame):
    cond, in_else = frame
    if in_else:
        return re.fullmatch(r"#if\s+UE_BUILD_SHIPPING", cond) is not None
    return re.fullmatch(r"#if\s+!\s*UE_BUILD_SHIPPING", cond) is not None or re.fullmatch(r"#if\s+UE_BUILD_DEVELOPMENT", cond) is not None


def scan(path):
    """[(line_no, code_without_comment, guarded)] for a .cpp file."""
    out, stack = [], []
    for number, raw in enumerate(path.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
        code = raw.split("//", 1)[0]
        s = code.strip()
        if s.startswith("#if"):
            stack.append((re.sub(r"\s+", " ", s), False))
        elif s.startswith("#elif") and stack:
            stack[-1] = (re.sub(r"\s+", " ", s).replace("#elif", "#if", 1), False)
        elif s.startswith("#else") and stack:
            stack[-1] = (stack[-1][0], True)
        elif s.startswith("#endif") and stack:
            stack.pop()
        out.append((number, code, any(non_shipping(f) for f in stack)))
    return out


def census():
    decls, leaks = [], []
    for path in sorted(SOURCE.rglob("*.cpp")):
        rows = scan(path)
        text = "\n".join(c for _, c, _ in rows)
        guarded_vars = {}
        for i, (number, code, guarded) in enumerate(rows):
            m = DECL.search(code)
            if m:
                window = " ".join(c for _, c, _ in rows[i:i + 3])  # declarations may span lines
                name = re.search(r'TEXT\("([^"]+)"\)', window)
                decls.append((path.relative_to(SOURCE).as_posix(), number, m.group(1), name.group(1) if name else "?", guarded))
                if guarded:
                    guarded_vars[m.group(1)] = number
        for number, code, guarded in rows:
            for var, decl_line in guarded_vars.items():
                if number != decl_line and not guarded and re.search(r"\b%s\b" % var, code):
                    leaks.append((path.relative_to(SOURCE).as_posix(), number, var))
        del text
    return decls, leaks


class ShippingCVarGuards(unittest.TestCase):
    def test_exactly_the_six_kI168_controls_are_shipping_visible(self):
        decls, _ = census()
        visible = {name for _, _, _, name, guarded in decls if not guarded}
        self.assertEqual(visible, SHIPPING_VISIBLE)

    def test_census_size(self):
        decls, _ = census()
        self.assertEqual(len(decls), 52, decls)  # 6 Shipping-visible + 43 non-Shipping + 3 Development-only (2026-11-12)

    def test_no_guarded_cvar_is_referenced_from_shipping_code(self):
        _, leaks = census()
        self.assertEqual(leaks, [])


if __name__ == "__main__":
    unittest.main()
