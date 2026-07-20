"""Download the public base and atomically build public Shadowrocket output."""

import argparse
import os
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from scripts.rule_tools import merge_custom_rules


DEFAULT_UPSTREAM = (
    "https://johnshall.github.io/Shadowrocket-ADBlock-Rules-Forever/"
    "sr_top500_banlist_ad.conf"
)


def download_text(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "shadowrocket-rules-builder/1.0"},
    )
    with urlopen(request, timeout=60) as response:
        data = response.read()
    if not data:
        raise ValueError("upstream response is empty")
    return data.decode("utf-8-sig")


def write_atomic(target: Path, text: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=target.name + ".",
        suffix=".tmp",
        dir=target.parent,
    )
    try:
        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as handle:
            handle.write(text)
        os.replace(temporary_name, target)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def build_from_text(upstream_text: str, custom_text: str, target: Path) -> None:
    merged = merge_custom_rules(upstream_text, custom_text)
    write_atomic(target, merged)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a public Shadowrocket configuration"
    )
    parser.add_argument("--upstream-url", default=DEFAULT_UPSTREAM)
    parser.add_argument(
        "--custom",
        type=Path,
        default=Path("custom_rules.conf"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/my_shadowrocket.conf"),
    )
    args = parser.parse_args()

    upstream = download_text(args.upstream_url)
    custom = args.custom.read_text(encoding="utf-8-sig")
    build_from_text(upstream, custom, args.output)
    print(f"Built {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
