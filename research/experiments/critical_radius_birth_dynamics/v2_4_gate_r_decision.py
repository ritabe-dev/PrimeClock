"""Source-only Gate R decision table for PRC v2.4."""

from __future__ import annotations

import csv
import math
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

from tools import first_primes, format_fraction, primorial, residue_uncovered_measure
from v2_4_phase_gate_diagnostics import (
    read_phase_gate_family_summary_csv,
    read_phase_gate_lift_diagnostics_csv,
)
from v2_4_residual_genealogy import read_birth_residual_genealogy_csv

EXPERIMENT_DIR = Path(__file__).resolve().parent
DEFAULT_GATE_R_DECISION_TABLE_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_gate_r_decision_table_v0_1.csv"
)
DEFAULT_ARITHMETIC_STRATUM_BIAS_CSV = (
    EXPERIMENT_DIR / "data" / "prc_v2_4_arithmetic_stratum_bias_v0_1.csv"
)


@dataclass(frozen=True)
class GateRDecisionRow:
    candidate: str
    role: str
    visually_obvious_score: int
    definition_restatement_score: int
    persistence_score: int
    arithmetic_content_score: int
    checker_backed_score: int
    paper_section_score: int
    decision: str
    evidence: str
    reason: str


@dataclass(frozen=True)
class ArithmeticStratumBiasRow:
    diagnostic: str
    scope: str
    population: str
    stratum_kind: str
    stratum: str
    family_count: int
    lift_count: int
    close_count: int
    birth_count: int
    close_rate: str
    birth_rate: str
    observed_share: str
    note: str


def build_arithmetic_stratum_bias_rows() -> list[ArithmeticStratumBiasRow]:
    """Build capacity-conditioned arithmetic and reflection diagnostics."""
    family_rows = read_phase_gate_family_summary_csv()
    lift_rows = read_phase_gate_lift_diagnostics_csv()
    rows: list[ArithmeticStratumBiasRow] = _k2_width_normalized_lineage_rows()

    aggregate_family_populations = {
        "all": family_rows,
        "capacity": [row for row in family_rows if row.capacity_pass],
        "capacity_nonclose": [
            row for row in family_rows if row.capacity_pass and row.close_lift_count == 0
        ],
        "close": [row for row in family_rows if row.close_lift_count > 0],
    }
    for population, population_rows in aggregate_family_populations.items():
        rows.extend(_parent_gcd_rows("all", population, population_rows))
    rows.extend(_k2_capacity_survival_rows("all", family_rows))

    for scope in _scopes(family_rows):
        scoped_families = [row for row in family_rows if row.scope == scope]
        family_populations = {
            "all": scoped_families,
            "capacity": [row for row in scoped_families if row.capacity_pass],
            "capacity_nonclose": [
                row for row in scoped_families if row.capacity_pass and row.close_lift_count == 0
            ],
            "close": [row for row in scoped_families if row.close_lift_count > 0],
        }
        for population, population_rows in family_populations.items():
            rows.extend(_parent_gcd_rows(scope, population, population_rows))
        rows.extend(_k2_capacity_survival_rows(scope, scoped_families))

        scoped_lifts = [row for row in lift_rows if row.scope == scope]
        close_lifts = [row for row in scoped_lifts if row.is_close]
        rows.extend(_child_gcd_rows(scope, close_lifts))
        rows.extend(_reflection_pair_rows(scope, close_lifts))
        rows.extend(_gcd_reflection_pair_rows(scope, close_lifts))

    return sorted(
        rows,
        key=lambda row: (
            row.diagnostic,
            row.scope,
            row.population,
            row.stratum_kind,
            _natural_stratum_key(row.stratum),
        ),
    )


