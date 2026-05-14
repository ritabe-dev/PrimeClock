# PRC v2.6 Mod 6 Ancestry Diagnostic v0.1

## Goal

Purpose: add a source-only v2.6 diagnostic that explains why `3 mod 6` ancestry is relevant to special point obstruction without turning it into a theorem, predictor, or public claim. Current v2.6 theorem-note readiness is about 97-99% after this diagnostic, with about 0.2-0.3 slice remaining before a Gate R checkpoint decision. The v2.5 public theorem release remains protected.

## k=2 Special Point Suppression

At `k=2`, the old prefix contains `p=2` and `p=3`. These two early clouds are the first layer that organizes the special points `0` and `1/2`.

The diagnostic reading is that `p=2,3` suppress the special-point sides early: `0` and `1/2` become boundary-controlled locations, so later birth candidates are expected to come from interior single-gap ancestry rather than from the special points themselves.

## Mod 6 Gap Geometry

Modulo `6`, the residue class `3 mod 6` is the central class between the even and `p=3` structure. It is not claimed to force birth. It is used as an ancestry marker for productive interior single-gap candidates after the special points have been suppressed.

This diagnostic is downstream of the special point obstruction theorem-note candidate. It does not prove the obstruction; it helps explain why later close rows may concentrate in one ancestry class.

## Checked-Scope Evidence

The committed `prc_v2_6_mod6_ancestry_summary_v0_1.csv` records an asymmetric signal:

- `B4_to_B5_full`: `B4->B5` is weak_or_non_supportive for `mod 6 = 3`, with close rows `2/14`.
- `B5_to_B6_full`: `B5->B6` is `mod 6 = 3` enriched, with close rows `32/42`.
- `B6_to_B7_full`: `B6->B7` is `mod 6 = 3` enriched, with close rows `522/714`.

This asymmetry is important. The diagnostic is not retrofitted into a universal theorem: the early checked transition is explicitly weak, while later checked scopes show enrichment.

## Link To Special Point Obstruction

Special point obstruction says that `0` and the two central remainders adjacent to `1/2` cannot be the birth source. The mod 6 ancestry diagnostic asks where productive interior single-gap candidates tend to come from after those special-point routes are removed.

The working interpretation is:

- special point obstruction removes endpoint and special-remainder routes;
- remaining productive rows are strict interior single-gap rows;
- `3 mod 6` becomes enriched in later checked close rows as an ancestry marker for those interior candidates.

## Diagnostic Decision

`diagnostic=continue`

`mod6_theorem=defer`

`mod6_predictor=reject_for_v2_6_gate_r`

`public_theorem=defer`

Decision: continue mod 6 ancestry as a Gate R diagnostic only.

## Non-claims

This note makes no theorem claim, no predictor claim, no public theorem claim, no DOI claim, no GitHub Release claim, no B8 theorem claim, no B8 full graph claim, and no asymptotic law claim.

