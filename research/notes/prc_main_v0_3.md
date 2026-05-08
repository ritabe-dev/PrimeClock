# PRC Main v0.3: Branch Fill-In

This note moves the PRC work back from consecutive complete-covering runs to
the main covering object:

```text
A_full(N) = A(N) = |T \ U_N|
```

The v0.3 diagnostic asks how the uncovered circle changes as reciprocal
branches are added cumulatively:

```text
B_k(N)      = {p prime : floor(N/p)=k}
U_{<=K}(N)  = union of arcs from branches 1..K
A_{<=K}(N)  = |T \ U_{<=K}(N)|
A_full(N)  = A(N)
```

The notation `A_k` is deliberately avoided because it is ambiguous between a
single branch and a cumulative branch cutoff.

Generate the canonical long table, summary table, and figures with:

```bash
python -m prime_reciprocal_projection.cli covering-branch-fill \
  --n 1000 10000 100000 1000000 39069 372759 \
  --max-branch 1000 \
  --out data/summaries/prc_branch_fill_v0_3.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-summary \
  --input data/summaries/prc_branch_fill_v0_3.csv \
  --out data/summaries/prc_branch_fill_summary_v0_3.csv

python -m prime_reciprocal_projection.cli covering-branch-fill-figures \
  --input data/summaries/prc_branch_fill_v0_3.csv \
  --out figures/v0
```

## Summary Table

`Kq` is the first branch cutoff where the normalized fill fraction reaches
`q`. A censored value means that the threshold was not reached by `K=1000`.

| N | exact complete | A_full(N) | K50 | K90 | K99 | A_{<=1} | A_{<=1000} | residual at K=1000 |
|---:|:---:|---:|---:|---:|---:|---:|---:|---:|
| 1,000 | false | 0.114647 | 27 | 333 | 500 | 0.898629 | 0.114647 | 0.000000 |
| 10,000 | false | 0.041923 | 126 | censored | censored | 0.922129 | 0.266129 | 0.254720 |
| 39,069 | true | 0.000000 | 285 | censored | censored | 0.932367 | 0.343132 | 0.368022 |
| 100,000 | false | 0.040222 | 369 | censored | censored | 0.937978 | 0.403242 | 0.404364 |
| 372,759 | true | 0.000000 | 885 | censored | censored | 0.944573 | 0.460601 | 0.487629 |
| 1,000,000 | false | 0.050069 | censored | censored | censored | 0.948604 | 0.501490 | 0.502397 |

## First Reading

Branch 1 remains the prime-gap shadow layer, but it covers only a small part of
the circle by measure: the branch-1 uncovered mass is about `0.90` to `0.95` on
the tested anchors.

The deeper result is that even branches `1..1000` do not usually explain the
full covering state. Only `N=1000` reaches the full uncovered measure by
`K=1000`. The exact-complete anchors `39069` and `372759` are not fast early
fill-in cases; they still have large normalized residuals at `K=1000`.

This makes the main PRC question sharper:

```text
How deep into k must the reciprocal branch system go before A_{<=K}(N)
approaches A_full(N), and does that depth behave differently for exact-complete
values than for matched controls?
```

## Consequence

The main PRC research direction should treat these as separate signals:

- `G1(N)`: transformed prime-gap shadow from branch 1.
- `G(N)`: largest shadow that survives all branch fill-in.
- `A(N)`: total uncovered mass after all branches.
- `A_{<=K}(N)`: cumulative branch fill-in curve.
- `K50/K90/K99`: branch depth needed to explain a chosen fraction of the
  branch-1-to-full fill-in.

The consecutive-run work remains useful as a forensic side problem, but this
branch fill-in curve is closer to the central PRC mechanism.

## Non-Claims

- v0.3 does not claim that exact-complete values are explained by early branch
  fill-in speed.
- v0.3 does not claim that the six anchor values are unbiased.
- v0.3 does not claim that `K50/K90/K99` behavior is stable across `N`.
- Complete-vs-ordinary interpretation is deferred until matched controls are
  generated in v0.4.
