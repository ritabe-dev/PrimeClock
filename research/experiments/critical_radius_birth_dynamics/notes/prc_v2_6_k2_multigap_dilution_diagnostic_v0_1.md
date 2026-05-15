# PRC v2.6 K=2 Multi-Gap Dilution Diagnostic v0.1

## Goal

Purpose: add a source-only v2.6 Gate R diagnostic for the apparent `B4->B5` weakness of `3 mod 6` ancestry. The diagnostic asks whether the weak early signal is better read as `k=2 multi-gap dilution`: many `3 mod 6` proxy families in `B4->B5` are multi-gap and therefore poor birth candidates under the special point obstruction line.

Current diagnostic readiness is about 95% after this note and checker. The remaining work is to decide whether this belongs in the next Gate R checkpoint. The v2.5 public theorem release remains protected.

## B4 Weakness

The existing mod 6 ancestry diagnostic records `B4->B5` as weak_or_non_supportive for `mod 6 = 3`, with close rows `2/14`. This note does not overturn that result.

Instead, it refines the reading: `B4->B5` may be weak for `3 mod 6` because `3 mod 6` proxy families are diluted by multi-gap parents at this early transition. In the committed checked scope, `B4->B5` has `35` families with `parent_residue % 6 = 3`; only `14` are single-gap, while `21` are multi-gap. The `2` close rows in that class come from the single-gap side.

## Component Dilution Table

The committed `prc_v2_6_k2_multigap_dilution_summary_v0_1.csv` aggregates the checked phase diagnostics by `scope x parent_mod6_proxy`, where `parent_mod6_proxy = parent_residue % 6`.

This is an ancestry proxy, not a proven lineage theorem. It is used because the checked phase diagnostics contain `parent_residue`, `old_component_count`, and close-row flags for the B4/B5/B6/B7 transition scopes.

The key `B4->B5` comparison is:

- `parent_mod6_proxy = 3`: `35` families, `14` single-gap, `21` multi-gap, `2` close rows.
- `parent_mod6_proxy = 2`: `34` families, `34` single-gap, `0` multi-gap, `6` close rows.
- `parent_mod6_proxy = 4`: `34` families, `34` single-gap, `0` multi-gap, `6` close rows.

The diagnostic reading is that `3 mod 6` is not simply unproductive at `B4->B5`; rather, much of its early proxy mass falls into multi-gap parents.

## Single-Gap Conditional Close Rate

The summary records both all-family close rate and single-gap conditional close rate. This separates two questions:

- How often does a proxy class close among all families?
- How often does it close after multi-gap parents are removed?

For `B4->B5`, `parent_mod6_proxy = 3` has `close_rate_all = 2/35` but `close_rate_given_single_gap = 2/14`. The latter is still not promoted to a theorem claim. It is a diagnostic that the weak all-family signal is partly explained by a smaller single-gap denominator.

For `B5->B6` and `B6->B7`, `parent_mod6_proxy = 3` remains enriched among close rows and is recorded as `single_gap_conditioned_enrichment_candidate`.

## Link To Special Point Obstruction

Special point obstruction removes special-remainder and endpoint-touch routes. The remaining birth candidates are expected to be strict interior single-gap rows.

This diagnostic supports that route by splitting `mod 6` ancestry proxy counts by parent component count. It suggests that the `B4->B5` exception is not a contradiction of the later `3 mod 6` enrichment story; it may be the first transition where many `3 mod 6` proxy families have not yet survived into productive single-gap form.

## Diagnostic Decision

`diagnostic=continue`

`k2_multigap_dilution=continue`

`mod6_theorem=defer`

`mod6_predictor=reject_for_v2_6_gate_r`

`public_theorem=defer`

Decision: continue `k=2 multi-gap dilution` as a Gate R diagnostic only.

## Non-claims

This note makes no theorem claim, no predictor claim, no public theorem claim, no DOI claim, no GitHub Release claim, no B8 theorem claim, no B8 full graph claim, and no asymptotic law claim.

It also makes no proven ancestry-lineage claim. `parent_residue % 6` is a checked-scope ancestry proxy, not a theorem that determines birth.