def build_gate_r_decision_rows(
    arithmetic_rows: Iterable[ArithmeticStratumBiasRow] | None = None,
) -> list[GateRDecisionRow]:
    """Return the fixed v2.4 Gate R candidate-selection table."""
    rows = list(arithmetic_rows) if arithmetic_rows is not None else build_arithmetic_stratum_bias_rows()
    k2_width_evidence = _k2_width_evidence(rows)
    k2_capacity_evidence = _k2_capacity_evidence(rows)
    reflection_evidence = _reflection_pair_evidence(rows)
    cross_evidence = _gcd_pair_cross_evidence(rows)
    return [
        GateRDecisionRow(
            candidate="capacity + phase gate",
            role="foundation",
            visually_obvious_score=5,
            definition_restatement_score=4,
            persistence_score=5,
            arithmetic_content_score=1,
            checker_backed_score=5,
            paper_section_score=2,
            decision="weak",
            evidence="capacity_close=770;capacity_nonclose=2430;phase_pass_nonclose=0",
            reason="correct and useful as a guard, but too visually obvious for the headline claim",
        ),
        GateRDecisionRow(
            candidate="signed phase-margin separation theorem",
            role="headline theorem candidate",
            visually_obvious_score=3,
            definition_restatement_score=2,
            persistence_score=5,
            arithmetic_content_score=2,
            checker_backed_score=5,
            paper_section_score=5,
            decision="keep",
            evidence="close=770/770;capacity_nonclose=2430;phase_pass_nonclose=0;close_rank_1=770/770",
            reason=(
                "positive signed containment margin is the checked finite separator "
                "across B4->B5, B5->B6, and B6->B7 sibling-lift families"
            ),
        ),
        GateRDecisionRow(
            candidate="sibling itinerary divergence",
            role="explanatory support",
            visually_obvious_score=3,
            definition_restatement_score=2,
            persistence_score=4,
            arithmetic_content_score=2,
            checker_backed_score=5,
            paper_section_score=3,
            decision="support",
            evidence="birth_siblings=770;nonbirth_siblings=12068;nonbirth_sequences=23",
            reason="useful for explaining last-step divergence, but weaker than the arithmetic bias story",
        ),
        GateRDecisionRow(
            candidate="width-normalized k2 r=3 lineage survival bias",
            role="arithmetic refinement",
            visually_obvious_score=1,
            definition_restatement_score=1,
            persistence_score=4,
            arithmetic_content_score=5,
            checker_backed_score=5,
            paper_section_score=4,
            decision="support",
            evidence=f"{k2_width_evidence};{k2_capacity_evidence}",
            reason=(
                "gcd=3 is too coarse; the checked signal is k=2 r=3 lineage "
                "survival after inverse-width and capacity conditioning, as a refinement"
            ),
        ),
        GateRDecisionRow(
            candidate="reflection-paired final remainder bias",
            role="arithmetic refinement",
            visually_obvious_score=2,
            definition_restatement_score=1,
            persistence_score=4,
            arithmetic_content_score=4,
            checker_backed_score=5,
            paper_section_score=3,
            decision="support",
            evidence=f"{reflection_evidence};{cross_evidence}",
            reason=(
                "reflection symmetry is a guard, but concentration into specific "
                "reflected pairs is a refinement inside the phase-separated close set"
            ),
        ),
    ]


def _k2_width_normalized_lineage_rows() -> list[ArithmeticStratumBiasRow]:
    genealogy_rows = read_birth_residual_genealogy_csv()
    layer_rows = [row for row in genealogy_rows if row.layer_k == 2]
    total = len(layer_rows)
    counts = Counter(row.layer_residue for row in layer_rows)
    widths = {residue: residue_uncovered_measure(residue, first_primes(2)) for residue in range(6)}
    inverse_weights = {
        residue: Fraction(1, 1) / width
        for residue, width in widths.items()
        if width > 0
    }
    inverse_total = sum(inverse_weights.values(), Fraction(0, 1))

    rows: list[ArithmeticStratumBiasRow] = []
    for residue in range(6):
        observed = counts[residue]
        expected = Fraction(total, 1) * inverse_weights[residue] / inverse_total
        observed_over_expected = (
            Fraction(observed, 1) / expected if expected else Fraction(0, 1)
        )
        rows.append(
            ArithmeticStratumBiasRow(
                diagnostic="k2_width_normalized_lineage_survival",
                scope="all",
                population="birth_lineage",
                stratum_kind="k2_residue_mod_6",
                stratum=f"r={residue}",
                family_count=observed,
                lift_count=total,
                close_count=observed,
                birth_count=observed,
                close_rate=format_fraction(observed_over_expected),
                birth_rate=_format_ratio(observed, total),
                observed_share=format_fraction(expected),
                note=(
                    f"width={format_fraction(widths[residue])};"
                    f"inverse_width_expected={format_fraction(expected)};"
                    "close_rate stores observed_over_inverse_width_expected"
                ),
            )
        )
    return rows


