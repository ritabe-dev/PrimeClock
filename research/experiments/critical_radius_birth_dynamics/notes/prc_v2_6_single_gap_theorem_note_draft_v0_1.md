# PRC v2.6 Necessary-Only Proof Note v0.1

## Definitions

Work on `R/Z`. The old prime prefix is `{p_1=2, p_2=3, ..., p_k}` with
`p_k >= 5`; let `q=p_{k+1}` be the next odd prime. Old clouds are closed arcs,
and the old residual set is their open complement.

For a q-remainder `a`,

```text
I_q(a) = [(a - 1/2)/q, (a + 1/2)/q].
```

Use a local circular representative when an interval crosses `0/1`. Endpoint
equality is not strict containment.

For this note, a q-cloud produces birth for an old residual component `G` only
when `closure(G) subset int(I_q(a))`.

## Special Endpoint Spacing Lemma

For old endpoints up to `p_k`,

```text
dist(0, nearest old endpoint) >= 1/(2p_k)
dist(1/2, nearest old endpoint other than 1/2) >= 1/p_k.
```

Odd-prime endpoints have form `odd/(2p)`. Endpoints are a union; combining old
clouds does not create new endpoints. Near `0`, the closest endpoint for prime
`p` is at distance `1/(2p)`. Near `1/2`, the closest distinct odd numerators are
`p-2` and `p+2`, so the distance is `1/p`.

The prime `2` endpoints are handled separately. For `p_k >= 5`, their distance
`1/4` from `1/2` is larger than `1/p_k`, so they do not weaken the displayed
bound.

## Residual Boundary Lemma

Since the old covered set is a finite union of closed arcs, its boundary is
contained in the set of old cloud endpoints.

On each one-sided open interval adjacent to `0` or `1/2`, up to the nearest old
endpoint on that side, the old covered/uncovered state is constant.

If the side is covered, that interval contains no old residual component. If
the side is uncovered, the same old residual component continues until the
nearest old endpoint.

## Forbidden Special Remainder Lemma

For `q=p_{k+1}`, the remainders

```text
0, (q-1)/2, (q+1)/2
```

cannot produce birth.

For `a=0`, use the local representative `(-1/2, 1/2)`. On both sides of `0`,
the q-cloud reaches only `1/(2q)`, while the nearest old endpoint is at distance
at least `1/(2p_k)`. Since `q>p_k`, the q-cloud cannot reach that endpoint. By
the Residual Boundary Lemma, the covered case contains no residual component
and the uncovered case leaves part of the adjacent residual component outside
the q-cloud.

For the two central remainders, the q-cloud touches `1/2` from one side and
reaches only `1/q`. The nearest old endpoint other than `1/2` is at distance at
least `1/p_k`, so the same argument applies.

## Central Endpoint Obstruction

If an old odd-prime endpoint equals a new q-endpoint, then the point is `1/2`.
Indeed, `m/(2p)=n/(2q)` with distinct odd primes gives `mq=np`, hence `p|m` and
`q|n`; the endpoint numerators force `m=p` and `n=q`.

The `p=2` endpoints are `1/4` and `3/4`. An odd-q endpoint has form `n/(2q)`
with `n` odd, so equality with `1/4` or `3/4` would require `n=q/2` or
`n=3q/2`, impossible for odd `q`.

The only q-clouds with endpoint `1/2` are the two central clouds, already
excluded by the forbidden special remainder lemma. Thus endpoint-touch birth is
obstructed.

## Single-Gap Grid Containment Criterion

For a fixed old residual component `G=(L,R)` and a fixed q-remainder `a`,
choose a local linear representative of `R/Z` in which both `G` and the
relevant q-cloud are represented without crossing the chosen cut.

```text
closure(G) subset int(I_q(a))
iff
(a - 1/2)/q < L < R < (a + 1/2)/q
iff
qR - 1/2 < a < qL + 1/2.
```

This is only a fixed-gap geometric criterion. It is not a general theorem that
all PRC birth rows reduce to this case beyond checked scopes.

## Boundary

This is a private source-only proof note. It makes no public theorem, DOI,
GitHub Release, B8 theorem, predictor, or asymptotic-law claim. The global
`Close(row)` equivalence remains checked-scope support only.
