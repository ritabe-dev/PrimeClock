# PRC v2.4 Research Review Note v0.1

Status: initial Gate R note for the v2.4 research line.
Release eligibility: source-only research review metadata; not a candidate
package or public release artifact.

## Core idea

v2.4 should start from early residual genealogy: gaps appear in the small
prime-prefix layers, then survive through local miss/trim/split/partial-close
transitions before final extinction at a checked birth layer. The previous
`C4 -> B5` transition graph is still useful, but it is a local transition layer
inside a longer lineage rather than the natural starting point.

The v2.3 gap-aperture birth formula explains when an old residual gap is closed
by the next prime arc. The v2.4 question is broader: for each checked
`B5/B6/B7` birth residue, where did the final residual component come from
across `k=1..birth_k`?

The formal terminal state is:

```text
zero-residual state: R_k(r) = empty set
```

This is not a gap at the point `0` and not residue `0`; it is the absence of
any residual open gap after the new arc is added.

The intended transition vocabulary is:

```text
miss          : the new arc does not intersect the old residual gaps
trim          : the new arc intersects residual set, no component vanishes,
                and the circular component count does not increase
split         : the new arc intersects residual set, no component vanishes,
                and the circular component count increases
partial_close : at least one component closes, but residual gaps remain
close         : the new arc reaches the zero-residual state
```

Fine structure should be carried as attributes, not as additional primary
labels:

```text
old_component_count
new_component_count
component_delta = new_component_count - old_component_count
touched_component_count
closed_component_count
is_birth
```

The Gate R story should use circular-component attributes so cut-at-0 CSV
pieces are not mistaken for changes in the number of circular gaps. In that
normalized geometry, `split` is kept as a primary label because increasing the
number of residual components is not just trimming.

## Claim shape

The first claim shape is diagnostic, not release-level. The source-only early
genealogy table records every checked `B5/B6/B7` birth residue across
`k=1..birth_k`, then the transition graph tables describe selected local layers
inside that lineage.

The current finite diagnostic is:

```text
Birth residual genealogy
rows = 5320
B5 lineage rows = 70 = 14 births * 5 layers
B6 lineage rows = 252 = 42 births * 6 layers
B7 lineage rows = 4998 = 714 births * 7 layers

Genealogy transition totals
start = 770
miss = 1294
trim = 1354
split = 566
partial_close = 566
close = 770

Genealogy diagnostics
all final birth layers close = 770
all pre-final layers remain uncovered
origin_component_present rows = 576
zero_center_available rows = 4744
final birth rows with gcd(residue, M_k) > 1 = 770
final birth rows with new-prime remainder 0 = 0

Angle/aperture diagnostics
k=2 r=3 mod 6 residual width = 1/6
k=2 r=3 mod 6 birth-lineage count = 556 / 770
k=2 birth-lineage average residual measure = 59/308
k=2 all-residue average residual measure = 1/3
k=2 birth-lineage target-sector share = 112/177
k=2 all-residue target-sector share = 1/6
final aperture rows = 770, all positive aperture and containment margins
incremental grid phase: k=2 p=3 remainder 0 split = 556 / 770
incremental B7 grid phase: k=2 p=3 remainder 0 split = 522 / 714
incremental B7 grid phase: k=3 p=5 remainders 1 and 4 partial_close = 252 + 252
incremental B7 grid phase: k=7 p=17 remainders 4 and 13 close = 199 + 199
birth-potential score: inverse_width pearson = 0.928735
birth-potential score: covered_width pearson = 0.785851
birth-potential score: inverse_width r=3 expected = 5775/26, observed = 556

B5 observed taxonomy
miss = 1520
trim = 474
split = 258
partial_close = 22
close = 14

B5 structural attributes
trim + component_delta 0 = 474
split + component_delta +1 = 258
partial_close + component_delta -1 = 22
close + component_delta -1 + is_birth = true = 14

B6 birth-parent sanity probe
rows = 546 = 42 birth parents * 13 lifts
miss = 504
close = 42
trim = partial_close = 0
split = 0

B5 -> B6 full transition graph
rows = 29562 = 2274 uncovered C5 parents * 13 lifts
miss = 20442
trim = 5610
split = 3090
partial_close = 378
close = 42

B6 -> B7 birth-neighborhood probe
rows = 12138 = 714 B7 birth parents * 17 lifts
miss = 11424
close = 714
trim = partial_close = 0
split = 0

B6 -> B7 full transition graph
rows = 501840 = 29520 uncovered B6 parents * 17 lifts
miss = 363600
trim = 78310
split = 54490
partial_close = 4726
close = 714

Sibling-lift phase controls
families = 32002
birth families = 770
non-birth families = 31232
non-birth close families = 0

Transition itinerary controls
rows = 12838
birth sibling rows = 770
non-birth sibling rows = 12068
distinct non-birth transition sequences = 23

Exact residual lineage atlas
atlas rows = 369824
final represented lifts = 53336
birth sibling final lifts = 770
non-birth sibling final lifts = 12068
capacity-satisfied non-close final lifts = 40498
capacity gate close families = 770
capacity gate non-close families = 2430

Independent phase-gate diagnostics
lift rows = 533690
families = 32002
close families = 770
capacity-satisfied non-close families = 2430
phase-pass non-close lifts = 0
close lifts with top phase-margin rank = 770

Gate R decision table
claim candidates = 5
keep = 2
support = 2
weak = 1
k2 width-normalized lineage: r=3 observed / inverse-width expected = 14456/5775
k2 capacity survival: r=2 close rate = 103/1112, r=3 close rate = 278/475, r=4 close rate = 103/1112
B7 close top reflection pair = 4/13 with 398 / 714 close rows
B7 close top gcd/reflection cross stratum = gcd=3;pair=4/13 with 316 / 714 close rows
```

