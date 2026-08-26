#!/usr/bin/env python3
"""Update registry/upstream-lock.json from a health report.

Only stable upstream observations are stored. Transient/unknown checks preserve the
previous lock entry so a temporary API outage cannot erase provenance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = ROOT / "registry" / "upstream-lock.json"


def load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--health", type=Path, required=True)
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    args = parser.parse_args()

    health = load(args.health, None)
    if not health:
        raise SystemExit("health report is missing or empty")
    current = load(args.lock, {"schema_version": "1.0.0", "entries": {}})
    previous = current.get("entries", {})
    updated: dict[str, Any] = dict(previous)

    for entry in health.get("entries", []):
        if entry.get("state") == "unknown" or not entry.get("resolved_commit"):
            continue
        updated[entry["id"]] = {
            "repo": entry["repo"],
            "ref": entry["ref"],
            "resolved_commit": entry["resolved_commit"],
            "observed_license": entry.get("observed_license", "NOASSERTION"),
            "archived": bool(entry.get("archived")),
            "pushed_at": entry.get("pushed_at"),
            "subdir": entry.get("subdir", "."),
            "subdir_exists": entry.get("subdir_exists")
        }

    result = {
        "schema_version": "1.0.0",
        "source": "scripts/check_upstreams.py",
        "entries": {key: updated[key] for key in sorted(updated)}
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    old = args.lock.read_text(encoding="utf-8") if args.lock.exists() else ""
    if rendered == old:
        print("UPSTREAM_LOCK_UNCHANGED")
        return 0
    args.lock.parent.mkdir(parents=True, exist_ok=True)
    args.lock.write_text(rendered, encoding="utf-8")
    print(f"UPSTREAM_LOCK_UPDATED entries={len(result['entries'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
