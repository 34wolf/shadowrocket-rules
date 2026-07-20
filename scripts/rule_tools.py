"""Pure, secret-conscious helpers for Shadowrocket rule configurations."""

from __future__ import annotations

import re
from typing import Dict, List, Optional


SECTION_RE = re.compile(r"^\s*\[([^]]+)]\s*$")
SENSITIVE_MARKERS = ("://", "token=", "password=", "authorization=", "secret=")


def _lines(text: str) -> List[str]:
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def _section_name(line: str) -> Optional[str]:
    match = SECTION_RE.match(line)
    return match.group(1) if match else None


def extract_section(text: str, section: str) -> List[str]:
    lines = _lines(text)
    starts = [
        index
        for index, line in enumerate(lines)
        if (_section_name(line) or "").casefold() == section.casefold()
    ]
    if len(starts) != 1:
        raise ValueError(f"configuration must contain exactly one [{section}] section")

    start = starts[0] + 1
    end = next(
        (
            index
            for index in range(start, len(lines))
            if _section_name(lines[index]) is not None
        ),
        len(lines),
    )
    return lines[start:end]


def normalize_rule(line: str) -> str:
    return ",".join(
        part.strip() for part in line.strip().lstrip("\ufeff").split(",")
    )


def active_rules(lines: List[str]) -> List[str]:
    return [
        normalize_rule(line)
        for line in lines
        if line.strip() and not line.strip().startswith(("#", ";"))
    ]


def public_rule_issue(rule: str) -> Optional[str]:
    normalized = normalize_rule(rule)
    lowered = normalized.casefold()
    if any(marker in lowered for marker in SENSITIVE_MARKERS):
        return "contains a URL or secret-like parameter"

    parts = normalized.split(",")
    if parts[0].upper() in {"FINAL", "MATCH"}:
        return "terminal rules cannot be published as a personal override"
    if len(parts) < 3:
        return "rule must contain type, value, and policy"
    return None


def find_candidates(export_text: str, upstream_text: str) -> List[Dict[str, str]]:
    exported = active_rules(extract_section(export_text, "Rule"))
    upstream = set(active_rules(extract_section(upstream_text, "Rule")))
    result = []
    seen = set()

    for rule in exported:
        if rule in upstream or rule in seen:
            continue
        seen.add(rule)
        result.append(
            {
                "rule": rule,
                "classification": "unclassified",
                "warning": public_rule_issue(rule) or "",
            }
        )
    return result


def merge_custom_rules(upstream_text: str, custom_text: str) -> str:
    custom = []
    seen = set()
    for rule in active_rules(_lines(custom_text)):
        issue = public_rule_issue(rule)
        if issue:
            raise ValueError(f"custom rule is not safe to publish: {issue}")
        if rule not in seen:
            seen.add(rule)
            custom.append(rule)

    lines = _lines(upstream_text)
    headers = [
        index
        for index, line in enumerate(lines)
        if (_section_name(line) or "").casefold() == "rule"
    ]
    if len(headers) != 1:
        raise ValueError("configuration must contain exactly one [Rule] section")

    header = headers[0]
    end = next(
        (
            index
            for index in range(header + 1, len(lines))
            if _section_name(lines[index]) is not None
        ),
        len(lines),
    )
    filtered = []
    for line in lines[header + 1 : end]:
        stripped = line.strip()
        if (
            stripped
            and not stripped.startswith(("#", ";"))
            and normalize_rule(stripped) in seen
        ):
            continue
        filtered.append(line)

    insertion = (
        [
            "# Custom rules: individually reviewed and approved for publication",
            *custom,
            "",
        ]
        if custom
        else []
    )
    merged = [*lines[: header + 1], *insertion, *filtered, *lines[end:]]
    return "\n".join(merged).rstrip("\n") + "\n"
