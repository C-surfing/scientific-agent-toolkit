# Upstream Attribution and Licensing

## Principle

This repository curates metadata and installation logic. It does **not** claim authorship of upstream skills and does **not** relicense them.

The repository's own registry metadata and installer code are released under this repository's MIT license. Every upstream skill remains governed by its upstream license and third-party notices.

## Registry requirements

Every installable entry records:

- canonical upstream repository;
- installable subdirectory;
- upstream ref used for retrieval;
- SPDX license identifier;
- license verification status;
- attribution text / upstream project name;
- whether automatic installation is allowed.

If the license cannot be verified, set:

```json
{
  "license": {
    "spdx": "NOASSERTION",
    "status": "unverified"
  },
  "installable": false,
  "tier": "reference"
}
```

The installer must fail closed for such entries.

## What the installer records

For every successful installation it writes `_scientific_agent_toolkit_upstream.json` containing:

- upstream URL;
- requested ref;
- resolved commit SHA;
- upstream subdirectory;
- SPDX license;
- installation timestamp;
- registry ID.

When the upstream repository exposes a root `LICENSE`, `LICENSE.md`, `LICENSE.txt`, `COPYING`, or `NOTICE`, the installer copies it into `_UPSTREAM_NOTICES/` next to the installed skill.

## Vendoring policy

Default: **do not vendor upstream skill code into this repository**.

Reasons:

- keeps authorship boundaries obvious;
- avoids stale forks;
- makes upstream updates visible;
- reduces mixed-license ambiguity;
- allows resolved commit tracking during installation.

If a future version vendors or forks upstream code, that change must include:

1. explicit upstream license compatibility review;
2. preserved copyright/license notices;
3. a recorded upstream commit;
4. a list of local modifications;
5. a decision on whether changes should be contributed upstream.

## Reference-only projects

A reference link may be listed even when the upstream license is unclear, because linking and describing a public project is not the same as redistributing its source. The registry marks these entries `installable: false`, and the installer never clones them automatically.

## Data, figures, icons, and examples

A repository license does not automatically grant rights to every embedded paper figure, dataset, brand logo, screenshot, icon, or example. Third-party asset manifests and per-example attribution remain authoritative. Users must review those notices before publication or redistribution.

## Trademarks and venue names

Terms such as Nature, Science, IEEE, NeurIPS, or publisher names may describe formatting targets or styles. They do not imply endorsement, affiliation, or official compliance.
