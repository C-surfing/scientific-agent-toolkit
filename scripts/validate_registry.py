#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "skills.json"
LOCK = ROOT / "registry" / "upstream-lock.json"
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")

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
    by_id = {}
    for skill in data["skills"]:
        sid = skill["id"]
        if sid in ids:
            fail(f"duplicate id: {sid}")
        ids.add(sid)
        by_id[sid] = skill
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

    lock_entries = {}
    if LOCK.exists():
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        if lock.get("schema_version") != "1.0.0":
            fail("unsupported upstream-lock schema_version")
        lock_entries = lock.get("entries", {})
        for sid, observed in lock_entries.items():
            if sid not in by_id:
                fail(f"upstream-lock contains unknown skill: {sid}")
            declared = by_id[sid]["upstream"]
            for field in ("repo", "ref", "subdir"):
                if observed.get(field) != declared.get(field):
                    fail(f"{sid}: lock {field} does not match registry")
            commit = observed.get("resolved_commit", "")
            if not SHA_RE.fullmatch(commit):
                fail(f"{sid}: lock resolved_commit must be a full 40-char SHA")

    print(f"OK: {len(ids)} registry entries validated; lock entries={len(lock_entries)}")

if __name__ == "__main__":
    main()
