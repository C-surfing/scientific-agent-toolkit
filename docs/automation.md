# Upstream Health and Registry Update Automation

v0.2 separates **human curation** from **machine observation**.

## Two layers

### `registry/skills.json`

Human-curated policy and routing:

- tier and category
- intended role
- installability
- declared license status
- curator score
- routing guidance

Automation must not silently promote/demote a skill or change a curation score.

### `registry/upstream-lock.json`

Machine-observed, reproducibility-oriented state:

- resolved commit SHA for the configured ref
- observed repository license
- archived state
- latest repository push timestamp
- configured subdirectory and whether it exists

The lockfile intentionally excludes volatile fields such as `checked_at`, star count, issue count, or popularity metrics. A scheduled check should not create a pull request merely because time passed.

## Health states

`check_upstreams.py` reports four states:

- **healthy** — declared upstream identity/ref/path are available and no policy issue was found.
- **warning** — non-fatal concern, such as long inactivity for a reference entry.
- **critical** — evidence of a broken or unsafe declared upstream relationship.
- **unknown** — the check could not establish facts because of transient API/network/rate-limit problems.

Only a critical condition on an **installable** entry becomes a hard CI failure. `unknown` is never treated as evidence that an upstream is broken.

## Hard integrity failures

For an installable skill, examples include:

- repository no longer exists
- configured ref no longer resolves
- configured skill subdirectory disappeared
- repository became archived
- a repository-level license disappeared after the registry marked it verified
- observed SPDX license conflicts with the verified declared SPDX license

These conditions require human review before the registry should advance.

## Run locally

```bash
GITHUB_TOKEN=... python3 scripts/check_upstreams.py \
  --output /tmp/upstream-health.json \
  --markdown /tmp/upstream-health.md \
  --fail-on-critical

python3 scripts/update_upstream_lock.py \
  --health /tmp/upstream-health.json \
  --lock registry/upstream-lock.json
```

`update_upstream_lock.py` preserves the previous lock entry when the latest observation is `unknown`. A temporary API outage therefore cannot erase provenance.

## Scheduled GitHub workflow

The scheduled workflow:

1. checks every registry upstream using `GITHUB_TOKEN`;
2. fails without modifying policy when an installable entry has a critical integrity problem;
3. produces a Markdown health summary in the workflow run;
4. updates only stable fields in `upstream-lock.json`;
5. opens or refreshes `automation/upstream-lock` only when meaningful lock content changed.

The automation does **not** automatically merge that pull request. A changed upstream commit is observable evidence, not permission to upgrade blindly.

## Why not automatically rewrite `skills.json`?

A newer upstream commit can change behavior, dependencies, licensing details, or skill scope. Updating the lock is safe observation; changing curation policy requires review. This is the same reason the installer records exact resolved commits at installation time.
