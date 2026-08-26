#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "skills.json"

WEIGHTS = {
    "scientific_integrity": 20,
    "reproducibility": 15,
    "workflow_quality": 15,
    "editability_outputs": 10,
    "qa_evals": 10,
    "interoperability": 10,
    "maintenance": 10,
    "licensing": 5,
    "scope_uniqueness": 5,
}

def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)

def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ids = set()
    for skill in data["skills"]:
        sid = skill["id"]
        if sid in ids:
            fail(f"duplicate id: {sid}")
        ids.add(sid)
        lic = skill["license"]
        if skill["installable"] and lic["status"] != "verified":
            fail(f"{sid}: installable skill must have license.status=verified")
        if skill["installable"] and lic["spdx"] in {"NOASSERTION", "NONE", ""}:
            fail(f"{sid}: installable skill must have an SPDX license")
        if skill["tier"] in {"core", "extension"} and not skill["installable"]:
            fail(f"{sid}: core/extension must be installable")
        score = skill.get("score")
        if score:
            computed = sum(score[k] for k in WEIGHTS)
            if computed != score["total"]:
                fail(f"{sid}: score total={score['total']} but computed={computed}")
            for key, maximum in WEIGHTS.items():
                if not 0 <= score[key] <= maximum:
                    fail(f"{sid}: {key} out of range")
    print(f"OK: {len(ids)} registry entries validated")

if __name__ == "__main__":
    main()
