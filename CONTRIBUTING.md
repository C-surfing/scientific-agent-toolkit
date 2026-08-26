# Contributing

Contributions should improve **coverage, routing, evidence, or maintenance**, not merely increase the number of listed skills.

## Proposing a skill

A proposal should include:

1. canonical GitHub repository;
2. exact installable Skill path;
3. license and evidence for it;
4. primary role and explicit non-goals;
5. supported outputs;
6. score breakdown using `docs/scoring.md`;
7. overlap analysis against existing Core skills;
8. at least two representative user tasks;
9. reasons it should be Core, Extension, Reference, or Experimental.

## Core admission

Core candidates must pass every hard gate in `docs/scoring.md`. Popularity is not a substitute for scientific integrity, provenance, or licensing.

## Registry changes

Run:

```bash
python3 scripts/validate_registry.py
python3 scripts/install.py --list
python3 scripts/install.py --tier core --dry-run
```

Do not silently change an upstream repository, path, license, or role. Explain such changes in the pull request.
