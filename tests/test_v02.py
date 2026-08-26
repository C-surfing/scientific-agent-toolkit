from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


health = load_script("check_upstreams")
evals = load_script("eval_runner")


class UpstreamHealthTests(unittest.TestCase):
    def entry(self, declared_license="MIT"):
        return {
            "id": "demo",
            "tier": "core",
            "installable": True,
            "upstream": {"repo": "owner/repo", "ref": "main", "subdir": "skills/demo"},
            "license": {"spdx": declared_license, "status": "verified"},
        }

    def healthy_api(self, url: str):
        if url.endswith("/repos/owner/repo"):
            return {
                "archived": False,
                "default_branch": "main",
                "pushed_at": datetime.now(timezone.utc).isoformat(),
                "license": {"spdx_id": "MIT"},
            }
        if "/commits/" in url:
            return {"sha": "a" * 40}
        if "/contents/" in url:
            return {"type": "dir"}
        raise AssertionError(url)

    def test_healthy_installable_entry(self):
        with patch.object(health, "gh_get", side_effect=self.healthy_api):
            result = health.check_entry(self.entry(), 365)
        self.assertEqual(result["state"], "healthy")
        self.assertFalse(result["hard_failure"])
        self.assertEqual(result["resolved_commit"], "a" * 40)
        self.assertTrue(result["subdir_exists"])

    def test_verified_license_mismatch_is_hard_failure(self):
        with patch.object(health, "gh_get", side_effect=self.healthy_api):
            result = health.check_entry(self.entry("Apache-2.0"), 365)
        self.assertEqual(result["state"], "critical")
        self.assertTrue(result["hard_failure"])
        self.assertTrue(any("license mismatch" in issue for issue in result["issues"]))

    def test_transient_repository_error_is_unknown_not_failure(self):
        with patch.object(health, "gh_get", side_effect=health.GitHubError(403, "rate limited")):
            result = health.check_entry(self.entry(), 365)
        self.assertEqual(result["state"], "unknown")
        self.assertFalse(result["hard_failure"])


class BenchmarkTests(unittest.TestCase):
    def test_perfect_manifest_scores_100(self):
        benchmark = evals.load_json(ROOT / "evals" / "benchmark.json")
        self.assertEqual(evals.validate_benchmark(benchmark), [])
        manifest = evals.init_manifest(benchmark, "claim-to-data-figure", "sci-plot")
        manifest["provenance"]["upstream_commit"] = "b" * 40
        manifest["human_scores"] = {
            "scientific_correctness": 5,
            "evidence_fidelity": 5,
            "visual_clarity": 5,
            "editability_reproducibility": 5,
            "accessibility": 5,
        }
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for name in ("figure.svg", "source.py", "contract.json"):
                (base / name).write_text("{}" if name.endswith(".json") else "test", encoding="utf-8")
            manifest["artifacts"] = [
                {"role": "figure", "path": "figure.svg"},
                {"role": "source", "path": "source.py"},
                {"role": "figure-contract", "path": "contract.json"},
            ]
            manifest_path = base / "run.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            scored = evals.score_manifest(benchmark, manifest_path)
        self.assertEqual(scored["status"], "complete")
        self.assertEqual(scored["automated_score"], 40.0)
        self.assertEqual(scored["human_score"], 60.0)
        self.assertEqual(scored["total_score"], 100.0)


if __name__ == "__main__":
    unittest.main()
