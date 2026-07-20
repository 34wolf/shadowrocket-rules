# Shadowrocket Rules Repository Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a public, secret-free Shadowrocket rules repository that preserves individually confirmed custom rules and refreshes the Johnshall base configuration every day.

**Architecture:** Python standard-library tools isolate the `[Rule]` section, mark export-only lines as unclassified review candidates, validate confirmed public rules, and atomically merge them at the top of the upstream `[Rule]` section. GitHub Actions runs the same tested builder daily and commits only the generated public configuration.

**Tech Stack:** Python 3.9+ standard library, `unittest`, Git, GitHub Actions, Shadowrocket configuration format.

## Global Constraints

- Repository name: `shadowrocket-rules`; visibility: Public.
- `input/` and `.local/` are local-only and must never be tracked by Git.
- Analyze only the exported `[Rule]` section.
- Differences are unclassified candidates, never automatic personal rules.
- Every line added to `custom_rules.conf` requires individual confirmation and approval to publish.
- Never request or commit a GitHub password, Personal Access Token, node subscription, server password, certificate, or other secret.
- Explain immediately before overwriting, deleting, pushing, or publishing.
- Verified upstream URL: `https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_banlist_ad.conf`.
- Use Python standard-library modules only.
- Guide the beginner through one visible user action at a time and wait for the result.

## File Map

- `.gitignore`: blocks private exports, review reports, metadata, and temporary files.
- `AGENTS.md`: project safety and collaboration rules.
- `README.md`: public purpose, source attribution, and subscription instructions.
- `BEGINNER_GUIDE.md`: beginner maintenance guide.
- `custom_rules.conf`: confirmed public custom rules only.
- `scripts/rule_tools.py`: pure parsing, validation, comparison, and merge functions.
- `scripts/find_candidates.py`: local-only review-report command.
- `scripts/build_config.py`: downloader and atomic builder.
- `tests/`: standard-library automated tests.
- `.github/workflows/update.yml`: daily/manual updater.
- `output/my_shadowrocket.conf`: generated Mac/iPhone subscription.

---

### Task 1: Establish the privacy boundary and documentation

**Files:**
- Create: `.gitignore`
- Create: `AGENTS.md`
- Create: `README.md`
- Create: `BEGINNER_GUIDE.md`
- Create: `custom_rules.conf`

**Interfaces:**
- Consumes: existing local `input/lz.conf` without copying its contents.
- Produces: a verified ignore boundary before any public repository exists.

- [ ] **Step 1: Explain and replace the unpublished commit's Mac identity**

Explain that rewriting the one unpublished local commit removes the automatically generated Mac hostname from its author email. No file contents change and nothing is uploaded.

```bash
git config user.name "Shadowrocket Rules"
git config user.email "shadowrocket-rules@users.noreply.github.com"
git commit --amend --reset-author --no-edit
git remote -v
```

Expected: rewritten local commit; no remote output.

- [ ] **Step 2: Create the privacy files before staging anything**

Create `.gitignore` exactly as follows:

```gitignore
# Private Shadowrocket exports and local review data
input/
.local/

# Temporary files
*.tmp
*.part

# macOS and Python metadata
.DS_Store
__pycache__/
*.py[cod]
```

Create `custom_rules.conf` exactly as follows:

```conf
# Public custom Shadowrocket rules
# Add a rule only after individual review and explicit approval to publish it.
```

- [ ] **Step 3: Verify the private export is ignored**

```bash
git check-ignore -v input/lz.conf
git status --short --ignored
```

Expected: status shows `!! input/`; it must not show `?? input/lz.conf`.

- [ ] **Step 4: Create the public documentation**

Create `AGENTS.md` exactly as follows:

