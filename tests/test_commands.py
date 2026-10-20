import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.build_config import build_from_text, download_text, write_atomic
from scripts.find_candidates import write_candidate_report
from scripts.rule_tools import active_rules, extract_section


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
            count = write_candidate_report(exported, upstream, target, anchor_size=1)
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
                "[General]\nipv6=false\n[Rule]\nDOMAIN,base.example,PROXY\n",
                "DOMAIN,mine.example,DIRECT\n",
                target,
            )
            self.assertIn(
                "DOMAIN,mine.example,DIRECT",
                target.read_text(encoding="utf-8"),
            )

    def test_build_adds_system_dns_and_private_answers_without_changing_proxy_dns(self):
        upstream = (
            "[General]\n"
            "dns-server = https://dns.example/dns-query\n"
            "ipv6 = false\n"
            "[Rule]\nDOMAIN,base.example,PROXY\nFINAL,DIRECT\n"
            "[MITM]\nhostname = *.example\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "output.conf"
            build_from_text(upstream, "DOMAIN,intranet.example,DIRECT\n", target)
            text = target.read_text(encoding="utf-8")

        general = extract_section(text, "General")
        self.assertIn("dns-direct-system = true", general)
        self.assertIn("private-ip-answer = true", general)
        self.assertIn("dns-server = https://dns.example/dns-query", general)
        self.assertIn("ipv6 = false", general)
        self.assertEqual(
            active_rules(extract_section(text, "Rule")),
            ["DOMAIN,intranet.example,DIRECT", "DOMAIN,base.example,PROXY", "FINAL,DIRECT"],
        )
        self.assertEqual(extract_section(text, "MITM"), ["hostname = *.example", ""])

    def test_build_overrides_upstream_disabling_intranet_support_once(self):
        upstream = (
            "[General]\n"
            "DNS-DIRECT-SYSTEM = false\n"
            "dns-direct-system = false\n"
            "private-ip-answer = false\n"
            "[Rule]\nDOMAIN,base.example,PROXY\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "output.conf"
            build_from_text(upstream, "", target)
            text = target.read_text(encoding="utf-8")

        general = extract_section(text, "General")
        settings = [line.strip() for line in general if line.strip()]
        self.assertEqual(
            settings,
            ["dns-direct-system = true", "private-ip-answer = true"],
        )

    def test_build_keeps_intranet_settings_stable_on_rebuild(self):
        upstream = "[General]\nipv6=false\n[Rule]\nDOMAIN,base.example,PROXY\n"
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "output.conf"
            build_from_text(upstream, "", target)
            first = target.read_text(encoding="utf-8")
            self.assertIn("dns-direct-system = true", extract_section(first, "General"))
            build_from_text(first, "", target)
            self.assertEqual(target.read_text(encoding="utf-8"), first)

    def test_missing_or_duplicate_general_preserves_existing_output(self):
        for upstream in (
            "[Rule]\nDOMAIN,base.example,PROXY\n",
            "[General]\nipv6=false\n[General]\nipv6=true\n[Rule]\nDOMAIN,base.example,PROXY\n",
        ):
            with self.subTest(upstream=upstream):
                with tempfile.TemporaryDirectory() as directory:
                    target = Path(directory) / "output.conf"
                    target.write_text("previous working config\n", encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "exactly one.*General"):
                        build_from_text(upstream, "", target)
                    self.assertEqual(
                        target.read_text(encoding="utf-8"),
                        "previous working config\n",
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
