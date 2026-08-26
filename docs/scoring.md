# Curation and Scoring

The score is a **curator score**, not an objective benchmark or claim of superiority. It is used to make inclusion decisions explainable and repeatable.

## Hard gates

A candidate cannot be `core` or automatically installable unless all applicable hard gates pass:

1. **License identified** — explicit repository/skill license with an SPDX identifier or equivalent clear grant.
2. **Upstream identified** — canonical repository and installable source path are known.
3. **Scientific integrity** — the default workflow does not silently alter data meaning, statistics, axes, uncertainty, or topology.
4. **Role clarity** — the skill has a distinct primary job; it is not included merely as another style prompt.
5. **Reviewability** — output has adequate source, provenance, editability, or reproducibility for its role.

A failed license gate always makes the candidate `reference-only`, regardless of score or popularity.

## 100-point rubric

| Criterion | Weight | What earns a high score |
|---|---:|---|
| Scientific / semantic integrity | 20 | Explicit safeguards for data, statistics, claims, topology, missing data, uncertainty |
| Reproducibility & provenance | 15 | Runnable sources, deterministic steps, manifests, resolved versions/commits |
| Agent workflow quality | 15 | Clear triggers, routes, failure modes, handoffs, deliverable contract |
| Editability & publication outputs | 10 | SVG/PDF/Draw.io/native PPTX/source code; final-size awareness |
| QA / tests / evals | 10 | Render inspection, validators, tests, eval datasets, fail-closed checks |
| Interoperability / portability | 10 | Standard Skill packaging, Codex/Claude/generic compatibility, modest host assumptions |
| Maintenance signal | 10 | Recent activity, coherent repository, tests/docs, non-archived status |
| Licensing clarity | 5 | SPDX license and third-party attribution handled cleanly |
| Scope uniqueness | 5 | Adds a distinct capability instead of duplicating an existing core role |

## Tier policy

- **Core**: normally ≥ 85, all hard gates pass, and role coverage is important.
- **Extension**: normally ≥ 78, all hard gates pass, but domain-specific or non-default.
- **Reference**: useful ideas/examples but overlap, portability, or licensing prevents default installation.
- **Experimental**: promising workflow with higher semantic/reproducibility risk for final scientific artifacts.

Scores do not automatically determine tier. A strong but redundant tool may stay Reference; a narrowly domain-specific tool may be Extension even with a high score.

## Current curated scores

| ID | Integrity | Repro | Workflow | Editable | QA | Interop | Maint. | License | Unique | Total | Tier |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| ml-architecture-diagram | 20 | 15 | 14 | 10 | 10 | 9 | 9 | 5 | 4 | **96** | Core |
| sci-plot | 20 | 15 | 15 | 9 | 10 | 9 | 8 | 5 | 4 | **95** | Core |
| scientific-figure-design | 19 | 15 | 14 | 10 | 10 | 8 | 9 | 5 | 4 | **94** | Core |
| scientific-visualization | 20 | 14 | 14 | 9 | 9 | 10 | 9 | 5 | 3 | **93** | Core |
| paper-figures | 19 | 15 | 14 | 9 | 8 | 9 | 8 | 5 | 4 | **91** | Core |
| sci-diagram-pptx | 19 | 14 | 14 | 10 | 9 | 8 | 7 | 5 | 4 | **90** | Core |
| chart-aesthetic-logic | 18 | 13 | 13 | 8 | 9 | 9 | 7 | 5 | 4 | **86** | Core |
| huitu | 18 | 13 | 12 | 9 | 8 | 7 | 7 | 5 | 5 | **84** | Extension |

Reference/experimental projects are intentionally not ranked as if they had passed all hard gates.