def _k2_capacity_survival_rows(scope: str, family_rows) -> list[ArithmeticStratumBiasRow]:
    capacity_rows = [row for row in family_rows if row.capacity_pass]
    total_capacity = len(capacity_rows)
    by_residue: dict[int, list[object]] = {residue: [] for residue in range(6)}
    for row in capacity_rows:
        by_residue[row.parent_residue % 6].append(row)

    rows: list[ArithmeticStratumBiasRow] = []
    for residue in range(6):
        stratum_rows = by_residue[residue]
        family_count = len(stratum_rows)
        close_count = sum(row.close_lift_count > 0 for row in stratum_rows)
        birth_count = sum(row.birth_lift_count > 0 for row in stratum_rows)
        lift_count = sum(row.lift_count for row in stratum_rows)
        rows.append(
            ArithmeticStratumBiasRow(
                diagnostic="k2_capacity_conditioned_survival",
                scope=scope,
                population="capacity",
                stratum_kind="k2_residue_mod_6",
                stratum=f"r={residue}",
                family_count=family_count,
                lift_count=lift_count,
                close_count=close_count,
                birth_count=birth_count,
                close_rate=_format_ratio(close_count, family_count),
                birth_rate=_format_ratio(birth_count, family_count),
                observed_share=_format_ratio(family_count, total_capacity),
                note="capacity-conditioned k=2 residue lineage; not a raw gcd claim",
            )
        )
    return rows


def write_gate_r_decision_artifacts(
    *,
    decision_path: str | Path = DEFAULT_GATE_R_DECISION_TABLE_CSV,
    arithmetic_path: str | Path = DEFAULT_ARITHMETIC_STRATUM_BIAS_CSV,
) -> None:
    arithmetic_rows = build_arithmetic_stratum_bias_rows()
    decision_rows = build_gate_r_decision_rows(arithmetic_rows)
    write_dataclass_csv(arithmetic_rows, arithmetic_path, ArithmeticStratumBiasRow)
    write_dataclass_csv(decision_rows, decision_path, GateRDecisionRow)


def read_gate_r_decision_table_csv(
    path: str | Path = DEFAULT_GATE_R_DECISION_TABLE_CSV,
) -> list[GateRDecisionRow]:
    return _read_dataclass_csv(path, GateRDecisionRow)


def read_arithmetic_stratum_bias_csv(
    path: str | Path = DEFAULT_ARITHMETIC_STRATUM_BIAS_CSV,
) -> list[ArithmeticStratumBiasRow]:
    return _read_dataclass_csv(path, ArithmeticStratumBiasRow)


def row_signature(row: object) -> tuple[object, ...]:
    return tuple(getattr(row, field) for field in row.__dataclass_fields__)


def write_dataclass_csv(rows: Iterable[object], output_path: str | Path, row_type: type) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(row_type.__dataclass_fields__.keys())
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fieldnames})


def _parent_gcd_rows(
    scope: str,
    population: str,
    family_rows,
) -> list[ArithmeticStratumBiasRow]:
    total_families = len(family_rows)
    total_lifts = sum(row.lift_count for row in family_rows)
    by_gcd: dict[int, list[object]] = {}
    for row in family_rows:
        row_scope = row.scope if scope == "all" else scope
        parent_modulus = primorial(first_primes(_parent_k_from_scope(row_scope)))
        by_gcd.setdefault(math.gcd(row.parent_residue, parent_modulus), []).append(row)

    rows: list[ArithmeticStratumBiasRow] = []
    for gcd_value, stratum_rows in sorted(by_gcd.items()):
        family_count = len(stratum_rows)
        close_count = sum(row.close_lift_count > 0 for row in stratum_rows)
        birth_count = sum(row.birth_lift_count > 0 for row in stratum_rows)
        lift_count = sum(row.lift_count for row in stratum_rows)
        rows.append(
            ArithmeticStratumBiasRow(
                diagnostic="parent_gcd_capacity_conditioned",
                scope=scope,
                population=population,
                stratum_kind="parent_gcd",
                stratum=f"gcd={gcd_value}",
                family_count=family_count,
                lift_count=lift_count,
                close_count=close_count,
                birth_count=birth_count,
                close_rate=_format_ratio(close_count, family_count),
                birth_rate=_format_ratio(birth_count, family_count),
                observed_share=_format_ratio(family_count, total_families),
                note=(
                    "capacity-conditioned parent gcd stratum; gcd>1 is not a standalone claim"
                    if population == "capacity"
                    else "parent gcd stratum"
                ),
            )
        )
    if total_families == 0:
        rows.append(
            ArithmeticStratumBiasRow(
                diagnostic="parent_gcd_capacity_conditioned",
                scope=scope,
                population=population,
                stratum_kind="parent_gcd",
                stratum="empty",
                family_count=0,
                lift_count=total_lifts,
                close_count=0,
                birth_count=0,
                close_rate="0",
                birth_rate="0",
                observed_share="0",
                note="empty population",
            )
        )
    return rows


