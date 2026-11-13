import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BOSS_DOCS_DIR = REPO_ROOT / "Documentation" / "Boss"


class BhA13SfxDiskBytesContractTest(unittest.TestCase):
    def test_active_sfx_and_voice_specs_resolve_non_zero_uassets(self) -> None:
        doc_paths = [
            BOSS_DOCS_DIR / "BB_A05_SFX_BLOCKED_ON_OWNER_PICKS.md",
            BOSS_DOCS_DIR / "BB_A11_A13_SEVAROG_CARD_SFX_SPEC.md",
            BOSS_DOCS_DIR / "BB_A14_SEVAROG_VOICE_BARKS_SPEC.md",
            BOSS_DOCS_DIR / "SFX_03_AUDITION_MANIFEST.md",
        ]
        doc_paths.extend(sorted(BOSS_DOCS_DIR.glob("SFX_0[5-9]*.md")))
        doc_paths.extend(sorted(BOSS_DOCS_DIR.glob("SFX_1[0-2]*.md")))

        audio_markers = (
            "Sound",
            "Cue",
            "Wavs",
            "Audio",
            "Voice",
            "ParagonSevarog/Characters/Heroes/Sevarog/Sounds",
            "Dialogue",
        )
        asset_refs: set[str] = set()
        for doc in doc_paths:
            self.assertTrue(doc.is_file(), f"Missing SFX spec doc: {doc}")
            text = doc.read_text(encoding="utf-8")
            for match in re.findall(r"/Game/[A-Za-z0-9_/\-]+", text):
                cleaned = match.rstrip("/")
                if cleaned.endswith("/Sounds"):
                    continue
                if any(marker in cleaned for marker in audio_markers):
                    asset_refs.add(cleaned)

        self.assertGreaterEqual(len(asset_refs), 100)
        missing = []
        for asset_path in sorted(asset_refs):
            rel = asset_path.replace("/Game/", "Content/") + ".uasset"
            uasset = REPO_ROOT / rel
            if not (uasset.is_file() and uasset.stat().st_size > 0):
                missing.append(asset_path)

        self.assertEqual(missing, [], f"Unresolved/empty SFX or voice .uassets: {missing}")


if __name__ == "__main__":
    unittest.main()
