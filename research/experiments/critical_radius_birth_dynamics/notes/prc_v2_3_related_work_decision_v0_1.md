# PRC v2.3 Related-Work Decision v0.1

Status: internal terminology decision, not a bibliography.

For the v2.3 public-candidate review path, use `critical radius` as the primary
project term. The expression

```text
lambda_k(r) = max_x min_i p_i d_T(x, c_i(r))
```

may be described as a finite weighted covering-radius max-min expression, but
the note should not present `weighted covering radius` as a new theorem name or
as a novelty claim.

This decision is enough for internal candidate review because the finite claims
are checked directly by:

```text
check_candidate.py: checks=13, failed=0
check_candidate_standalone.py: checks=10, failed=0
```

Before a public release, either:

1. keep `critical radius` as the project-defined term and leave
   `weighted covering-radius` as descriptive shorthand; or
2. add formal related-work citations if the public note leans on covering-radius
   terminology as an established external concept.

Do not delay internal v2.3 candidate review on bibliography expansion alone.