def _child_gcd_rows(scope: str, close_lifts) -> list[ArithmeticStratumBiasRow]:
    child_modulus = primorial(first_primes(_child_k_from_scope(scope)))
    total = len(close_lifts)
    by_gcd: Counter[int] = Counter(
        math.gcd(row.child_residue, child_modulus) for row in close_lifts
    )
    return [
        ArithmeticStratumBiasRow(
            diagnostic="close_child_gcd_by_scope",
            scope=scope,
            population="close",
            stratum_kind="child_gcd",
            stratum=f"gcd={gcd_value}",
            family_count=count,
            lift_count=count,
            close_count=count,
            birth_count=count,
            close_rate="1",
            birth_rate="1",
            observed_share=_format_ratio(count, total),
            note="final child gcd among close/birth lifts",
        )
        for gcd_value, count in sorted(by_gcd.items())
    ]


def _reflection_pair_rows(scope: str, close_lifts) -> list[ArithmeticStratumBiasRow]:
    q = close_lifts[0].new_prime if close_lifts else _new_prime_from_scope(scope)
    pair_counts = Counter(_reflection_pair_key(row.new_prime_remainder, q) for row in close_lifts)
    remainder_counts = Counter(row.new_prime_remainder for row in close_lifts)
    total = len(close_lifts)
    rows = []
    for pair, count in sorted(pair_counts.items(), key=lambda item: (-item[1], item[0])):
        left, right = (int(part) for part in pair.split("/"))
        imbalance = abs(remainder_counts[left] - remainder_counts[right])
        rows.append(
            ArithmeticStratumBiasRow(
                diagnostic="close_reflection_pair_by_scope",
                scope=scope,
                population="close",
                stratum_kind="reflection_pair",
                stratum=pair,
                family_count=count,
                lift_count=count,
                close_count=count,
                birth_count=count,
                close_rate="1",
                birth_rate="1",
                observed_share=_format_ratio(count, total),
                note=f"pair_imbalance={imbalance}",
            )
        )
    return rows


def _gcd_reflection_pair_rows(scope: str, close_lifts) -> list[ArithmeticStratumBiasRow]:
    child_modulus = primorial(first_primes(_child_k_from_scope(scope)))
    q = close_lifts[0].new_prime if close_lifts else _new_prime_from_scope(scope)
    counts = Counter(
        (
            math.gcd(row.child_residue, child_modulus),
            _reflection_pair_key(row.new_prime_remainder, q),
        )
        for row in close_lifts
    )
    total = len(close_lifts)
    return [
        ArithmeticStratumBiasRow(
            diagnostic="close_child_gcd_reflection_pair_crosstab",
            scope=scope,
            population="close",
            stratum_kind="child_gcd_reflection_pair",
            stratum=f"gcd={gcd_value};pair={pair}",
            family_count=count,
            lift_count=count,
            close_count=count,
            birth_count=count,
            close_rate="1",
            birth_rate="1",
            observed_share=_format_ratio(count, total),
            note="close/birth arithmetic stratum and final remainder pair",
        )
        for (gcd_value, pair), count in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0][0], item[0][1]),
        )
    ]


def _parent_gcd_shift_evidence(rows: list[ArithmeticStratumBiasRow]) -> str:
    capacity = _top_stratum(rows, "parent_gcd_capacity_conditioned", "all", "capacity")
    close = _top_stratum(rows, "parent_gcd_capacity_conditioned", "all", "close")
    return f"capacity_top={capacity};close_top={close}"


