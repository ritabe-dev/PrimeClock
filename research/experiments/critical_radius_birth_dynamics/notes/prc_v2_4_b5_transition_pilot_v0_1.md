# PRC v2.4 B5 Transition Pilot v0.1

Status: source-only v2.4 research seed.
Release eligibility: excluded from v2.3 public and candidate bundles.

Data file:

```text
research/experiments/critical_radius_birth_dynamics/data/prc_v2_4_b5_gap_close_transition_pilot_v0_1.csv
```

## Purpose

This CSV is the first small pilot for the v2.4 residual gap transition graph
direction. It records `k=4 -> k=5` parent/child transition rows and is meant to
test whether the v2.3 gap-aperture birth formula can be expanded into a full
gap genealogy view.

Each row records:

```text
parent residue modulo M_4
child residue modulo M_5
new prime q = 11
new-prime remainder
old residual gap count and endpoints
new q-arc boundary endpoints
closed and remaining gap counts
transition type
whether the row is a B5 birth
```

## Initial Interpretation

For v2.3, the release-level statement is the close case: a birth occurs when
the new `q`-arc closes the old residual gap, and the checked `B_5/B_6/B_7`
birth rows are unique strict single-gap births.

For v2.4, the pilot asks whether the non-birth rows can also be organized
cleanly as residual-gap transitions. The first useful check is whether B5
close rows align with the v2.3 gap-aperture/q-grid phase explanation while the
miss/trim/split/partial-close rows explain nearby non-birth lifts.

## Zero-Residual State

This note uses `zero-residual state` for a row whose child residual set is
empty:

```text
R_k(r) = empty set
```

The shorter phrase `zero-gap state` is only explanatory shorthand. It does not
mean a gap at the point `0`, and it does not mean residue `0`. In this pilot,
the `close` rows are exactly the rows where a B5 birth reaches the
zero-residual state. The code keeps `close_to_zero` as a compatibility label,
but the v2.4 research wording uses `close`, `zero-residual state`, and
`residual extinction`.

Current pilot summary:

```text
rows = 2288 = 208 parents * 11 lifts
transition_type close = 14
transition_type not_close = 2274
is_b5_birth = 14
non-birth close rows = 0
birth rows with remaining_gap_count = 0: 14
```

Primary v2.4 taxonomy:

```text
miss            = 1520
trim            = 474
split           = 258
partial_close   = 22
close           = 14
```

The primary taxonomy is source-only and is derived from the existing CSV
columns; the CSV schema is not changed in this slice. The classifier normalizes
cut-at-0 interval pieces into circular components before assigning labels.

The labels are intentionally simple:

```text
miss          : the new arc does not hit any old residual component
trim          : the new arc hits residual set, no old component vanishes,
                and the circular component count does not increase
split         : the new arc hits residual set, no old component vanishes,
                and the circular component count increases
partial_close : at least one old component vanishes, but residual set remains
close         : residual set becomes empty
```

Finer structure is recorded as attributes rather than taxonomy names:

```text
old_component_count
new_component_count
component_delta = new_component_count - old_component_count
touched_component_count
closed_component_count
is_birth
```

For the B5 pilot:

```text
trim + component_delta 0  = 474
split + component_delta +1 = 258
partial_close + component_delta -1 = 22
close + component_delta -1 + is_birth = true = 14
```

So `trim` is component-preserving shrinkage, while `split` records the case
where the new arc cuts a residual component into more components. This keeps the
primary labels simple without hiding the difference between shrinking a gap and
increasing the number of residual gaps.

Additional finite diagnostics:

```text
close rows are exactly the B5 birth rows
partial_close rows all have old_gap_count = 2
close parent residues form 7 reflection pairs
close rows use 4 old-gap endpoint shapes
```

The `partial_close` rows are useful because they separate "the new arc interacts
with old residual gaps" from "the new arc reaches the zero-residual terminal
state." In this pilot, partial closure never creates a B5 birth. `Birth` and
`close` are not synonyms: `close` is the geometric residual-extinction state,
while `birth` is the historical event of moving from previously uncovered to
covered at this layer.

## Prime-Zero Obstruction Diagnostic

The local `N=11` diagnostic is:

```text
For p in {2,3,5,7}, 11 mod p != 0.
```

So the smaller prime clocks have no center exactly at `0` for the target
`N=11`. Adding the prime `11` itself removes that obstruction because
`11 mod 11 = 0`; the new `11`-arc has a zero-centered component. This is a
local diagnostic for the B5 pilot, not a general theorem.

This is a v2.4 research diagnostic. It is not a new public v2.3.0 claim.

## Non-Claims

This pilot does not claim:

```text
B_8 data
a public v2.4 release
a null model
a general residual-gap theorem
that all future births are single-gap births
```

It is source material for Gate R only until a small checker and explanatory
note make the transition taxonomy worth packaging.