```markdown
# Project collaboration rules

- This public repository stores Shadowrocket routing rules only.
- Never track or publish `input/`, `.local/`, node subscriptions, server credentials, certificates, or passwords.
- Analyze only `[Rule]` from a local exported configuration.
- Treat every export/upstream difference as unclassified until the user reviews that exact line.
- Add a line to `custom_rules.conf` only after explicit approval to make it public.
- Explain before overwriting, deleting, pushing, or publishing a file.
- Guide a beginner through one visible action at a time and wait for the result.
```

Create `README.md` exactly as follows:

```markdown
# Shadowrocket Rules

This public repository keeps routing rules only. It does not contain proxy nodes, subscription URLs, server passwords, certificates, or private exported configurations.

## Files

- `custom_rules.conf`: individually reviewed public custom rules.
- `output/my_shadowrocket.conf`: generated Shadowrocket subscription.
- `scripts/`: tested Python standard-library build tools.

## Upstream

The base is Johnshall's public `sr_top500_banlist_ad.conf`:
https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_banlist_ad.conf

Custom rules are inserted immediately after `[Rule]`. GitHub Actions checks daily at 11:15 Beijing time and commits only changed output.

## Subscription

After publication, this section contains the exact Raw link verified from GitHub. The same configuration works on Mac and iPhone Shadowrocket.
```

Create `BEGINNER_GUIDE.md` exactly as follows:

```markdown
# Beginner Guide

## Safety first

The `input` folder is private and ignored by Git. Never drag `input/lz.conf` into GitHub or include its contents in screenshots.

## Public files

Only reviewed rules, scripts, documentation, tests, workflow, and generated output are public.

## Personal rules

Review one candidate line at a time. Confirm both that it is yours and that its full text is safe to publish before adding it to `custom_rules.conf`.

## Automatic updates

A green Actions check means tests and the build succeeded. A red cross means the previous working output remains available while the failure is investigated.
```

- [ ] **Step 5: Stage named public files and commit**

```bash
git add .gitignore AGENTS.md README.md BEGINNER_GUIDE.md custom_rules.conf
git diff --cached --name-only
git commit -m "chore: establish public rules safety boundary"
```

Expected: only the five named public files; no `input/` file.

---

### Task 2: Build and test the pure rule-processing core

**Files:**
- Create: `tests/test_rule_tools.py`
- Create: `scripts/rule_tools.py`

**Interfaces:**
- Consumes: UTF-8 configuration text and confirmed custom-rule text.
- Produces: `extract_section`, `find_candidates`, `public_rule_issue`, and `merge_custom_rules`.

- [ ] **Step 1: Write failing tests**

Create `tests/test_rule_tools.py` exactly as follows:

