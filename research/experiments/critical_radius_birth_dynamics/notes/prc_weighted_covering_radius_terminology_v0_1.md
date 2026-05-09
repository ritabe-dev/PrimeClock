# Weighted Covering-Radius Terminology v0.1

Status: internal terminology note, not a related-work survey.

## Purpose

The v2.3 candidate uses `critical radius` as the project term for the exact
threshold

```text
lambda_k(r) = inf { lambda >= 0 :
  union_{i<=k} I_{p_i}^(lambda)(r) = R/Z }.
```

The phrase `weighted covering-radius` is used only as descriptive shorthand for
the finite max-min expression

```text
lambda_k(r) = max_x min_{i<=k} p_i * d_T(x, c_{p_i}(r)).
```

This does not claim novelty, import a named external theorem, or replace the
project term `critical radius`.

## Computation Boundary

The exact implementation evaluates the lower envelope

```text
x -> min_{i<=k} p_i * d_T(x, c_{p_i}(r))
```

at rational candidate points, including lifted weighted-bisector candidates.
The reported bottleneck point is then checked against the exact value.

The candidate does not use the naive adjacent-center formula as a theorem-level
shortcut. Adjacent-center or bottleneck rows may be used only as checked
certificate data after the exact weighted max-min value has been computed.

## Promotion Guidance

For a public v2.3 note:

- keep `critical radius` as the primary term;
- describe `weighted covering-radius` as a finite max-min interpretation;
- add formal related-work citations before presenting the terminology as more
  than descriptive shorthand;
- keep all `B_5/B_6/B_7` birth statements finite.

This resolves the internal wording blocker enough for a public-candidate draft.
External terminology review and bibliography polish remain useful before a
public release.
