# PRC v2.6 Gate R Local-First Process v0.1

## Purpose

Purpose: keep v2.6 proof-candidate exploration local-first until a coherent Gate R checkpoint is ready. This prevents early research notes from being promoted into GitHub PR / CI flow before the theorem-note promote/defer decision is stable.

Current status: v2.5 public theorem release protection remains 100%; v2.6 endpoint-distance proof-obligation readiness is about 90-95%; the theorem-note promote/defer decision remains about 0.5 slice away.

## Gate Policy

Gate R is local-first by default:

- local branch;
- source-only note/checker;
- local workflow;
- local commit when useful;
- no new PR or push unless the work has become a coherent Gate R checkpoint.

Gate C is PR/CI-first because it involves candidate bundles, manifests, reproducibility, release guards, and package hygiene.

Gate P is PR/CI-first because it involves public wording, release notes, DOI, citation, GitHub Release, and publication boundaries.

## PR #6 Handling

PR #6 is a draft checkpoint candidate for the v2.6 endpoint-distance proof-obligation work. It is already CI green and mergeable, but it should not be merged while the endpoint-distance proof is still under theorem-note review.

Operational decision:

- keep PR #6 open as a draft;
- do not close it;
- do not merge it yet;
- continue endpoint-distance and theorem-note decision work on the same local branch;
- update the existing PR only after the theorem-note promote/defer decision is clear.

## Next Work

The next v2.6 work should remain local on `codex/v26-special-point-endpoint-distance-proof`.

It should decide whether:

- `Forbidden Special Remainder Lemma` can be promoted to a source-only theorem note;
- `Central Endpoint Obstruction Lemma` can be promoted to a source-only theorem note;
- endpoint spacing is enough to prove the residual-gap containment bridge;
- `3 mod 6 ancestry` remains diagnostic only.

## Non-claims

This v2.6 process note makes no public theorem claim, no DOI claim, no B8 theorem, no B8 full graph claim, no general predictor claim, and no asymptotic law claim.

PR/CI is not forbidden for Gate R. It is only reserved for coherent Gate R checkpoints, not every proof-candidate edit.
