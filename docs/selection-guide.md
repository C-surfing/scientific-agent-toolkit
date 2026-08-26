# Skill Selection Guide

## The rule: route by evidence carrier

The fastest reliable routing question is:

> **What carries the scientific meaning of this artifact?**

- **Axes, scales, data geometry, uncertainty, statistics** → data-figure route.
- **Nodes, arrows, modules, causal/processing topology** → diagram route.
- **A reference visual whose structure must survive into PowerPoint** → reconstruction route.

## Selection matrix

| Task | Primary | Optional QA/handoff | Avoid as default |
|---|---|---|---|
| Design a new evidence-driven scientific plot | `sci-plot` | `scientific-visualization` | Diagram generators |
| Turn manuscript + CSV/XLSX into figures/tables | `paper-figures` | `scientific-visualization` | Pure aesthetic skills as first step |
| Improve an already-correct matplotlib/seaborn chart | `chart-aesthetic-logic` | `scientific-visualization` | Recomputing statistics without need |
| Audit a figure for statistical/scientific validity | `sci-plot` | `scientific-visualization` | Aesthetics-only review |
| Create a method overview/framework/pipeline | `scientific-figure-design` | manual scientific review | Data-plot skills |
| Draw ML architecture from actual code/config | `ml-architecture-diagram` | `scientific-figure-design` only for paper-wide style alignment | Inventing unknown internals |
| Rebuild a screenshot/framework as editable PPTX | `sci-diagram-pptx` | manual semantic comparison | Redesigning instead of reconstructing |
| Materials/electrochemistry/spectroscopy plot | `huitu` | `scientific-visualization` | General wrapper if domain semantics matter |
| Explore generative academic illustration concepts | PaperBanana (reference) | deterministic rebuild before final publication | Treating generated raster as authoritative evidence |

## Recommended handoffs

### Data figure

```text
paper-figures OR sci-plot
          ↓
scientific-visualization QA
          ↓
chart-aesthetic-logic (only if visual refinement is still needed)
```

Do not automatically run all three. `chart-aesthetic-logic` is a refinement route, not a mandatory postprocessor.

### Scientific diagram

```text
scientific-figure-design
          ↓
editable draw.io / SVG / PDF
          ↓
manual scientific review
```

### ML architecture

```text
model code/config
      ↓
ml-architecture-diagram
      ↓
Architecture IR + topology review
      ↓
editable publication artifact
```

### Reference image → PowerPoint

```text
reference image/PDF
      ↓
sci-diagram-pptx
      ↓
native shapes + text + connectors
      ↓
render/structure comparison
```

## Conflict resolution

When two skills both appear applicable, use this precedence:

1. **Semantic fidelity** beats aesthetics.
2. **Domain-specific semantics** beat generic style wrappers.
3. **Source recovery** beats visual inference when source code/config exists.
4. **Editable deterministic output** beats generated raster for final scientific artifacts.
5. **Primary authoring skill + one QA skill** beats multi-skill authoring chains.

## Why some good projects remain references

A high-quality project can remain reference-only because of:

- unclear licensing;
- very high overlap with an existing core role;
- no portable Agent Skill package;
- outputs that are useful for ideation but not authoritative scientific evidence;
- insufficient provenance/editability for a default publication workflow.
