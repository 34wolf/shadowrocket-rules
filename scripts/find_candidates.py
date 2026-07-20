"""Create a local-only report from an exported Shadowrocket [Rule] section."""

import argparse
import json
from pathlib import Path

from scripts.rule_tools import find_candidates


def write_candidate_report(
    export_text: str,
    upstream_text: str,
    target: Path,
    anchor_size: int = 10,
) -> int:
    candidates = find_candidates(export_text, upstream_text, anchor_size=anchor_size)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(candidates, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(candidates)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find unclassified Shadowrocket rule candidates"
    )
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".local/candidates.json"),
    )
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