```python
import unittest

from scripts.rule_tools import extract_section, find_candidates, merge_custom_rules, public_rule_issue


class RuleToolsTests(unittest.TestCase):
    def test_extracts_only_rule_section(self):
        text = "[General]\nsecret=yes\n[Rule]\nDOMAIN,a.example,DIRECT\n[MITM]\npassword=no\n"
        self.assertEqual(extract_section(text, "Rule"), ["DOMAIN,a.example,DIRECT"])

    def test_missing_or_duplicate_rule_section_fails(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            extract_section("[General]\na=b\n", "Rule")
        duplicate = "[Rule]\nDOMAIN,a.example,DIRECT\n[Rule]\nDOMAIN,b.example,DIRECT\n"
        with self.assertRaisesRegex(ValueError, "exactly one"):
            extract_section(duplicate, "Rule")

    def test_differences_are_unclassified(self):
        exported = "[Rule]\nDOMAIN,my.example,DIRECT\nDOMAIN,shared.example,PROXY\n"
        upstream = "[Rule]\nDOMAIN,shared.example,PROXY\n"
        self.assertEqual(find_candidates(exported, upstream), [{"rule": "DOMAIN,my.example,DIRECT", "classification": "unclassified", "warning": ""}])

    def test_other_sections_never_become_candidates(self):
        exported = "[General]\nserver=secret\n[Rule]\nDOMAIN,shared.example,PROXY\n[MITM]\npassword=secret\n"
        upstream = "[Rule]\nDOMAIN,shared.example,PROXY\n"
        self.assertEqual(find_candidates(exported, upstream), [])

    def test_sensitive_and_terminal_rules_are_rejected(self):
        self.assertIn("URL", public_rule_issue("RULE-SET,https://private.example/list,PROXY"))
        self.assertIn("terminal", public_rule_issue("FINAL,PROXY"))
        self.assertIsNone(public_rule_issue("DOMAIN-SUFFIX,example.com,DIRECT"))

    def test_custom_rules_are_first_and_deduplicated(self):
        upstream = "[General]\nipv6=false\n[Rule]\nDOMAIN,base.example,PROXY\nDOMAIN,custom.example,DIRECT\n[MITM]\nenable=false\n"
        custom = "# reviewed\nDOMAIN,custom.example,DIRECT\nDOMAIN-SUFFIX,second.example,PROXY\n"
        merged = merge_custom_rules(upstream, custom)
        active = [line for line in extract_section(merged, "Rule") if line and not line.startswith("#")]
        self.assertEqual(active, ["DOMAIN,custom.example,DIRECT", "DOMAIN-SUFFIX,second.example,PROXY", "DOMAIN,base.example,PROXY"])
        self.assertIn("[MITM]\nenable=false", merged)

    def test_invalid_custom_rule_does_not_build(self):
        with self.assertRaisesRegex(ValueError, "not safe to publish"):
            merge_custom_rules("[Rule]\nDOMAIN,base.example,PROXY\n", "RULE-SET,https://private.example/list,PROXY\n")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify the expected import failure**

```bash
python3 -m unittest tests/test_rule_tools.py -v
```

Expected: failure because `scripts.rule_tools` does not exist.

- [ ] **Step 3: Implement `scripts/rule_tools.py`**

```python
"""Pure, secret-conscious Shadowrocket rule helpers."""

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
    starts = [i for i, line in enumerate(lines) if (_section_name(line) or "").casefold() == section.casefold()]
    if len(starts) != 1:
        raise ValueError(f"configuration must contain exactly one [{section}] section")
    start = starts[0] + 1
    end = next((i for i in range(start, len(lines)) if _section_name(lines[i]) is not None), len(lines))
    return lines[start:end]


def normalize_rule(line: str) -> str:
    return ",".join(part.strip() for part in line.strip().lstrip("\ufeff").split(","))


def active_rules(lines: List[str]) -> List[str]:
    return [normalize_rule(line) for line in lines if line.strip() and not line.strip().startswith(("#", ";"))]


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
        result.append({"rule": rule, "classification": "unclassified", "warning": public_rule_issue(rule) or ""})
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
    headers = [i for i, line in enumerate(lines) if (_section_name(line) or "").casefold() == "rule"]
    if len(headers) != 1:
        raise ValueError("configuration must contain exactly one [Rule] section")
    header = headers[0]
    end = next((i for i in range(header + 1, len(lines)) if _section_name(lines[i]) is not None), len(lines))
    filtered = []
    for line in lines[header + 1:end]:
        stripped = line.strip()
        if stripped and not stripped.startswith(("#", ";")) and normalize_rule(stripped) in seen:
            continue
        filtered.append(line)
    insertion = ["# Custom rules: individually reviewed and approved for publication", *custom, ""] if custom else []
    return "\n".join([*lines[:header + 1], *insertion, *filtered, *lines[end:]]).rstrip("\n") + "\n"
```

- [ ] **Step 4: Run tests and commit**

```bash
python3 -m unittest tests/test_rule_tools.py -v
git add scripts/rule_tools.py tests/test_rule_tools.py
git commit -m "feat: add safe Shadowrocket rule processing"
```

Expected: seven tests pass; commit contains two named files.

---

### Task 3: Add local candidate reporting and atomic output building

**Files:**
- Create: `tests/test_commands.py`
- Create: `scripts/find_candidates.py`
- Create: `scripts/build_config.py`

**Interfaces:**
- Consumes: local export, public upstream, and confirmed custom rules.
- Produces: ignored `.local/candidates.json` and atomically replaced public output.

- [ ] **Step 1: Write command-level failing tests**

Create `tests/test_commands.py` exactly as follows:

```python
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.build_config import build_from_text, download_text, write_atomic
from scripts.find_candidates import write_candidate_report


