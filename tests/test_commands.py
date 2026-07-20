import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.build_config import build_from_text, download_text, write_atomic
from scripts.find_candidates import write_candidate_report


class CommandTests(unittest.TestCase):
    def test_candidate_report_contains_rule_differences_only(self):
        exported = (
            "[General]\npassword=secret\n"
            "[Rule]\nDOMAIN,mine.example,DIRECT\nDOMAIN,base.example,PROXY\n"
            "[MITM]\npassword=secret\n"
        )
        upstream = "[Rule]\nDOMAIN,base.example,PROXY\n"
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "candidates.json"
            count = write_candidate_report(exported, upstream, target)
            data = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(count, 1)
        self.assertEqual(data[0]["rule"], "DOMAIN,mine.example,DIRECT")
        self.assertNotIn("secret", json.dumps(data))

    def test_failed_build_preserves_old_output(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "output.conf"
            target.write_text("old\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                build_from_text("[General]\na=b\n", "", target)
            self.assertEqual(target.read_text(encoding="utf-8"), "old\n")

    def test_successful_build_replaces_output(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "output.conf"
            write_atomic(target, "old\n")
            build_from_text(
                "[Rule]\nDOMAIN,base.example,PROXY\n",
                "DOMAIN,mine.example,DIRECT\n",
                target,
            )
            self.assertIn(
                "DOMAIN,mine.example,DIRECT",
                target.read_text(encoding="utf-8"),
            )

    @patch("scripts.build_config.urlopen")
    def test_download_rejects_empty_response(self, mocked_urlopen):
        mocked_urlopen.return_value.__enter__.return_value.read.return_value = b""
        with self.assertRaisesRegex(ValueError, "empty"):
            download_text("https://example.invalid/rules.conf")

    @patch("scripts.build_config.urlopen")
    def test_download_decodes_utf8_bom(self, mocked_urlopen):
        mocked_urlopen.return_value.__enter__.return_value.read.return_value = (
            b"\xef\xbb\xbf[Rule]\nDOMAIN,base.example,PROXY\n"
        )
        self.assertTrue(
            download_text("https://example.invalid/rules.conf").startswith("[Rule]")
        )


if __name__ == "__main__":
    unittest.main()
