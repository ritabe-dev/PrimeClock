from pathlib import Path

import pytest

from prime_reciprocal_projection.cli import main
from prime_reciprocal_projection.covering_prime_prefix_certificates import (
    NO_PREFIX_CERTIFICATE_STATUS,
    PREFIX_CERTIFICATE_STATUS,
    prime_prefix_certificate_rows,
    prime_prefix_certificate_rows_from_runs_csv,
    prime_prefix_certificate_summary_rows,
    prime_prefix_uncertified_mod210_summary_rows,
    prime_prefix_uncertified_overall_summary_rows,
    prime_prefix_uncertified_residue_rows,
    read_prime_prefix_certificate_csv,
    write_prime_prefix_certificate_csv,
    write_prime_prefix_certificate_summary_csv,
    write_prime_prefix_uncertified_mod210_summary_csv,
    write_prime_prefix_uncertified_overall_summary_csv,
    write_prime_prefix_uncertified_residue_csv,
)


def test_prime_prefix_certificate_depth_known_values():
    rows = prime_prefix_certificate_rows([118, 208], max_k=7)
    by_n = {row.n: row for row in rows}

    assert by_n[208].k_cert == 4
    assert by_n[208].p_cert == 7
    assert by_n[208].primorial_cert == 210
    assert by_n[208].residue_cert == 208
    assert by_n[208].trivial_c4_certificate is True

    assert by_n[118].k_cert == 5
    assert by_n[118].p_cert == 11
    assert by_n[118].primorial_cert == 2310
    assert by_n[118].residue_cert == 118
    assert by_n[118].trivial_c4_certificate is False


def test_prime_prefix_certificate_requires_prefix_prime_not_exceeding_n():
    row = prime_prefix_certificate_rows([2], max_k=7)[0]
    assert row.certificate_status == NO_PREFIX_CERTIFICATE_STATUS
    assert row.k_cert is None
    assert row.p_cert is None
    assert row.primorial_cert is None
    assert row.residue_cert is None


def test_prime_prefix_certificate_summary_groups_counts():
    rows = prime_prefix_certificate_rows([2, 118, 208], max_k=7)
    summary = prime_prefix_certificate_summary_rows(rows)

    assert [(row.certificate_status, row.k_cert, row.complete_count) for row in summary] == [
        (PREFIX_CERTIFICATE_STATUS, 4, 1),
        (PREFIX_CERTIFICATE_STATUS, 5, 1),
        (NO_PREFIX_CERTIFICATE_STATUS, None, 1),
    ]
    assert sum(row.complete_count for row in summary) == len(rows)
    assert sum(row.share_of_complete for row in summary) == pytest.approx(1.0)


def test_prime_prefix_certificate_csv_headers(tmp_path: Path):
    rows = prime_prefix_certificate_rows([2, 208], max_k=7)
    summary = prime_prefix_certificate_summary_rows(rows)
    detail_out = tmp_path / "detail.csv"
    summary_out = tmp_path / "summary.csv"

    write_prime_prefix_certificate_csv(rows, detail_out)
    write_prime_prefix_certificate_summary_csv(summary, summary_out)

    assert detail_out.read_text(encoding="utf-8").splitlines()[0] == (
        "n,k_cert,p_cert,primorial_cert,residue_cert,checked_max_k,"
        "checked_max_prime,certificate_status,mod210,trivial_c4_certificate"
    )
    assert summary_out.read_text(encoding="utf-8").splitlines()[0] == (
        "certificate_status,k_cert,p_cert,complete_count,share_of_complete,"
        "min_n,max_n,checked_max_k,checked_max_prime"
    )


def test_prime_prefix_certificate_rows_from_runs_csv(tmp_path: Path):
    source = tmp_path / "runs.csv"
    source.write_text("start,stop,length\n118,118,1\n208,208,1\n", encoding="utf-8")

    rows = prime_prefix_certificate_rows_from_runs_csv(source, max_k=7)

    assert [row.n for row in rows] == [118, 208]
    assert [row.k_cert for row in rows] == [5, 4]


