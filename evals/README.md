# Benchmark / Eval Framework

The benchmark is intentionally agent-agnostic. It evaluates the artifacts produced by a skill rather than coupling the repository to one model or coding-agent vendor.

## Score model

A completed run is scored out of 100:

- **40 automated points**: required artifact contracts and upstream commit provenance.
- **60 expert-review points**: scientific correctness, evidence fidelity, visual clarity, editability/reproducibility, and accessibility.

This separation is deliberate: machine-checkable facts should be automated, while scientific meaning and visual communication should not be reduced to a cosmetic model score.

## Validate the benchmark

```bash
python3 scripts/eval_runner.py --validate
```

## Start a run

```bash
python3 scripts/eval_runner.py \
  --init-run claim-to-data-figure sci-plot \
  --output eval-results/sci-plot/claim-to-data-figure/run.json
```

The generated manifest records the selected case, skill, provenance fields, artifact paths, and the five human-review dimensions.

After the skill/agent has produced outputs, add artifact entries such as:

```json
{
  "role": "figure",
  "path": "artifacts/figure.svg"
}
```

Record the exact upstream skill commit in `provenance.upstream_commit`. This is required for a complete automated score.

## Score a run

```bash
python3 scripts/eval_runner.py \
  --score eval-results/sci-plot/claim-to-data-figure/run.json
```

If human scores are still `null`, the result status is `needs-human-review` and no misleading 100-point total is emitted.

Each human dimension uses a 0–5 score. The benchmark converts those values into their weighted contribution only after all dimensions are completed.

## Aggregate completed runs

```bash
python3 scripts/eval_runner.py --aggregate eval-results/
```

Aggregation reports run count, mean, minimum, and maximum by skill. Do not compare skills across unrelated cases without also reporting the case mix.

## Benchmark cases

The v0.2 benchmark provides one contract for each Core responsibility:

- final scientific figure QA → `scientific-visualization`
- claim/evidence → data figure → `sci-plot`
- manuscript + raw data → figure/table package → `paper-figures`
- existing semantically-correct chart refinement → `chart-aesthetic-logic`
- editable research framework diagram → `scientific-figure-design`
- model code/config topology recovery → `ml-architecture-diagram`
- scientific reference diagram → editable PowerPoint → `sci-diagram-pptx`

The benchmark does **not** claim that these seven cases are a complete scientific-visualization benchmark. They establish a reproducible baseline that can be extended with real datasets, adversarial cases, venue constraints, and domain-specific extensions.
