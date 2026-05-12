# PRC v2.4 Transition Graph Probes v0.1

Status: source-only Gate R diagnostic for the v2.4 research line. This note is
not a candidate package, public release note, or public claim.

## Scope

The goal is to check whether the row-level transition vocabulary

```text
miss / trim / split / partial_close / close
```

continues to carry useful structure after the initial B5 pilot. The labels
describe geometry. The `is_birth` flag remains a separate historical event:
`close` means residual extinction, while `birth` means first coverage at the
new layer.

This slice adds:

```text
B5 -> B6 full transition graph
B6 -> B7 birth-neighborhood probe
B6 -> B7 full transition graph
sibling-lift phase controls
transition itinerary non-birth controls
```

## B5 To B6 Full Graph

The full graph uses every uncovered `k=5` parent residue and every `q=13`
lift:

```text
rows = 29562 = 2274 uncovered C5 parents * 13 lifts
```

Primary taxonomy:

```text
miss          = 20442
trim          = 5610
split         = 3090
partial_close = 378
close         = 42
```

Component delta breakdown:

```text
miss + delta 0          = 20442
trim + delta 0          = 5610
split + delta +1        = 3090
partial_close + delta -1 = 378
close + delta -1        = 42
```

All `close` rows match the checked B6 birth rows, and there are no non-birth
`close` rows in this graph.

The B5-to-B6 genealogy flow gives one useful diagnostic: B6 births come from
B5 parents that were either `miss + delta 0` or `trim + delta 0` in the B5
pilot, not from B5 `partial_close` or `split + delta +1` rows.

```text
B5 miss + delta 0 -> B6 close = 18
B5 trim + delta 0 -> B6 close = 24
```

This is not yet a theorem; it is a candidate pattern for the Gate R story.

## B7 Birth-Neighborhood Probe

The B7 probe only uses B7 birth parent residues and all `q=17` lifts:

```text
rows = 12138 = 714 B7 birth parents * 17 lifts
```

Primary taxonomy:

```text
miss          = 11424
trim          = 0
split         = 0
partial_close = 0
close         = 714
```

Component delta breakdown:

```text
miss + delta 0   = 11424
close + delta -1 = 714
```

All `close` rows match the checked B7 birth rows, and there are no non-birth
`close` rows in this restricted neighborhood.

## B6 To B7 Full Graph

The full graph uses every uncovered `k=6` parent residue and every `q=17`
lift:

```text
rows = 501840 = 29520 uncovered B6 parents * 17 lifts
```

Primary taxonomy:

```text
miss          = 363600
trim          = 78310
split         = 54490
partial_close = 4726
close         = 714
```

Component delta breakdown:

```text
miss + delta 0           = 363600
trim + delta 0           = 78310
split + delta +1         = 54490
partial_close + delta -1 = 4726
close + delta -1         = 714
```

All `close` rows match the checked B7 birth rows, and there are no non-birth
`close` rows in the full graph.

## Sibling And Itinerary Controls

The sibling-lift phase controls summarize one row per parent family across the
B5, B6, and B7 scopes:

```text
families = 32002
birth families = 770
non-birth families = 31232
non-birth close families = 0
```

The itinerary controls compare birth siblings against non-birth siblings inside
the checked birth-parent families:

```text
rows = 12838
birth sibling rows = 770
non-birth sibling rows = 12068
distinct non-birth transition sequences = 23
```

These controls make the final phase selection explicit: siblings can share the
same parent residual history but fail to close at the final remainder.

## Deferred

This slice also excludes B8, a null model, candidate ZIP generation, GitHub
Release, and Zenodo publication.

## Source-Only Figures

The source checkout includes regenerated Gate R figures using the
`miss / trim / split / partial_close / close` taxonomy:

```text
figures/v2_4/prc_v2_4_transition_taxonomy_counts_v0_1.png
figures/v2_4/prc_v2_4_transition_component_delta_v0_1.png
figures/v2_4/prc_v2_4_b5_to_b6_genealogy_flow_v0_1.png
figures/v2_4/prc_v2_4_remainder_taxonomy_heatmaps_v0_1.png
figures/v2_4/prc_v2_4_transition_figures_manifest_v0_1.json
```

These figures are source-only research diagnostics. They are intentionally not
part of the v2.3 public release bundle or any v2.4 candidate bundle.
