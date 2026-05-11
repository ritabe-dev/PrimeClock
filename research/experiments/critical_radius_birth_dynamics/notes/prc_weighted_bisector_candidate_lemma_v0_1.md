# Weighted Bisector Candidate Lemma v0.1

Status: public v2.3.0 finite certificate lemma note.

## Statement

For a fixed prime prefix and residue, write

```text
F_r(x) = min_i p_i * d_T(x, c_{p_i}(r)).
```

Then

```text
lambda_k(r) = max_x F_r(x).
```

On each lifted interval where the circular distance to each center is represented
by a fixed signed linear function, every active branch

```text
p_i * d_T(x, c_{p_i}(r))
```

is linear. Therefore the maximum of the lower envelope `F_r` can occur only at:

- a boundary of a lifted interval;
- a cusp/center point where a circular-distance branch changes sign;
- a weighted bisector where two active linear branches agree.

This is the finite candidate set used by the exact `critical_radius_certificate`
helper.

## Certificate Boundary

This lemma justifies the candidate-point enumeration used for the finite
critical-radius certificates. It does not use the naive adjacent-center formula
as a theorem-level shortcut.

Adjacent-center data may appear in a row only after the exact lower-envelope
bottleneck has already been computed and checked.

## Promotion Use

For v2.3.0, this note is cited as the finite certificate lemma for the exact
critical-radius checker path.