The genealogy table is the top-level Gate R object. It shows that every checked
birth has a nonempty residual history before final extinction. The `close` rows
in local transition graphs are alignment checks: `close` is the geometric
residual-extinction state, while `birth` is the historical event of becoming
covered at this layer. The `partial_close` rows are evidence that v2.4 can
explain non-birth interactions instead of only birth rows.

The angle/aperture diagnostic is the current correction against a too-simple
angle story. Across all residues, angle exposure averages out. After
conditioning on future birth lineages, the data strongly selects the narrow
`k=2, r=3 mod 6` residual state and its side-sector gaps. That selection is not
explained by residual width alone: the observed `r=3` count is still high after
uniform, residual-width, covered-width, and inverse-width baselines are shown.
The final checked birth layers then require positive aperture and containment
margins, keeping the v2.3 q-grid phase story in the loop.

The grid-phase diagnostic should be read one prime at a time. The early
`p=3` grid center at remainder `0` is the dominant `k=2` event in future birth
lineages; it splits the `k=1` origin-side residual into side gaps. The later
histograms then show how `p=5`, `p=7`, ..., and the final prime act on those
lineage states. A final-layer-only histogram is useful, but it is secondary to
this incremental story.

The birth-potential score is intentionally model-comparison, not model
selection by fiat. The simple `inverse_width` score fits the observed k=2
birth-lineage counts better than uniform, residual-width, or covered-width
baselines, but it still underpredicts the `r=3 mod 6` state. That leaves room
for other mechanisms, especially lineage survival and q-grid phase alignment.

The five-cycle synthesis now re-runs the story from five separate angles:
reflection-orbit guards, genealogy grammar, local transition dynamics,
aperture/phase robustness, and negative controls. It fixes that broader
boundary as source-only review evidence:

```text
scoreboard rows = 25
matched-control diagnostics = 11
reflection max imbalance = 0
final nonunit residue strata = 770/770
distinct transition sequences = 23
B5 -> B6 full graph = miss 20442, trim 5610, split 3090, partial_close 378, close 42
B6 -> B7 full graph = miss 363600, trim 78310, split 54490, partial_close 4726, close 714
B7 top final reflected q-pair share = 398/714
sibling-lift non-birth close families = 0/32002
itinerary non-birth sibling rows = 12068
exact residual lineage atlas = birth 770, nonbirth 12068, capacity_nonclose 40498
independent phase gate = 770/770 close families aligned, capacity_nonclose 2430
Gate R decision table = keep 2, support 2, weak 1
best simple model = inverse_width, Pearson 0.928735
known model failure = inverse_width still underpredicts r=3 mod 6
prime-zero all-birth explanation = rejected, final new-prime remainder zero 0/770
Gate R synthesis decision = continue research
```

The current compact explanation is therefore not a single-cause model. It is:

```text
early narrow residual potential + lineage survival + incremental q-grid phase alignment
```

This is strong enough to justify more source-only synthesis, but not yet a
candidate package decision. The synthesis note
`notes/prc_v2_4_five_cycle_research_synthesis_v0_1.md` is the current
review-facing summary of supported diagnostics, partial hypotheses, weak
baselines, and non-claims.

The exact residual lineage atlas makes the mechanism more inspectable. It
shows every checked birth sibling as an exact `k=1..birth_k` residual history,
and it adds non-birth sibling plus capacity-satisfied non-close controls. All
checked close families pass the single-component capacity gate, but 2430
families also pass that gate without closing. This is the current strongest
evidence that capacity is necessary-looking but not sufficient; sibling phase
selection remains part of the explanation.

The independent phase-gate diagnostics make that last step non-circular.
For each sibling lift, the signed containment margin is computed from the
pre-final residual component and the new prime arc before reading the
`close`/`birth` labels. In the checked B5/B6/B7 scopes, every close lift has
`capacity_pass=true`, `phase_pass=true`, and phase-margin rank 1 inside its
family. The 2430 capacity-satisfied non-close families have no phase-pass lift.
Thus the current source-only evidence separates:

```text
capacity gate : enough width to close the residual component
phase gate    : the sibling q-grid arc is positioned to contain it
birth         : the historical event attached to that close
```

