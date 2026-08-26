#!/usr/bin/env python3
"""Agent-agnostic benchmark manifest validator and scorer.

The runner deliberately does not execute a particular coding agent. It scores the
portable output contract after any agent/skill has produced artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BENCHMARK = ROOT / "evals" / "benchmark.json"
COMMIT_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def validate_benchmark(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "1.0.0":
        errors.append("unsupported benchmark schema_version")
    scoring = data.get("scoring", {})
    if scoring.get("automated_max") != 40 or scoring.get("human_max") != 60:
        errors.append("benchmark scoring must remain 40 automated + 60 human")
    dims = scoring.get("human_dimensions", [])
    if sum(d.get("weight", 0) for d in dims) != 60:
        errors.append("human dimension weights must total 60")
    dim_ids = [d.get("id") for d in dims]
    if len(dim_ids) != len(set(dim_ids)):
        errors.append("human dimension ids must be unique")
    cases = data.get("cases", [])
    case_ids = [c.get("id") for c in cases]
    if not cases:
        errors.append("benchmark must define cases")
    if len(case_ids) != len(set(case_ids)):
        errors.append("case ids must be unique")
    for case in cases:
        if not case.get("candidate_skills"):
            errors.append(f"{case.get('id')}: candidate_skills is empty")
        if not case.get("required_artifacts"):
            errors.append(f"{case.get('id')}: required_artifacts is empty")
        for req in case.get("required_artifacts", []):
            if not req.get("role") or not req.get("extensions"):
                errors.append(f"{case.get('id')}: artifact requirement must include role/extensions")
    return errors


def find_case(benchmark: dict[str, Any], case_id: str) -> dict[str, Any]:
    for case in benchmark["cases"]:
        if case["id"] == case_id:
            return case
    raise SystemExit(f"Unknown case: {case_id}")


def init_manifest(benchmark: dict[str, Any], case_id: str, skill_id: str) -> dict[str, Any]:
    case = find_case(benchmark, case_id)
    if skill_id not in case["candidate_skills"]:
        raise SystemExit(f"{skill_id} is not a declared candidate for {case_id}")
    return {
        "schema_version": "1.0.0",
        "benchmark_id": benchmark["benchmark_id"],
        "case_id": case_id,
        "skill_id": skill_id,
        "provenance": {"upstream_commit": "", "agent": "", "model": ""},
        "artifacts": [],
        "human_scores": {d["id"]: None for d in benchmark["scoring"]["human_dimensions"]},
        "notes": ""
    }


def artifact_pass(req: dict[str, Any], artifacts: list[dict[str, Any]], base_dir: Path) -> tuple[bool, str]:
    role = req["role"]
    candidates = [a for a in artifacts if a.get("role") == role and a.get("path")]
    if not candidates:
        return False, f"missing role {role}"
    allowed = {ext.lower() for ext in req["extensions"]}
    for artifact in candidates:
        rel = Path(artifact["path"])
        full = rel if rel.is_absolute() else base_dir / rel
        if full.exists() and full.suffix.lower() in allowed:
            return True, str(full)
    return False, f"no existing {role} artifact with allowed extension {sorted(allowed)}"


def score_manifest(benchmark: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if manifest.get("benchmark_id") != benchmark["benchmark_id"]:
        raise SystemExit("manifest benchmark_id does not match benchmark")
    case = find_case(benchmark, manifest.get("case_id", ""))
    if manifest.get("skill_id") not in case["candidate_skills"]:
        raise SystemExit("manifest skill_id is not a candidate for this case")

    requirements = case["required_artifacts"]
    per_requirement = 30.0 / len(requirements)
    automated_details = []
    automated = 0.0
    for req in requirements:
        passed, detail = artifact_pass(req, manifest.get("artifacts", []), manifest_path.parent)
        if passed:
            automated += per_requirement
        automated_details.append({"role": req["role"], "passed": passed, "detail": detail})

    commit = manifest.get("provenance", {}).get("upstream_commit", "")
    provenance_ok = bool(COMMIT_RE.fullmatch(commit))
    if provenance_ok:
        automated += 10.0
    automated_details.append({"check": "upstream_commit", "passed": provenance_ok, "detail": commit or "missing"})

    human_total = 0.0
    human_complete = True
    human_details = []
    supplied = manifest.get("human_scores", {})
    for dim in benchmark["scoring"]["human_dimensions"]:
        raw = supplied.get(dim["id"])
        if raw is None:
            human_complete = False
            human_details.append({"id": dim["id"], "score": None, "weighted": None})
            continue
        if not isinstance(raw, (int, float)) or raw < 0 or raw > 5:
            raise SystemExit(f"human score {dim['id']} must be in [0, 5]")
        weighted = dim["weight"] * float(raw) / 5.0
        human_total += weighted
        human_details.append({"id": dim["id"], "score": raw, "weighted": round(weighted, 2)})

    total = automated + human_total if human_complete else None
    return {
        "benchmark_id": benchmark["benchmark_id"],
        "case_id": case["id"],
        "skill_id": manifest["skill_id"],
        "automated_score": round(automated, 2),
        "automated_max": 40,
        "human_score": round(human_total, 2) if human_complete else None,
        "human_max": 60,
        "total_score": round(total, 2) if total is not None else None,
        "status": "complete" if human_complete else "needs-human-review",
        "automated_details": automated_details,
        "human_details": human_details
    }


def aggregate(directory: Path) -> dict[str, Any]:
    records = []
    for path in sorted(directory.rglob("*.score.json")):
        data = load_json(path)
        if data.get("total_score") is not None:
            records.append(data)
    by_skill: dict[str, list[float]] = {}
    for record in records:
        by_skill.setdefault(record["skill_id"], []).append(float(record["total_score"]))
    return {
        "completed_runs": len(records),
        "skills": {
            skill: {
                "runs": len(values),
                "mean": round(statistics.fmean(values), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2)
            }
            for skill, values in sorted(by_skill.items())
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--init-run", nargs=2, metavar=("CASE_ID", "SKILL_ID"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--score", type=Path)
    parser.add_argument("--aggregate", type=Path)
    args = parser.parse_args()

    benchmark = load_json(args.benchmark)
    errors = validate_benchmark(benchmark)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if args.validate:
        print(f"BENCHMARK_VALID cases={len(benchmark['cases'])}")
    if args.init_run:
        if not args.output:
            raise SystemExit("--init-run requires --output")
        dump_json(args.output, init_manifest(benchmark, args.init_run[0], args.init_run[1]))
        print(args.output)
    if args.score:
        scored = score_manifest(benchmark, args.score)
        output = args.output or args.score.with_suffix(".score.json")
        dump_json(output, scored)
        print(json.dumps(scored, indent=2))
    if args.aggregate:
        summary = aggregate(args.aggregate)
        if args.output:
            dump_json(args.output, summary)
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