def test_covering_prime_prefix_certificates_cli_writes_csvs(tmp_path: Path):
    source = tmp_path / "runs.csv"
    detail_out = tmp_path / "detail.csv"
    summary_out = tmp_path / "summary.csv"
    source.write_text("start,stop,length\n118,118,1\n208,208,1\n", encoding="utf-8")

    assert (
        main(
            [
                "covering-prime-prefix-certificates",
                "--complete-source",
                str(source),
                "--max-k",
                "7",
                "--out",
                str(detail_out),
                "--summary-out",
                str(summary_out),
            ]
        )
        == 0
    )
    assert len(detail_out.read_text(encoding="utf-8").splitlines()) == 3
    assert len(summary_out.read_text(encoding="utf-8").splitlines()) == 3


def test_covering_prime_prefix_certificates_cli_rejects_large_k_without_flag(
    tmp_path: Path,
):
    source = tmp_path / "runs.csv"
    source.write_text("start,stop,length\n118,118,1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="primorial-scale"):
        main(
            [
                "covering-prime-prefix-certificates",
                "--complete-source",
                str(source),
                "--max-k",
                "8",
                "--out",
                str(tmp_path / "detail.csv"),
                "--summary-out",
                str(tmp_path / "summary.csv"),
            ]
        )


def test_prime_prefix_uncertified_residue_profile_known_nearest_class(tmp_path: Path):
    certificate_rows = prime_prefix_certificate_rows([178, 208], max_k=4)
    detail_out = tmp_path / "certificates.csv"
    write_prime_prefix_certificate_csv(certificate_rows, detail_out)

    read_rows = read_prime_prefix_certificate_csv(detail_out)
    rows = prime_prefix_uncertified_residue_rows(read_rows, max_k=4)

    assert len(rows) == 1
    row = rows[0]
    assert row.n == 178
    assert row.residue_modulus == 210
    assert row.residue == 178
    assert row.nearest_covered_residue == 208
    assert row.nearest_covered_source_k == 4
    assert row.nearest_covered_source_prime == 7
    assert row.circular_residue_distance == 30
    assert row.normalized_residue_distance == pytest.approx(30 / 210)


def test_prime_prefix_uncertified_summaries_and_headers(tmp_path: Path):
    rows = prime_prefix_uncertified_residue_rows(
        prime_prefix_certificate_rows([178, 201, 208], max_k=4),
        max_k=4,
    )
    overall = prime_prefix_uncertified_overall_summary_rows(rows)
    mod210 = prime_prefix_uncertified_mod210_summary_rows(rows)
    detail_out = tmp_path / "uncertified.csv"
    overall_out = tmp_path / "overall.csv"
    mod210_out = tmp_path / "mod210.csv"

    write_prime_prefix_uncertified_residue_csv(rows, detail_out)
    write_prime_prefix_uncertified_overall_summary_csv(overall, overall_out)
    write_prime_prefix_uncertified_mod210_summary_csv(mod210, mod210_out)

    assert detail_out.read_text(encoding="utf-8").splitlines()[0] == (
        "n,checked_max_k,checked_max_prime,residue_modulus,residue,mod210,mod2310,"
        "nearest_covered_residue,nearest_covered_source_k,nearest_covered_source_prime,"
        "circular_residue_distance,normalized_residue_distance"
    )
    assert overall_out.read_text(encoding="utf-8").splitlines()[0] == "metric,value"
    assert mod210_out.read_text(encoding="utf-8").splitlines()[0] == (
        "mod210,uncertified_count,share_of_uncertified,nearest_distance_median,"
        "nearest_distance_max,sample_n"
    )
    assert any(row.metric == "uncertified_count" and row.value == "2" for row in overall)
    assert sum(row.uncertified_count for row in mod210) == 2


def test_covering_prime_prefix_uncertified_residues_cli_writes_csvs(tmp_path: Path):
    certificates = tmp_path / "certificates.csv"
    detail_out = tmp_path / "detail.csv"
    summary_out = tmp_path / "summary.csv"
    mod210_out = tmp_path / "mod210.csv"
    write_prime_prefix_certificate_csv(
        prime_prefix_certificate_rows([178, 208], max_k=4),
        certificates,
    )

    assert (
        main(
            [
                "covering-prime-prefix-uncertified-residues",
                "--certificates",
                str(certificates),
                "--max-k",
                "4",
                "--out",
                str(detail_out),
                "--summary-out",
                str(summary_out),
                "--mod210-out",
                str(mod210_out),
            ]
        )
        == 0
    )
    assert len(detail_out.read_text(encoding="utf-8").splitlines()) == 2
    assert len(summary_out.read_text(encoding="utf-8").splitlines()) == 10
    assert len(mod210_out.read_text(encoding="utf-8").splitlines()) == 2
