#!/usr/bin/env python3
"""Check upstream repositories declared in registry/skills.json.

Uses only the Python standard library and the GitHub REST API. Automatic failure is
restricted to installable entries with hard integrity failures; transient API/rate
limit errors are reported as unknown rather than treated as evidence of breakage.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "registry" / "skills.json"


class GitHubError(RuntimeError):
    def __init__(self, status: int | None, message: str):
        super().__init__(message)
        self.status = status


def gh_get(url: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "scientific-agent-toolkit-health-checker"
    }
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise GitHubError(exc.code, f"HTTP {exc.code}: {body}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise GitHubError(None, str(exc)) from exc


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def repo_api(repo: str, suffix: str = "") -> str:
    return f"https://api.github.com/repos/{repo}{suffix}"


def is_transient(status: int | None) -> bool:
    return status is None or status in {403, 429, 500, 502, 503, 504}


def check_entry(entry: dict[str, Any], max_stale_days: int) -> dict[str, Any]:
    upstream = entry["upstream"]
    repo = upstream["repo"]
    ref = upstream.get("ref", "main")
    subdir = upstream.get("subdir", ".")
    result: dict[str, Any] = {
        "id": entry["id"],
        "tier": entry["tier"],
        "installable": bool(entry.get("installable")),
        "repo": repo,
        "ref": ref,
        "subdir": subdir,
        "state": "healthy",
        "hard_failure": False,
        "issues": []
    }

    try:
        meta = gh_get(repo_api(repo))
    except GitHubError as exc:
        if is_transient(exc.status):
            result.update(state="unknown", issues=[f"repository check unavailable: {exc}"])
        else:
            result.update(state="critical" if entry.get("installable") else "warning", issues=[f"repository unavailable: {exc}"])
            result["hard_failure"] = bool(entry.get("installable"))
        return result

    result["archived"] = bool(meta.get("archived"))
    result["default_branch"] = meta.get("default_branch")
    result["pushed_at"] = meta.get("pushed_at")
    observed_license = ((meta.get("license") or {}).get("spdx_id") or "NOASSERTION")
    result["observed_license"] = observed_license

    pushed = parse_time(meta.get("pushed_at"))
    if pushed:
        age_days = (datetime.now(timezone.utc) - pushed).days
        result["stale_days"] = age_days
        if age_days > max_stale_days:
            result["issues"].append(f"no repository push for {age_days} days")
            result["state"] = "warning"
    if meta.get("archived"):
        result["issues"].append("repository is archived")
        result["state"] = "critical" if entry.get("installable") else "warning"
        result["hard_failure"] = bool(entry.get("installable"))

    declared = entry.get("license", {})
    declared_spdx = declared.get("spdx", "NOASSERTION")
    declared_status = declared.get("status", "unverified")
    if entry.get("installable") and declared_status.startswith("verified"):
        if observed_license in {None, "", "NOASSERTION"}:
            result["issues"].append(f"verified installable entry declares {declared_spdx}, but GitHub reports no repository license")
            result["state"] = "critical"
            result["hard_failure"] = True
        elif declared_spdx != observed_license:
            result["issues"].append(f"license mismatch: registry={declared_spdx}, upstream={observed_license}")
            result["state"] = "critical"
            result["hard_failure"] = True

    ref_q = urllib.parse.quote(ref, safe="")
    try:
        commit = gh_get(repo_api(repo, f"/commits/{ref_q}"))
        result["resolved_commit"] = commit.get("sha")
    except GitHubError as exc:
        if is_transient(exc.status):
            result["issues"].append(f"ref check unavailable: {exc}")
            if result["state"] == "healthy":
                result["state"] = "unknown"
        else:
            result["issues"].append(f"ref does not resolve: {exc}")
            result["state"] = "critical" if entry.get("installable") else "warning"
            result["hard_failure"] = bool(entry.get("installable"))

    if subdir not in {"", "."}:
        path_q = "/".join(urllib.parse.quote(part, safe="") for part in subdir.split("/"))
        try:
            gh_get(repo_api(repo, f"/contents/{path_q}?ref={urllib.parse.quote(ref, safe='')}"))
            result["subdir_exists"] = True
        except GitHubError as exc:
            if is_transient(exc.status):
                result["subdir_exists"] = None
                result["issues"].append(f"subdir check unavailable: {exc}")
                if result["state"] == "healthy":
                    result["state"] = "unknown"
            else:
                result["subdir_exists"] = False
                result["issues"].append(f"declared subdir is missing: {subdir}")
                result["state"] = "critical" if entry.get("installable") else "warning"
                result["hard_failure"] = bool(entry.get("installable"))
    else:
        result["subdir_exists"] = True

    return result


def collect(registry_path: Path, max_stale_days: int) -> dict[str, Any]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    entries = [check_entry(entry, max_stale_days) for entry in registry["skills"]]
    counts = {state: sum(1 for e in entries if e["state"] == state) for state in ["healthy", "warning", "critical", "unknown"]}
    counts["hard_failures"] = sum(1 for e in entries if e.get("hard_failure"))
    return {
        "schema_version": "1.0.0",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "registry_schema_version": registry.get("schema_version"),
        "summary": counts,
        "entries": entries
    }


def markdown(report: dict[str, Any]) -> str:
    s = report["summary"]
    lines = [
        "## Upstream health",
        "",
        f"Healthy: **{s['healthy']}** · Warning: **{s['warning']}** · Critical: **{s['critical']}** · Unknown: **{s['unknown']}** · Hard failures: **{s['hard_failures']}**",
        "",
        "| Skill | Tier | State | Commit | License | Notes |",
        "|---|---|---|---|---|---|"
    ]
    for entry in report["entries"]:
        commit = (entry.get("resolved_commit") or "—")[:12]
        license_name = entry.get("observed_license") or "—"
        notes = "; ".join(entry.get("issues", [])) or "OK"
        notes = notes.replace("|", "\\|")
        lines.append(f"| `{entry['id']}` | {entry['tier']} | **{entry['state']}** | `{commit}` | {license_name} | {notes} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown", type=Path)
    parser.add_argument("--max-stale-days", type=int, default=365)
    parser.add_argument("--fail-on-critical", action="store_true")
    args = parser.parse_args()

    report = collect(args.registry, args.max_stale_days)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = markdown(report)
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(md, encoding="utf-8")
    print(md, end="")
    if args.fail_on_critical and report["summary"]["hard_failures"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