The Gate R decision table changes the workflow from discovery to selection.
The obvious mechanisms are kept as support, not as the headline:

```text
capacity + phase gate              -> weak / foundation
signed phase-margin separation theorem -> keep / headline theorem candidate
sibling itinerary divergence       -> support / explanation
width-normalized k2 r=3 lineage survival bias -> support / arithmetic refinement
reflection-paired final remainder bias -> support / arithmetic refinement
```

The main theorem candidate is now the signed phase-margin separation theorem:
positive signed containment margin separates all checked close/birth lifts from
non-close lifts across B4->B5, B5->B6, and B6->B7 sibling families. The
arithmetic table deliberately does not accept `gcd > 1` or `gcd=3` as a
standalone claim. The `k=2, r=3 mod 6` lineage survives after inverse-width
correction and after capacity conditioning, so it remains an arithmetic
refinement. The reflection-pair diagnostic is also a refinement: final close
remainders remain reflection-balanced but concentrate in specific pairs,
especially the B7 `4/13` pair.

The B6 sanity probe is deliberately narrower than a full transition graph. It
checks only the B6 birth-parent neighborhoods and confirms that `close` still
aligns exactly with the checked B6 birth rows. In primary taxonomy terms, the
B6 probe gives `miss=504` and `close=42`, with no trim, split, or partial-close
rows in that restricted neighborhood. It does not yet claim anything about the
full B6 transition graph.

The B5 -> B6 full graph is the first full-layer sanity check for the v2.4
taxonomy. It keeps the simple primary labels but shows richer component-delta
structure: `trim + component_delta 0 = 5610`, `split + component_delta +1 =
3090`, and `partial_close + component_delta -1 = 378`. The 42 close rows match
the checked B6 birth rows, with no non-birth close rows.

The B6 -> B7 full graph is now available as a source-only diagnostic. It uses
every uncovered B6 parent and all `q=17` lifts. The full graph keeps the same
primary taxonomy, has 714 close rows, and those close rows match exactly the
checked B7 birth rows. There are no non-birth close rows.

The sibling-lift phase controls summarize all B5/B6/B7 parent families and
show that `close_lift_count == birth_lift_count` with `nonbirth_close_count =
0` in every checked family. The itinerary controls then compare birth siblings
against non-birth siblings from the same parent families. This strengthens the
non-birth control surface: siblings can share the same earlier transition
history but diverge at the final phase remainder.

The research line should separate:

```text
definition cleanup : exact residual gap nodes and transition edges
finite diagnostics : B5 transition pilot checks against v2.3 gap-aperture data
candidate claims   : only after a small checker/test path is stable
future work        : larger layers, null models, and broader transition laws
```

## Why now

v2.3.0 established the critical-radius spectrum and the gap-aperture /
q-grid phase birth mechanism for the checked finite layers. In particular,
`B_5/B_6/B_7` are recorded as unique strict single-gap births.

That leaves a natural next research step: explain not only birth rows, but the
full residual-gap transition behavior leading into and around those births. The
B5 transition pilot is small enough to inspect before committing to a v2.4
candidate package.

The `N=11` prime-zero obstruction is still a useful local diagnostic for actual
prime targets: smaller prime clocks `p < 11` cannot put a center at `0` for
the target `11`, because `11 mod p != 0`; adding `p=11` removes that
obstruction. But the checked `B5/B6/B7` birth residue classes are not generally
prime-origin events: all 770 final genealogy rows are non-coprime residue
classes, and none has new-prime remainder `0`. The broad v2.4 story should
therefore be residual genealogy, not a prime-zero theorem.

## Stop line

Do not package v2.4 as a candidate. The bridge line excludes:

```text
B_8
public release
GitHub Release or Zenodo publication
full null model expansion
broad theorem claim
general all-births single-gap theorem
```

The source-only bridge should remain available as internal Gate R evidence for
v2.5, but it should not create a candidate ZIP, public release, GitHub Release,
or Zenodo DOI.

## Risks

The transition taxonomy may be too noisy or too dependent on endpoint and
wrap-around conventions to support a clean v2.4 story. The early genealogy may
produce too many lineage shapes to summarize cleanly. A transition graph could
also duplicate the v2.3 gap-aperture formula unless it adds explanatory value
beyond the close case.

Before any later candidate packaging, the next line should decide which v2.4
diagnostics are worth recomputing and restating as v2.5 artifacts.

## Decision

defer

v2.4 should remain a source-only bridge, not a public candidate or DOI release.
It produced useful diagnostics, especially signed phase-margin separation,
sibling-lift controls, and residual lineage tables, but those are best treated
as internal Gate R evidence for the next research line.

The next candidate line should be v2.5, centered on residual dynamics,
obstruction classification, feature ablation, and prediction. Any v2.4
diagnostic that becomes part of v2.5 must be recomputed and restated as a v2.5
artifact instead of being cited as a public v2.4 result.
