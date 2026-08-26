#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "skills.json"
NOTICE_CANDIDATES = ["LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "NOTICE", "NOTICE.md"]

DESTINATIONS = {
    "codex": Path.home() / ".codex" / "skills",
    "claude": Path.home() / ".claude" / "skills",
    "generic": Path.home() / ".agents" / "skills",
}

def load_registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))["skills"]

def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def resolved_commit(repo_dir: Path) -> str:
    return run(["git", "rev-parse", "HEAD"], cwd=repo_dir).stdout.strip()

def copy_source(source: Path, target: Path):
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store"))

def install_one(skill, destination: Path, dry_run: bool, update: bool):
    sid = skill["id"]
    lic = skill["license"]
    if not skill["installable"]:
        raise RuntimeError(f"{sid} is reference/experimental only and cannot be auto-installed")
    if lic["status"] != "verified":
        raise RuntimeError(f"{sid} failed license gate: {lic['status']}")

    target = destination / sid
    if target.exists() and not update:
        print(f"SKIP {sid}: {target} exists (use --update)")
        return

    upstream = skill["upstream"]
    print(f"INSTALL {sid} <- {upstream['repo']}:{upstream['subdir']} @ {upstream['ref']}")
    if dry_run:
        return

    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="scientific-agent-toolkit-") as td:
        repo_dir = Path(td) / "repo"
        clone_cmd = ["git", "clone", "--depth", "1", "--filter=blob:none", "--branch", upstream["ref"], upstream["url"] + ".git", str(repo_dir)]
        run(clone_cmd)
        commit = resolved_commit(repo_dir)
        source = repo_dir if upstream["subdir"] == "." else repo_dir / upstream["subdir"]
        if not source.exists():
            raise RuntimeError(f"{sid}: upstream subdir not found: {upstream['subdir']}")
        copy_source(source, target)

        notice_dir = target / "_UPSTREAM_NOTICES"
        copied = []
        for name in NOTICE_CANDIDATES:
            p = repo_dir / name
            if p.is_file():
                notice_dir.mkdir(exist_ok=True)
                shutil.copy2(p, notice_dir / name)
                copied.append(name)

        provenance = {
            "registry_id": sid,
            "upstream_repo": upstream["repo"],
            "upstream_url": upstream["url"],
            "requested_ref": upstream["ref"],
            "resolved_commit": commit,
            "upstream_subdir": upstream["subdir"],
            "license_spdx": lic["spdx"],
            "license_status": lic["status"],
            "attribution": lic["attribution"],
            "copied_notices": copied,
            "installed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        (target / "_scientific_agent_toolkit_upstream.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
        (target / "UPSTREAM.md").write_text(
            f"# Upstream provenance\n\n- Project: {lic['attribution']}\n- Repository: {upstream['url']}\n- Ref requested: `{upstream['ref']}`\n- Commit installed: `{commit}`\n- Source path: `{upstream['subdir']}`\n- Declared license: `{lic['spdx']}`\n\nThis installed copy remains subject to the upstream license.\n",
            encoding="utf-8",
        )
        print(f"OK {sid}: {commit[:12]} -> {target}")

def select(skills, args):
    by_id = {s["id"]: s for s in skills}
    if args.skill:
        missing = [x for x in args.skill if x not in by_id]
        if missing:
            raise SystemExit("Unknown skill(s): " + ", ".join(missing))
        return [by_id[x] for x in args.skill]
    if args.tier == "all":
        return [s for s in skills if s["installable"]]
    return [s for s in skills if s["tier"] == args.tier and s["installable"]]

def main():
    parser = argparse.ArgumentParser(description="Install curated scientific Agent Skills from their canonical upstream repositories.")
    parser.add_argument("--list", action="store_true", help="list registry entries")
    parser.add_argument("--agent", choices=DESTINATIONS, default="generic")
    parser.add_argument("--dest", type=Path, help="override destination skill directory")
    parser.add_argument("--tier", choices=["core", "extension", "all"], default="core")
    parser.add_argument("--skill", nargs="+", help="install specific registry IDs")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--update", action="store_true", help="replace an existing installed copy")
    args = parser.parse_args()

    skills = load_registry()
    if args.list:
        for s in skills:
            gate = "installable" if s["installable"] else "reference-only"
            score = s.get("score", {}).get("total") if s.get("score") else "-"
            print(f"{s['id']:<30} {s['tier']:<12} {gate:<14} score={score}  {s['description']}")
        return

    destination = (args.dest or DESTINATIONS[args.agent]).expanduser().resolve()
    selected = select(skills, args)
    if not selected:
        raise SystemExit("No installable skills matched the selection")
    print(f"Destination: {destination}")
    for skill in selected:
        try:
            install_one(skill, destination, args.dry_run, args.update)
        except (RuntimeError, subprocess.CalledProcessError) as exc:
            print(f"ERROR {skill['id']}: {exc}", file=sys.stderr)
            raise SystemExit(1)

if __name__ == "__main__":
    main()
