# Scientific Agent Toolkit

> A curated, auditable registry of Agent Skills for scientific figures, research visualization, editable diagrams, and publication workflows.

[中文说明](README.zh-CN.md) · [Selection guide](docs/selection-guide.md) · [Benchmark](evals/README.md) · [Scoring](docs/scoring.md) · [Automation](docs/automation.md) · [Licensing](docs/licensing.md)

## Why this repository exists

Scientific visualization skills are easy to collect and hard to route correctly. A skill that makes a chart look better is not the same thing as a skill that decides whether a statistical encoding is scientifically valid; a model-architecture renderer should not be asked to reconstruct a PowerPoint figure; and a generative illustration pipeline should not silently replace data-grounded plots.

This repository is therefore **not an awesome-list and not a vendored bundle**. It is a curated registry with four goals:

1. **Route by scientific intent**, not by superficial visual similarity.
2. **Preserve data and topology semantics** before aesthetics.
3. **Prefer editable, reproducible deliverables** for publication work.
4. **Keep upstream authorship and licensing explicit**.

## v0.2: evidence for the curation

v0.1 established the registry, routing model, installer, licensing gates, and curator scores. v0.2 adds two independent evidence layers:

- **Benchmark/eval framework** — portable run manifests, artifact-contract checks, exact upstream commit provenance, a 40-point automated score, and a 60-point expert scientific-review rubric.
- **Upstream health + lockfile** — scheduled repository/ref/path/license checks and a stable `upstream-lock.json` that records the observed upstream commit without silently rewriting human curation policy.

Curator scores and benchmark scores are deliberately separate. A curator score evaluates whether a project belongs in this toolkit; a benchmark score evaluates a particular skill run on a particular case.

## Curated stack

### Core

| Skill | Primary role | Why it is core | Curator score |
|---|---|---|---:|
| `scientific-visualization` | Scientific integrity & publication QA | Cross-cutting rules for honest, accessible, publication-ready figures | 93 |
| `sci-plot` | Claim/evidence-driven figure design | Figure Contract, statistical semantics, create/revise/review/export routes | 95 |
| `paper-figures` | Manuscript + raw data → figures/tables | End-to-end reproducible statistics, chart selection, journal outputs | 91 |
| `chart-aesthetic-logic` | Improve an existing Python chart | Strong visual hierarchy and aesthetics without changing data semantics | 86 |
| `scientific-figure-design` | Create editable scientific diagrams | Claim-first Draw.io/SVG/PDF pipeline with deterministic validation | 94 |
| `ml-architecture-diagram` | Model code → faithful architecture diagram | Architecture IR and topology fidelity before publication abstraction | 96 |
| `sci-diagram-pptx` | Reference figure → editable PowerPoint | Faithful native PPTX reconstruction with explicit topology | 90 |

### Extensions and references

| Skill/project | Status | Use it when |
|---|---|---|
| `huitu` / Scientific Illustration | Extension | Materials science, electrochemistry, spectroscopy, DFT-specific plots |
| `matplotlib-skill` | Reference | You want a compact opinionated matplotlib pattern library; overlaps with core aesthetics skills |
| `figures4papers` | Reference-only | You want a strong corpus of real publication figure scripts; upstream license is not explicit enough for automatic installation |
| `science-plot-formatter` | Reference-only | You want venue-oriented formatting ideas; no clear root license was found during curation |
| PaperBanana | Experimental reference | You want generative academic-illustration exploration; not the default path for data-grounded or topology-critical figures |

Curator scores are not benchmark claims. See [docs/scoring.md](docs/scoring.md) and [evals/README.md](evals/README.md).

## Routing: choose by intent

```text
Need a research visual
│
├─ Evidence is encoded by data, axes, scales, statistics?
│  ├─ Whole manuscript + raw data → paper-figures
│  ├─ Design/revise/audit scientific evidence → sci-plot
│  ├─ Existing chart mainly needs visual refinement → chart-aesthetic-logic
│  └─ Final scientific/publication QA → scientific-visualization
│
├─ Meaning is encoded by nodes, arrows, modules, topology?
│  ├─ General method/framework/pipeline → scientific-figure-design
│  ├─ Architecture must be recovered from model code → ml-architecture-diagram
│  └─ Existing reference image must become native PPTX → sci-diagram-pptx
│
└─ Domain-specific materials-science measurements → huitu (extension)
```

