# PRC v2.4 Theorem Candidate Selection v0.1

Status: source-only theorem-candidate note. This is not a public theorem,
candidate package, or release claim.

## Purpose

Find a v2.4 theorem candidate from the experiment data while excluding:

- facts that are visually obvious from the plots;
- direct restatements of definitions;
- weak count summaries with no arithmetic content;
- claims already demoted by Gate R.

## Selection

The best current theorem candidate is the signed phase-margin separation
theorem.

Short name: signed phase-margin separation theorem.

### Candidate Theorem

In the checked source-only `B4 -> B5`, `B5 -> B6`, and `B6 -> B7` sibling-lift
families, a lift closes exactly when its independently computed signed
phase-containment margin is positive. Every close lift is also the unique
rank-1 phase-margin lift in its sibling family. The capacity gate is necessary
for all closes, but it is not sufficient.

Equivalently:

```text
B4 -> B5: capacity families = 28, close families = 14, phase-pass families = 14
B5 -> B6: capacity families = 224, close families = 42, phase-pass families = 42
B6 -> B7: capacity families = 2948, close families = 714, phase-pass families = 714
all scopes: close families = phase-pass families = birth families = 770
all scopes: capacity non-close families = 2430
all scopes: phase-pass non-close lifts = 0
all scopes: close lifts with phase-rank 1 = 770
```

This is not the visually obvious capacity statement. Capacity only says the old
single residual component is no wider than the new prime arc. That condition
leaves `2430` capacity-satisfied non-close families. The nontrivial separator
is the signed phase margin: it is computed from the old residual component and
the new arc before reading the close/birth label, and it has no non-close
passes in the checked scopes.

### Evidence

The row-level evidence is in
`data/prc_v2_4_phase_gate_lift_diagnostics_v0_1.csv` and
`data/prc_v2_4_phase_gate_family_summary_v0_1.csv`.

The family summary gives the cross-layer counts:

```text
B4_to_B5_full: capacity=28, capacity_nonclose=14, close=14, phase_pass=14
B5_to_B6_full: capacity=224, capacity_nonclose=182, close=42, phase_pass=42
B6_to_B7_full: capacity=2948, capacity_nonclose=2234, close=714, phase_pass=714
```

The lift diagnostics verify the exact selector:

```text
all close rows: capacity_pass=True and phase_pass=True
all non-close rows: phase_pass=False
all close rows: phase_rank_desc=1
```

The phase margin is independent of the close label in the implementation:

```text
phase_pass = (_phase_margin(row) > 0)
_phase_margin(row) = signed containment margin of old residual components inside the new prime arc
is_close = classify_canonical_transition(row) == "close"
```

## Why This Survives the Exclusion Filter

Rejected as headline: raw `capacity + phase gate`.

Reason: capacity itself is visually obvious and nonselective. The promoted
claim is not "capacity + phase" as a slogan; it is the exact signed-margin
separation theorem after capacity has produced many false positives.

Kept as root theorem candidate: `signed phase-margin separation theorem`.

Reason: it is the cross-layer finite mechanism that does not depend on the B7
`4/13` pair. It should be treated as the root theorem candidate, while the
arithmetic concentration statements become refinements that ask which families
reach positive phase margin.

Kept as refinement: reflected-pair arithmetic concentration.

Reason: the B7 `4/13` and `gcd=3;pair=4/13` concentration is real and
checker-backed, but it currently looks B7-specific. It should be presented as a
refinement inside the phase-separated close set, not as the root theorem.

Kept as second theorem candidate: `k=2 r=3 lineage survival bias`.

Reason: it is arithmetic and nontrivial after inverse-width correction, but it
is an early-lineage survival statement rather than the final B7 close-pair
theorem:

```text
r=3 observed / inverse-width expected = 14456/5775
r=3 capacity-conditioned close rate = 278/475
r=2 and r=4 capacity-conditioned close rate = 103/1112
```

## Presentation Shape

Use this as the main theorem-candidate slide:

```text
Theorem candidate (finite signed phase-margin separation).
Across the checked B4 -> B5, B5 -> B6, and B6 -> B7 sibling-lift families,
positive signed containment margin selects exactly the close/birth lift. It
selects 770/770 closes, selects no non-close lift, and every close is the
rank-1 phase-margin sibling. Capacity is necessary but leaves 2430 non-close
families, so the signed phase margin is the actual finite separator.
```

Use this as the proof outline:

```text
1. Regenerate the phase-gate lift rows from the exact transition graphs.
2. For each sibling lift, compute the signed containment margin from only the
   old residual components and the new-prime arc.
3. Define phase_pass as margin > 0, independently of close/birth.
4. Verify all close lifts pass capacity and phase.
5. Verify all non-close lifts fail phase, including capacity-satisfied
   non-close controls.
6. Verify every close lift has phase_rank_desc=1 inside its sibling family.
7. State the boundary: this is a finite checked B5/B6/B7 source-only theorem
   candidate, not a B8 or asymptotic claim.
```

## Claim Boundary

Safe:

```text
Across the checked v2.4 B5/B6/B7 sibling-lift scopes, positive signed phase
margin exactly separates close/birth lifts from non-close lifts, while capacity
alone has many false positives.
The checked v2.4 B7 data further supports a refinement: reflection symmetry is
preserved pairwise, but close rows are arithmetically concentrated in the
reflected pair 4/13 and especially in gcd=3;pair=4/13.
```

Unsafe:

```text
All future births close in pair 4/13.
```

Unsafe:

```text
Reflection symmetry explains the theorem.
```

The current data supports finite checked B5/B6/B7 source-only evidence. It does
not yet support B8, an asymptotic theorem, or a public release claim.
