#!/usr/bin/env python3
"""Verify source-only PRC v2.4 five-cycle research synthesis artifacts."""

from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from v2_4_five_cycle_synthesis import (
    DEFAULT_HYPOTHESIS_SCOREBOARD_CSV,
    DEFAULT_MATCHED_CONTROL_CSV,
    DEFAULT_R3_FACTOR_FORENSICS_NOTE,
    DEFAULT_SCOREBOARD_FIGURE,
    DEFAULT_SYNTHESIS_NOTE,
    build_hypothesis_scoreboard_rows,
    build_matched_control_rows,
    read_hypothesis_scoreboard_csv,
    read_matched_control_csv,
    row_signature,
    write_five_cycle_artifacts,
)


DEFAULT_OUT = (
    Path(tempfile.gettempdir())
    / "prc_v2_4_five_cycle_research_synthesis_verification_v0_1.csv"
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify source-only PRC v2.4 five-cycle synthesis artifacts.",
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUT,
        type=Path,
        help="verification summary CSV path",
    )
    parser.add_argument(
        "--update-data",
        action="store_true",
        help="regenerate committed source-only synthesis artifacts",
    )
    args = parser.parse_args()

    if args.update_data:
        write_five_cycle_artifacts()

    checks = verification_rows()
    write_checks(checks, args.out)
    failed = sum(int(row["failed"]) for row in checks)
    print(
        "check_v2_4_five_cycle_research_synthesis: "
        f"checks={len(checks)}, failed={failed}, out={args.out}"
    )
    return 0 if failed == 0 else 1


def verification_rows() -> list[dict[str, str]]:
    scoreboard_rows = read_hypothesis_scoreboard_csv(DEFAULT_HYPOTHESIS_SCOREBOARD_CSV)
    matched_rows = read_matched_control_csv(DEFAULT_MATCHED_CONTROL_CSV)
    note_text = DEFAULT_SYNTHESIS_NOTE.read_text(encoding="utf-8")
    r3_note_text = DEFAULT_R3_FACTOR_FORENSICS_NOTE.read_text(encoding="utf-8")
    return [
        compare_recomputed_rows(
            "hypothesis_scoreboard_rows_match_recomputed",
            scoreboard_rows,
            build_hypothesis_scoreboard_rows(),
        ),
        compare_recomputed_rows(
            "matched_control_rows_match_recomputed",
            matched_rows,
            build_matched_control_rows(),
        ),
        check_scoreboard_content(scoreboard_rows),
        check_matched_control_content(matched_rows),
        check_synthesis_note_boundaries(note_text),
        check_r3_factor_forensics_note(r3_note_text),
        check_figure_exists(DEFAULT_SCOREBOARD_FIGURE),
    ]


def compare_recomputed_rows(name: str, committed_rows, recomputed_rows) -> dict[str, str]:
    committed = [row_signature(row) for row in committed_rows]
    recomputed = [row_signature(row) for row in recomputed_rows]
    mismatches = sum(left != right for left, right in zip(committed, recomputed))
    mismatches += abs(len(committed) - len(recomputed))
    return check_bool(
        name,
        committed == recomputed,
        total=max(len(committed), len(recomputed)),
        failed=mismatches,
    )


def check_scoreboard_content(rows) -> dict[str, str]:
    cycles = {row.cycle for row in rows}
    hypotheses = {row.hypothesis for row in rows}
    statuses = {row.status for row in rows}
    passed = (
        cycles == {1, 2, 3, 4, 5}
        and len(rows) == 26
        and "reflection-orbit symmetry survives the broad v2.4 diagnostics"
        in hypotheses
        and "final checked birth rows live on nonunit residue strata" in hypotheses
        and "genealogy paths form multiple grammars rather than one template"
        in hypotheses
        and "local transition dynamics remain rich away from final birth rows"
        in hypotheses
        and "final aperture margins are positive but layer-dependent" in hypotheses
        and "sibling-lift controls show close is phase-selective in scoped probes"
        in hypotheses
        and "transition itinerary controls compare birth siblings against non-birth siblings"
        in hypotheses
        and "exact residual lineage atlas supports capacity gate plus sibling phase gate"
        in hypotheses
        and "signed phase-margin separation selects the closing sibling" in hypotheses
        and "k=2 inverse_width potential predicts birth-lineage counts" in hypotheses
        and "inverse_width is useful but not sufficient" in hypotheses
        and "Gate R story should remain continue research" in hypotheses
        and "Gate R decision table promotes signed phase-margin separation and demotes obvious mechanisms"
        in hypotheses
        and {"supported", "partial", "weak"}.issubset(statuses)
    )
    failed = 0 if passed else 1
    return check_bool("hypothesis_scoreboard_content", passed, total=6, failed=failed)


def check_matched_control_content(rows) -> dict[str, str]:
    groups = {row.diagnostic_group for row in rows}
    passed = (
        len(rows) == 12
        and "same_width_neighbors" in groups
        and "wide_zero_side_controls" in groups
        and "model_failure" in groups
        and "reflection_control" in groups
        and "path_diversity_control" in groups
        and "prime_zero_control" in groups
        and "sibling_lift_control" in groups
        and "itinerary_nonbirth_control" in groups
        and "independent_phase_gate_control" in groups
        and "gate_r_selection_control" in groups
        and "non_claim_boundary" in groups
    )
    failed = 0 if passed else 1
    return check_bool("matched_control_content", passed, total=9, failed=failed)


def check_synthesis_note_boundaries(note_text: str) -> dict[str, str]:
    required = [
        "continue research",
        "early narrow residual potential + lineage survival + incremental q-grid phase alignment",
        "Reflection symmetry is a guard",
        "genealogy paths are diverse",
        "No claim that width alone explains birth.",
        "No claim that prime-zero side-gap creation explains all births.",
        "The exact residual lineage atlas makes the current Gate R mechanism visible",
        "The independent phase-gate diagnostic makes that selection non-circular",
        "The Gate R decision table switches this line from exploration to selection",
        "B6->B7 full transition graph is source-only, not a public claim.",
    ]
    passed = all(text in note_text for text in required)
    failed = sum(text not in note_text for text in required)
    return check_bool("synthesis_note_boundaries", passed, total=len(required), failed=failed)


def check_r3_factor_forensics_note(note_text: str) -> dict[str, str]:
    required = [
        "556 / (5775/26)",
        "14456/5775",
        "2.503203",
        "inverse_width",
        "total inverse weight = 104/5",
        "770 * 6 / (104/5)",
        "width-normalized lineage-survival bias",
        "not a standalone width-only mechanism",
    ]
    passed = all(text in note_text for text in required)
    failed = sum(text not in note_text for text in required)
    return check_bool("r3_factor_forensics_note", passed, total=len(required), failed=failed)


def check_figure_exists(path: Path) -> dict[str, str]:
    passed = path.exists() and path.stat().st_size > 1000
    return check_bool("synthesis_figure_exists", passed, total=1, failed=0 if passed else 1)


def check_bool(name: str, passed: bool, *, total: int, failed: int) -> dict[str, str]:
    return {
        "check": name,
        "total": str(total),
        "passed": str(max(total - failed, 0)),
        "failed": str(failed),
        "status": "pass" if passed else "fail",
    }


def write_checks(rows: list[dict[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["check", "total", "passed", "failed", "status"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