A single task may use a **primary skill + one QA skill**, but avoid stacking several authoring skills on the same artifact unless there is a clear handoff. See the [selection matrix](docs/selection-guide.md).

## Benchmark

The benchmark is agent-agnostic: it evaluates delivered artifacts, not a particular model vendor.

```bash
# validate benchmark contracts
python3 scripts/eval_runner.py --validate

# create a portable run manifest
python3 scripts/eval_runner.py \
  --init-run claim-to-data-figure sci-plot \
  --output eval-results/sci-plot/run.json

# score after artifacts/provenance and expert review have been recorded
python3 scripts/eval_runner.py --score eval-results/sci-plot/run.json
```

Automated checks account for 40 points; expert review accounts for 60. If expert review is incomplete, the runner reports `needs-human-review` instead of fabricating a total score.

See [evals/README.md](evals/README.md).

## Upstream health and reproducibility lock

```bash
GITHUB_TOKEN=... python3 scripts/check_upstreams.py \
  --output /tmp/upstream-health.json \
  --fail-on-critical

python3 scripts/update_upstream_lock.py \
  --health /tmp/upstream-health.json
```

`skills.json` remains human-curated policy. `upstream-lock.json` records stable machine observations such as the resolved commit, observed license, archived state, and source subdirectory. Transient API failures are `unknown`, not false evidence of breakage.

A weekly GitHub workflow opens/refreshes an automation PR **only when meaningful lock content changes**. It never silently merges an upstream upgrade or rewrites curator scores. See [docs/automation.md](docs/automation.md).

## Install

The installer pulls directly from upstream repositories and writes provenance metadata into each installed skill. It does **not** vendor upstream code into this registry.

```bash
# list curated skills
python3 scripts/install.py --list

# install the recommended core set for Codex
python3 scripts/install.py --agent codex --tier core

# install selected skills for Claude Code
python3 scripts/install.py --agent claude --skill sci-plot chart-aesthetic-logic

# preview only
python3 scripts/install.py --agent codex --tier core --dry-run
```

Convenience wrappers:

```bash
./scripts/install.sh --agent codex --tier core
```

```powershell
./scripts/install.ps1 --agent claude --tier core
```

Default destinations:

- Codex: `~/.codex/skills`
- Claude Code: `~/.claude/skills`
- Generic Agent Skills: `~/.agents/skills`

The installer never installs a registry entry whose license gate is unresolved.

## Repository layout

```text
scientific-agent-toolkit/
├── README.md
├── README.zh-CN.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── CONTRIBUTING.md
├── registry/
│   ├── skills.json
│   └── upstream-lock.json
├── schema/
│   └── skill.schema.json
├── evals/
│   ├── README.md
│   ├── benchmark.json
│   └── result.schema.json
├── docs/
│   ├── selection-guide.md
│   ├── scoring.md
│   ├── automation.md
│   └── licensing.md
├── scripts/
│   ├── install.py
│   ├── eval_runner.py
│   ├── check_upstreams.py
│   ├── update_upstream_lock.py
│   └── validate_registry.py
└── .github/workflows/
    ├── validate.yml
    └── upstream-health.yml
```

## Curation hard gates

A project can be excellent and still stay out of the installable registry. Automatic installation requires:

- a clearly identified upstream repository and installable skill path;
- an explicit license compatible with redistribution/use of the upstream material;
- a stable scientific role that is not merely a duplicate of an existing core skill;
- no silent replacement of data-grounded evidence with generated pixels;
- enough source/editability/provenance to make the output reviewable;
- a documented workflow, not just a style prompt.

Unknown license → **reference-only**, regardless of popularity.

## Licensing model

This registry's own code and metadata are MIT licensed. **Upstream skills are not relicensed by this repository.** Each installed skill remains under its upstream license. The installer records the upstream URL, resolved commit SHA, declared SPDX license, and copies the upstream license notice when available.

See [docs/licensing.md](docs/licensing.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Contributing

New candidates should improve role coverage rather than just increase the count. Submit metadata, evidence for the license, a scoring breakdown, and a routing rationale. Benchmark contributions should add a reproducible case contract rather than only a screenshot of a good result. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Disclaimer

This is an independent curation project and is not affiliated with the upstream authors, OpenAI, Anthropic, any journal, conference, or publisher. Researchers remain responsible for checking scientific accuracy, statistical validity, journal requirements, copyright, and attribution before publication.