class CommandTests(unittest.TestCase):
    def test_report_contains_rule_differences_only(self):
        exported = "[General]\npassword=secret\n[Rule]\nDOMAIN,mine.example,DIRECT\nDOMAIN,base.example,PROXY\n[MITM]\npassword=secret\n"
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
            build_from_text("[Rule]\nDOMAIN,base.example,PROXY\n", "DOMAIN,mine.example,DIRECT\n", target)
            self.assertIn("DOMAIN,mine.example,DIRECT", target.read_text(encoding="utf-8"))

    @patch("scripts.build_config.urlopen")
    def test_download_rejects_empty_response(self, mocked_urlopen):
        mocked_urlopen.return_value.__enter__.return_value.read.return_value = b""
        with self.assertRaisesRegex(ValueError, "empty"):
            download_text("https://example.invalid/rules.conf")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify expected import failures**

```bash
python3 -m unittest tests/test_commands.py -v
```

Expected: failure because the command modules do not exist.

- [ ] **Step 3: Implement `scripts/find_candidates.py`**

```python
"""Create a local-only report from the exported [Rule] section."""

import argparse
import json
from pathlib import Path

from scripts.rule_tools import find_candidates


def write_candidate_report(export_text: str, upstream_text: str, target: Path) -> int:
    candidates = find_candidates(export_text, upstream_text)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(candidates)


def main() -> int:
    parser = argparse.ArgumentParser(description="Find unclassified Shadowrocket rule candidates")
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(".local/candidates.json"))
    args = parser.parse_args()
    count = write_candidate_report(
        args.export.read_text(encoding="utf-8-sig"),
        args.upstream.read_text(encoding="utf-8-sig"),
        args.output,
    )
    print(f"Wrote {count} unclassified candidates to the local review report.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Implement `scripts/build_config.py`**

```python
"""Download the public base and atomically build public output."""

import argparse
import os
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from scripts.rule_tools import merge_custom_rules


DEFAULT_UPSTREAM = "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/sr_top500_banlist_ad.conf"


def download_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "shadowrocket-rules-builder/1.0"})
    with urlopen(request, timeout=60) as response:
        data = response.read()
    if not data:
        raise ValueError("upstream response is empty")
    return data.decode("utf-8-sig")