def _k2_width_evidence(rows: list[ArithmeticStratumBiasRow]) -> str:
    r3 = _row_for(
        rows,
        "k2_width_normalized_lineage_survival",
        "all",
        "birth_lineage",
        "r=3",
    )
    return (
        "k2_width_norm="
        f"r3_observed={r3.family_count};"
        f"r3_inverse_width_obs_expected={r3.close_rate};"
        f"{r3.note}"
    )


def _k2_capacity_evidence(rows: list[ArithmeticStratumBiasRow]) -> str:
    r2 = _row_for(rows, "k2_capacity_conditioned_survival", "all", "capacity", "r=2")
    r3 = _row_for(rows, "k2_capacity_conditioned_survival", "all", "capacity", "r=3")
    r4 = _row_for(rows, "k2_capacity_conditioned_survival", "all", "capacity", "r=4")
    return (
        "k2_capacity_survival="
        f"r2_close_rate={r2.close_rate};"
        f"r3_close_rate={r3.close_rate};"
        f"r4_close_rate={r4.close_rate}"
    )


def _reflection_pair_evidence(rows: list[ArithmeticStratumBiasRow]) -> str:
    top_by_scope = [
        _top_stratum(rows, "close_reflection_pair_by_scope", scope, "close")
        for scope in ("B4_to_B5_full", "B5_to_B6_full", "B6_to_B7_full")
    ]
    return "top_pairs=" + "|".join(top_by_scope)


def _gcd_pair_cross_evidence(rows: list[ArithmeticStratumBiasRow]) -> str:
    top = _top_stratum(
        rows,
        "close_child_gcd_reflection_pair_crosstab",
        "B6_to_B7_full",
        "close",
    )
    return f"B7_top_gcd_pair={top}"


def _row_for(
    rows: list[ArithmeticStratumBiasRow],
    diagnostic: str,
    scope: str,
    population: str,
    stratum: str,
) -> ArithmeticStratumBiasRow:
    for row in rows:
        if (
            row.diagnostic == diagnostic
            and row.scope == scope
            and row.population == population
            and row.stratum == stratum
        ):
            return row
    raise ValueError(f"missing diagnostic row: {diagnostic} {scope} {population} {stratum}")


def _top_stratum(
    rows: list[ArithmeticStratumBiasRow],
    diagnostic: str,
    scope: str,
    population: str,
) -> str:
    subset = [
        row
        for row in rows
        if row.diagnostic == diagnostic
        and row.scope == scope
        and row.population == population
        and row.stratum != "empty"
    ]
    if not subset:
        return "none"
    top = max(subset, key=lambda row: (row.family_count, row.stratum))
    return f"{scope}:{top.stratum}:{top.family_count}:{top.observed_share}"


def _scopes(rows: Iterable[object]) -> list[str]:
    return sorted({row.scope for row in rows})


def _parent_k_from_scope(scope: str) -> int:
    if scope.startswith("B4"):
        return 4
    if scope.startswith("B5"):
        return 5
    if scope.startswith("B6"):
        return 6
    raise ValueError(f"unsupported scope: {scope}")


def _child_k_from_scope(scope: str) -> int:
    return _parent_k_from_scope(scope) + 1


def _new_prime_from_scope(scope: str) -> int:
    return first_primes(_child_k_from_scope(scope))[-1]


def _reflection_pair_key(remainder: int, q: int) -> str:
    reflected = (-remainder) % q
    left, right = sorted((remainder, reflected))
    return f"{left}/{right}"


def _format_ratio(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0"
    return format_fraction(Fraction(numerator, denominator))


def _natural_stratum_key(stratum: str) -> tuple[int, str]:
    if stratum.startswith("gcd="):
        return (int(stratum.split("=", 1)[1].split(";", 1)[0]), stratum)
    return (0, stratum)


def _read_dataclass_csv(path: str | Path, row_type: type):
    int_fields = {
        "visually_obvious_score",
        "definition_restatement_score",
        "persistence_score",
        "arithmetic_content_score",
        "checker_backed_score",
        "paper_section_score",
        "family_count",
        "lift_count",
        "close_count",
        "birth_count",
    }
    rows = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for raw_row in csv.DictReader(handle):
            values = dict(raw_row)
            for field in int_fields:
                if field in values:
                    values[field] = int(values[field])
            rows.append(row_type(**values))
    return rows
