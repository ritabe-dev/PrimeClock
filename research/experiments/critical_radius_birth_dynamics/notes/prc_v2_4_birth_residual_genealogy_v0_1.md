# PRC v2.4 Birth Residual Genealogy v0.1

Status: source-only Gate R diagnostic for the v2.4 research line. This note is
not a candidate package, public release note, or public claim.

## Purpose

The transition graph work started at `C4 -> B5`, but that is already midstream.
This source-only diagnostic asks where the final birth gaps came from by tracing
every checked `B5/B6/B7` birth residue through the earlier prime-prefix layers:

```text
k = 1 -> 2 -> 3 -> ... -> birth_k
```

Each row records the projected residue, residual components, uncovered measure,
local transition label, zero-center availability, origin-side residual presence,
and whether the row is the final birth layer.

## Summary

The committed source-only CSV is:

```text
data/prc_v2_4_birth_residual_genealogy_v0_1.csv
```

It contains:

```text
rows = 5320
B5 lineages = 70 = 14 births * 5 layers
B6 lineages = 252 = 42 births * 6 layers
B7 lineages = 4998 = 714 births * 7 layers
```

Transition totals:

```text
start         = 770
miss          = 1294
trim          = 1354
split         = 566
partial_close = 566
close         = 770
```

All 770 final birth-layer rows are `close` rows and reach the zero-residual
state. All pre-final rows remain uncovered, so the genealogy really does trace
a residual lineage before final extinction.

## Origin And Zero-Center Diagnostics

The origin-side and zero-center columns are diagnostics, not assumptions.

```text
origin_component_present rows = 576
zero_center_available rows = 4744
final birth rows with gcd(residue, M_k) > 1 = 770
final birth rows with new-prime remainder 0 = 0
```

This means the simple "target prime supplies a zero-centered arc" story is not
the general explanation for the checked `B5/B6/B7` birth residue classes. It is
still a useful local intuition for actual prime targets, but v2.4 should not
claim that all checked births are prime-origin events.

## Interpretation

The stronger v2.4 story is:

```text
early residual components persist through small-k layers;
local transitions miss, trim, split, or partially close them;
the final birth layer closes the remaining residual set.
```

The existing `C4 -> B5` and `B5 -> B6` transition graphs remain useful, but
they should be read as local transition layers inside this longer genealogy.

## Width-Corrected Angle And Aperture Diagnostics

The source-only angle/aperture diagnostic separates three effects that are easy
to mix together:

```text
residual measure: how much gap remains
angle exposure: where the remaining gap lies
aperture margin: whether the next prime arc is wide enough, with phase room, to close it
```

For `k=2`, the raw residual widths by `r mod 6` are:

```text
r=0: 1/2   = 180 degrees
r=1: 5/12  = 150 degrees, contains 0
r=2: 1/4   = 90 degrees
r=3: 1/6   = 60 degrees, two side gaps at 60-90 and 270-300 degrees
r=4: 1/4   = 90 degrees
r=5: 5/12  = 150 degrees, contains 0
```

The checked `B5/B6/B7` birth lineages are strongly enriched at the narrow
`r=3 mod 6` state:

```text
r=3 observed birth-lineage count = 556 / 770
observed / uniform expectation = 1668/385
observed / residual-width-weighted expectation = 3336/385
observed / covered-width-weighted expectation = 6672/1925
observed / inverse-width-weighted expectation = 14456/5775
```

So the effect is not explained by raw residual area alone. The safe reading is
that future birth lineages are filtered toward early narrow residual states,
and those narrow states happen to sit in the side sectors created by the
`k=2, r=3 mod 6` split.

The same diagnostic shows that all residues keep a constant target-sector share
of residual measure (`1/6`) when averaged over the full residue space, but the
birth lineage does not:

```text
k=2 all residues:     average residual measure = 1/3, target share = 1/6
k=2 birth lineages:   average residual measure = 59/308, target share = 112/177
k=4 all residues:     average residual measure = 8/35, target share = 1/6
k=4 birth lineages:   average residual measure = 2441/40425, target share = 1730/2441
```

This supports the current v2.4 interpretation:

```text
whole residue space: angle exposure averages out
future birth filter: early narrow side gaps are strongly selected
final close: q-grid phase and positive aperture margin finish the closure
```

For the final checked birth layers, all 770 prefinal residual states are
single-component gaps and all have positive aperture and containment margins.
This keeps the v2.3 strict single-gap result compatible with the v2.4
genealogy story.

The source-only birth-potential score keeps multiple hypotheses side by side.
For `k=2`, each residue occurs with baseline probability `1/6`, and the simple
models are:

```text
uniform
residual_width
covered_width
inverse_width
```

Against the observed B5/B6/B7 birth-lineage counts, the correlations are:

```text
inverse_width  pearson = 0.928735
covered_width  pearson = 0.785851
uniform        pearson = 0.000000
residual_width pearson = -0.785851
```

The inverse-width model is the best of these simple candidates, but it still
underpredicts `r=3 mod 6`:

```text
r=3 inverse-width expected count = 5775/26
r=3 observed birth-lineage count = 556
observed / expected = 14456/5775
```

So the current interpretation is not "width explains everything." It is:

```text
early narrow residual width is a strong selection factor;
additional survival and q-grid phase alignment still remain necessary.
```

The grid-phase diagnostic must be read incrementally, one newly added prime at
a time. The strongest early signal is not the final `q` histogram; it is the
`k=1 -> k=2` step:

```text
B5/B6/B7 birth lineages at k=2
p=3, remainder 0, transition split = 556 / 770
```

For B7 lineages alone:

```text
k=2, p=3, remainder 0, split = 522 / 714
k=3, p=5, remainders 1 and 4, partial_close = 252 + 252
k=7, p=17, remainders 4 and 13, close = 199 + 199
```

This gives a cleaner story than a one-shot final-grid histogram:

```text
p=3 center at 0 splits the k=1 origin-side gap;
later prime grids act on the resulting side components;
final close happens only when the next grid phase lands with positive aperture.
```

## Non-Claims

This diagnostic does not claim:

```text
B8 data
a public v2.4 release
a null model
a broad theorem for all births
that checked births are prime-origin events
```

## Source-Only Figures

The source checkout includes two genealogy-specific figures:

```text
figures/v2_4/prc_v2_4_birth_residual_genealogy_layers_v0_1.png
figures/v2_4/prc_v2_4_birth_origin_zero_diagnostics_v0_1.png
figures/v2_4/prc_v2_4_k2_gap_width_bias_v0_1.png
figures/v2_4/prc_v2_4_lineage_measure_bias_v0_1.png
figures/v2_4/prc_v2_4_incremental_grid_phase_histograms_v0_1.png
figures/v2_4/prc_v2_4_birth_potential_score_v0_1.png
```

They are Gate R diagnostics only and are excluded from public/candidate
bundles.
