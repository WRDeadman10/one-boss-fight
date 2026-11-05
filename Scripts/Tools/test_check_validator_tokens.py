"""Synthetic edge cases for the offline FrameworkProof token extractor."""
import tempfile
import unittest
from pathlib import Path

from check_validator_tokens import emitted_tokens, strip_cpp_comments


class ValidatorTokenExtractionTests(unittest.TestCase):
    def test_multiline_text_macro_and_repeat_are_collected_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / "sample.cpp").write_text(
                'UE_LOG(LogTemp, Display,\n TEXT("[FrameworkProof] wrapped first=%d"), 1);\n'
                'UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] wrapped first=%d"), 2);\n',
                encoding="utf-8")
            self.assertEqual(emitted_tokens(source), {"wrapped"})

    def test_macro_nested_format_argument_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / "sample.cpp").write_text(
                'UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] macro_wrapped value=%s"), *FString(TEXT("x")));',
                encoding="utf-8")
            self.assertEqual(emitted_tokens(source), {"macro_wrapped"})

    def test_comments_do_not_create_false_emissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / "sample.cpp").write_text(
                '// UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] line_comment"));\n'
                '/* UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] block_comment")); */\n'
                'UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] real"));\n',
                encoding="utf-8")
            self.assertEqual(emitted_tokens(source), {"real"})

    def test_comment_markers_inside_string_are_preserved(self):
        source = 'UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] slash value=//"));'
        stripped = strip_cpp_comments(source)
        self.assertIn('value=//', stripped)


if __name__ == "__main__":
    unittest.main()
