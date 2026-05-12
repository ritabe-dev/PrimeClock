# PRC v2.5 Deferred Review Resolution v0.1

Status: source-only planning note for the v2.5 research line. This is not a
candidate package, public release, DOI artifact, or public theorem claim.

## Purpose

Resolve the review items that were repeatedly deferred during v2.3 candidate
and v2.3.0 public review. The goal is to prevent v2.5 from becoming a grab bag
of old requests. Each item is assigned to one of four buckets:

```text
absorbed by v2.4 bridge
v2.5 core
v2.5 support
v2.6+ / paper-prep
```

## Decisions

| Review item | Resolution | Rationale |
| --- | --- | --- |
| Residual-gap transition graph and genealogy | absorbed by v2.4 bridge | v2.4 now has source-only transition graphs, sibling controls, lineage atlas, and checkers. v2.5 may reuse the idea only by recomputing and restating it under v2.5 artifacts. |
| Signed phase-margin separator | v2.5 support | It is the useful finite diagnostic inherited from v2.4, but should support obstruction and prediction rather than act as the whole v2.5 headline. |
| Obstruction classification | v2.5 core | This is the strongest next research question: why capacity-satisfied families fail to close. |
| Feature ablation and prediction | v2.5 core | This turns finite diagnostics into a forward-looking research line and can guide later targeted higher-layer probes. |
| Residual dynamics grammar | v2.5 core | Transition itineraries should be compressed into reusable lineage features instead of staying as raw CSV summaries. |
| Static figures | v2.5 support | v2.4 generated source-only figures. v2.5 should regenerate only the figures needed for the selected candidate story. |
| CSV schema documentation | v2.5 support, candidate blocker if packaged | External reviewers need explicit column/type documentation for any v2.5 candidate CSVs. |
| Focused pytest/checker coverage | v2.5 support, candidate blocker if packaged | Every v2.5 artifact needs a small checker path and focused pytest before candidate packaging. |
| Related-work expansion | paper-prep | Useful before a manuscript-style release, but not required to decide the v2.5 finite mechanism. |
| Single-gap heuristic for B5/B6/B7 | v2.5 support only | Keep as explanatory background. Do not make it the v2.5 headline or claim a general all-births theorem. |
| `k=6` critical-radius spectrum | v2.6+ | Helpful but orthogonal to obstruction/prediction. Do not let it block v2.5 Gate R. |
| Piecewise-envelope independent oracle | v2.6+ | Valuable verification hardening for critical-radius exactness, but not required for the v2.5 residual-dynamics line. |
| Full null model | v2.6+ | A lightweight baseline may be useful in v2.5, but a full null model is too broad for the next slice. |
| B8 / larger-layer experiments | v2.6+ targeted probe | Do not brute-force B8 before v2.5 has a predictor or high-potential family ranking. |
| `research/experiments/` path cleanup | v2.6+ | Moving public module paths is a packaging refactor, not a research blocker. |
| `setup.py` / PEP 517 cleanup | v2.6+ | Packaging cleanup should not distract from v2.5 Gate R. |
| `tools.py` splitting and `__init__.py` API cleanup | v2.6+ | Worth doing after the next research interface stabilizes. |
| mypy / strict typing expansion | v2.6+ | Useful engineering hardening, but not the next research decision. |

## v2.5 Core Scope

The v2.5 Gate R line should focus on three connected questions:

```text
1. Obstruction classification:
   Why do capacity-satisfied sibling families fail to close?

2. Feature ablation / prediction:
   Which features are actually needed to rank close-prone lineages?

3. Residual dynamics grammar:
   Which transition itineraries summarize close and non-close behavior?
```

The expected v2.5 artifact shape is:

```text
candidate_workflow_v2_5_v0_1.yml
data/prc_v2_5_obstruction_classes_v0_1.csv
data/prc_v2_5_feature_ablation_v0_1.csv
data/prc_v2_5_lineage_grammar_v0_1.csv
check_v2_5_obstruction_classification.py
check_v2_5_feature_ablation.py
notes/prc_v2_5_research_review_note_v0_1.md
```

## Non-Claims

This resolution note does not claim:

- a v2.5 candidate package;
- a public v2.4 theorem;
- a B8 result;
- an asymptotic or prime-distribution theorem;
- that signed phase margin alone is the final research story;
- that all future births are single-gap births.

## Decision

continue research
