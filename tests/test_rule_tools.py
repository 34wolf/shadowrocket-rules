import unittest

from scripts.rule_tools import (
    active_rules,
    extract_section,
    find_candidates,
    merge_custom_rules,
    public_rule_issue,
)


class RuleToolsTests(unittest.TestCase):
    def test_extracts_only_requested_section(self):
        text = (
            "[General]\nsecret=yes\n"
            "[Rule]\nDOMAIN,a.example,DIRECT\n"
            "[MITM]\npassword=no\n"
        )
        self.assertEqual(
            extract_section(text, "Rule"),
            ["DOMAIN,a.example,DIRECT"],
        )

    def test_missing_section_fails(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            extract_section("[General]\na=b\n", "Rule")

    def test_duplicate_section_fails(self):
        duplicate = (
            "[Rule]\nDOMAIN,a.example,DIRECT\n"
            "[Rule]\nDOMAIN,b.example,DIRECT\n"
        )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            extract_section(duplicate, "Rule")

    def test_differences_are_unclassified(self):
        exported = (
            "[Rule]\n"
            "DOMAIN,my.example,DIRECT\n"
            "DOMAIN,shared.example,PROXY\n"
        )
        upstream = "[Rule]\nDOMAIN,shared.example,PROXY\n"
        self.assertEqual(
            find_candidates(exported, upstream),
            [
                {
                    "rule": "DOMAIN,my.example,DIRECT",
                    "classification": "unclassified",
                    "warning": "",
                }
            ],
        )

    def test_non_rule_sections_never_become_candidates(self):
        exported = (
            "[General]\nserver=secret\n"
            "[Rule]\nDOMAIN,shared.example,PROXY\n"
            "[MITM]\npassword=secret\n"
        )
        upstream = "[Rule]\nDOMAIN,shared.example,PROXY\n"
        self.assertEqual(find_candidates(exported, upstream), [])

    def test_sensitive_url_rule_is_flagged(self):
        self.assertIn(
            "URL",
            public_rule_issue("RULE-SET,https://private.example/list,PROXY"),
        )

    def test_terminal_rule_is_flagged(self):
        self.assertIn("terminal", public_rule_issue("FINAL,PROXY"))

    def test_normal_public_rule_is_allowed(self):
        self.assertIsNone(public_rule_issue("DOMAIN-SUFFIX,example.com,DIRECT"))

    def test_active_rules_normalizes_spacing_and_ignores_comments(self):
        self.assertEqual(
            active_rules(["# note", "", " DOMAIN-SUFFIX, example.com , DIRECT "]),
            ["DOMAIN-SUFFIX,example.com,DIRECT"],
        )

    def test_custom_rules_are_first_and_deduplicated(self):
        upstream = (
            "[General]\nipv6=false\n"
            "[Rule]\n"
            "DOMAIN,base.example,PROXY\n"
            "DOMAIN,custom.example,DIRECT\n"
            "[MITM]\nenable=false\n"
        )
        custom = (
            "# reviewed\n"
            "DOMAIN,custom.example,DIRECT\n"
            "DOMAIN-SUFFIX,second.example,PROXY\n"
            "DOMAIN,custom.example,DIRECT\n"
        )
        merged = merge_custom_rules(upstream, custom)
        active = active_rules(extract_section(merged, "Rule"))
        self.assertEqual(
            active,
            [
                "DOMAIN,custom.example,DIRECT",
                "DOMAIN-SUFFIX,second.example,PROXY",
                "DOMAIN,base.example,PROXY",
            ],
        )
        self.assertIn("[MITM]\nenable=false", merged)

    def test_invalid_custom_rule_does_not_build(self):
        with self.assertRaisesRegex(ValueError, "not safe to publish"):
            merge_custom_rules(
                "[Rule]\nDOMAIN,base.example,PROXY\n",
                "RULE-SET,https://private.example/list,PROXY\n",
            )


if __name__ == "__main__":
    unittest.main()