def write_atomic(target: Path, text: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary_name, target)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def build_from_text(upstream_text: str, custom_text: str, target: Path) -> None:
    write_atomic(target, merge_custom_rules(upstream_text, custom_text))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a public Shadowrocket configuration")
    parser.add_argument("--upstream-url", default=DEFAULT_UPSTREAM)
    parser.add_argument("--custom", type=Path, default=Path("custom_rules.conf"))
    parser.add_argument("--output", type=Path, default=Path("output/my_shadowrocket.conf"))
    args = parser.parse_args()
    build_from_text(download_text(args.upstream_url), args.custom.read_text(encoding="utf-8-sig"), args.output)
    print(f"Built {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Run all tests and commit**

```bash
python3 -m unittest discover -s tests -v
git add scripts/find_candidates.py scripts/build_config.py tests/test_commands.py
git commit -m "feat: add local candidate report and atomic builder"
```

Expected: eleven tests pass; commit contains three named files.

---

### Task 4: Download current upstream and review candidates

**Files:**
- Create locally, ignored: `.local/sr_top500_banlist_ad.conf`
- Create locally, ignored: `.local/candidates.json`
- Modify after individual approval: `custom_rules.conf`

**Interfaces:**
- Consumes: `input/lz.conf`, verified Johnshall upstream, and user decisions.
- Produces: only individually approved public rules.

- [ ] **Step 1: Download upstream to the ignored local folder**

Use `scripts.build_config.download_text` to save the upstream to `.local/sr_top500_banlist_ad.conf`, then run:

```bash
git check-ignore -v .local/sr_top500_banlist_ad.conf
python3 -c 'from pathlib import Path; from scripts.rule_tools import extract_section; text=Path(".local/sr_top500_banlist_ad.conf").read_text(encoding="utf-8-sig"); print(len(extract_section(text, "Rule")))'
```

Expected: `.local/` is ignored and `[Rule]` is non-empty.

- [ ] **Step 2: Generate and verify the ignored candidate report**

```bash
python3 scripts/find_candidates.py --export input/lz.conf --upstream .local/sr_top500_banlist_ad.conf --output .local/candidates.json
git check-ignore -v .local/candidates.json
```

Expected: every record is labeled `unclassified`; the report is ignored.

- [ ] **Step 3: Review one candidate per user turn**

Show only the next candidate's `rule`, warning, and plain-language meaning. Ask for `保留并公开` or `跳过`, then wait. Never show adjacent export sections. Append the exact normalized line to `custom_rules.conf` only after `保留并公开` and a clean `public_rule_issue` result. URL-bearing or secret-like lines remain blocked unless the design is separately revised and approved.

- [ ] **Step 4: Validate and commit confirmed rules**

```bash
python3 -c 'from pathlib import Path; from scripts.rule_tools import active_rules, public_rule_issue, _lines; rules=active_rules(_lines(Path("custom_rules.conf").read_text(encoding="utf-8"))); assert all(public_rule_issue(rule) is None for rule in rules); print(f"Validated {len(rules)} confirmed public rules")'
git add custom_rules.conf
git diff --cached -- custom_rules.conf
git commit -m "feat: add individually confirmed custom rules"
```

Expected: only approved rules are staged; no `.local/` or `input/` path.

---

### Task 5: Generate and verify public output

**Files:**
- Create or replace after explanation: `output/my_shadowrocket.conf`

**Interfaces:**
- Consumes: current upstream and `custom_rules.conf`.
- Produces: complete public configuration with confirmed rules first.

- [ ] **Step 1: Explain the public output replacement and build**

Explain that only `output/my_shadowrocket.conf` is created or replaced and that `input/lz.conf` is never copied.

```bash
python3 scripts/build_config.py --custom custom_rules.conf --output output/my_shadowrocket.conf
```

Expected: `Built output/my_shadowrocket.conf`.

- [ ] **Step 2: Verify tests, ordering, and secret scan**

```bash
python3 -m unittest discover -s tests -v
python3 -c 'from pathlib import Path; from scripts.rule_tools import active_rules, extract_section, _lines; custom=active_rules(_lines(Path("custom_rules.conf").read_text(encoding="utf-8"))); output=active_rules(extract_section(Path("output/my_shadowrocket.conf").read_text(encoding="utf-8"), "Rule")); assert output[:len(custom)] == custom; print(f"Verified {len(custom)} custom rules first")'
git grep -n -i -E 'password=|authorization=|token=|ss://|vmess://|trojan://' -- output/my_shadowrocket.conf custom_rules.conf || true
```

Expected: tests pass, order passes, secret scan is empty.

- [ ] **Step 3: Commit named output only**

```bash
git add output/my_shadowrocket.conf
git diff --cached --name-only
git commit -m "build: generate Shadowrocket configuration"
```

Expected: only `output/my_shadowrocket.conf`.

---

### Task 6: Add the daily GitHub Actions workflow

**Files:**
- Create: `.github/workflows/update.yml`

**Interfaces:**
- Consumes: tested scripts, custom rules, and the public upstream URL.
- Produces: daily/manual builds that commit only changed public output.

- [ ] **Step 1: Create `.github/workflows/update.yml` exactly**

```yaml
name: Update Shadowrocket rules

on:
  schedule:
    - cron: "15 3 * * *"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: update-shadowrocket-rules
  cancel-in-progress: false

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.13"

      - name: Run tests
        run: python -m unittest discover -s tests -v

      - name: Build latest configuration
        run: python scripts/build_config.py --custom custom_rules.conf --output output/my_shadowrocket.conf

      - name: Commit changed public output
        shell: bash
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add -- output/my_shadowrocket.conf
          if git diff --cached --quiet; then
            echo "Upstream output is unchanged."
            exit 0
          fi
          git commit -m "build: update Shadowrocket rules"
          git push
```

- [ ] **Step 2: Run static safety checks and commit**

```bash
rg -n 'cron: "15 3 \* \* \*"|contents: write|git add -- output/my_shadowrocket.conf|actions/checkout@v6|actions/setup-python@v6' .github/workflows/update.yml
if rg -n 'git add \.|input/|\.local/' .github/workflows/update.yml; then exit 1; fi
git add .github/workflows/update.yml
git commit -m "ci: update Shadowrocket rules daily"
```

Expected: required lines found; forbidden scan empty; one named workflow committed.

---

### Task 7: Create the Public GitHub repository and upload safely

**Files:**
- Modify after GitHub shows the exact Raw URL: `README.md`

**Interfaces:**
- Consumes: audited local repository and user's signed-in GitHub session.
- Produces: Public `shadowrocket-rules` without password or token requests.

- [ ] **Step 1: Run final pre-publication audit**

```bash
git status --short --ignored
git ls-files
git remote -v
git log --format='%h %an | %ae'
```

Expected: `input/` and `.local/` ignored and absent from tracked files; no remote; no Mac hostname in commit emails.

- [ ] **Step 2: Guide creation one visible action at a time**

Tell the user to open `https://github.com/new`, name the repository `shadowrocket-rules`, choose Public, leave initialization checkboxes off, and click Create repository. Stop for a screenshot of the empty repository before any remote or push.

- [ ] **Step 3: Explain publication, connect, and push**

Read the exact HTTPS URL from the new repository page. Explain that the next action publishes every tracked file shown by `git ls-files`, while ignored `input/` and `.local/` remain on the Mac. Add that exact remote and push `main`. If authentication is required, use GitHub's private browser/device sign-in flow; never request credentials in chat.

- [ ] **Step 4: Record the exact Raw URL**

On GitHub, open `output/my_shadowrocket.conf`, click `Raw`, and copy the browser address. Add that exact verified URL to the README Subscription section, commit, and push. Do not invent the account name.

---

### Task 8: Verify Actions and subscriptions

**Files:**
- Modify only the smallest affected public file if verification proves an issue.

**Interfaces:**
- Consumes: published repository, Actions page, and exact Raw URL.
- Produces: verified automation and working Mac/iPhone subscriptions.

- [ ] **Step 1: Run GitHub Actions manually**

Guide the user to repository `Actions` → `Update Shadowrocket rules` → `Run workflow`. Wait for a screenshot showing a green check. On failure, use systematic debugging before changing files.

- [ ] **Step 2: Verify no-change behavior**

Run the workflow again without changing inputs. Expected: green check, log says `Upstream output is unchanged.`, and no extra build commit appears.

- [ ] **Step 3: Verify Mac subscription**

Guide one click at a time to add the exact Raw URL in Mac Shadowrocket without showing existing nodes. Expected: import succeeds and confirmed rules are first in `[Rule]`.

- [ ] **Step 4: Verify iPhone subscription**

Guide one tap at a time to add the same Raw URL in iPhone Shadowrocket. Ask only for a success/failure screenshot without nodes, private subscriptions, or passwords.

- [ ] **Step 5: Run final local verification**

```bash
python3 -m unittest discover -s tests -v
git status --short
if git ls-files | rg '^(input|\.local)/'; then exit 1; fi
```

Expected: tests pass, working tree clean, no private path tracked. Provide the exact verified Raw URL for both devices.
