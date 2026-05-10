#!/usr/bin/env python3
"""Run reusable internal-candidate workflow gates.

The candidate workflow is intentionally non-publishing: it may build temporary
candidate packages, run checkers, and write reports, but it must not create a
GitHub Release, tag, or Zenodo archive.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only in missing deps envs.
    raise SystemExit(
        "PyYAML is required for candidate workflow configs. "
        "Install the research dev dependencies with: "
        'cd research && python -m pip install -e ".[dev]"'
    ) from exc


MODES = {
    "quick",
    "bundle",
    "slow",
    "artifact-freshness",
    "manifest-consistency",
    "promotion-readiness",
    "all",
}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError(f"candidate workflow config must be a mapping: {path}")
    return config


def format_value(value: Any, variables: dict[str, str]) -> Any:
    if isinstance(value, str):
        return value.format(**variables)
    if isinstance(value, list):
        return [format_value(item, variables) for item in value]
    if isinstance(value, dict):
        return {key: format_value(item, variables) for key, item in value.items()}
    return value


def resolve_path(repo_root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else repo_root / path


def run_command(
    command_config: dict[str, Any],
    *,
    repo_root: Path,
    variables: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    command = format_value(command_config["command"], variables)
    cwd_value = format_value(command_config.get("cwd", str(repo_root)), variables)
    cwd = resolve_path(repo_root, cwd_value)
    print(f"+ ({cwd}) {' '.join(command)}")
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    expected_stdout = command_config.get("expected_stdout")
    if expected_stdout and expected_stdout not in result.stdout:
        raise SystemExit(
            "command stdout did not contain expected text "
            f"{expected_stdout!r}: {' '.join(command)}"
        )
    return result


def run_gate(
    config: dict[str, Any],
    gate_name: str,
    *,
    repo_root: Path,
    variables: dict[str, str],
) -> None:
    gate = config.get("gates", {}).get(gate_name)
    if not gate:
        raise SystemExit(f"candidate workflow config missing gate: {gate_name}")
    print(f"candidate gate: {gate_name}")
    for command_config in gate.get("commands", []):
        run_command(command_config, repo_root=repo_root, variables=variables)


def check_artifact_freshness(
    config: dict[str, Any],
    *,
    repo_root: Path,
    variables: dict[str, str],
) -> None:
    failures: list[str] = []
    for item in config.get("artifact_freshness", []):
        rendered = format_value(item, variables)
        output_path = resolve_path(repo_root, rendered["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        run_command(rendered, repo_root=repo_root, variables=variables)
        committed_path = resolve_path(repo_root, rendered["committed"])
        if not output_path.is_file():
            failures.append(f"{item['name']}: missing generated output {output_path}")
            continue
        if not committed_path.is_file():
            failures.append(f"{item['name']}: missing committed output {committed_path}")
            continue
        if output_path.read_bytes() != committed_path.read_bytes():
            failures.append(
                f"{item['name']}: generated output differs from committed artifact "
                f"{committed_path}"
            )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print("candidate artifact freshness check passed")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected YAML mapping: {path}")
    return data


def experiment_relative(
    repo_relative_path: str,
    experiment_dir: str,
) -> str | None:
    prefix = f"{experiment_dir.rstrip('/')}/"
    if repo_relative_path.startswith(prefix):
        return repo_relative_path[len(prefix) :]
    return None


def bundle_experiment_sources(bundle_manifest: dict[str, Any], experiment_dir: str) -> set[str]:
    sources: set[str] = set()
    for entry in bundle_manifest.get("root_file_map", []):
        relative = experiment_relative(entry["source"], experiment_dir)
        if relative:
            sources.add(relative)
    for path in bundle_manifest.get("research_files", []):
        relative = experiment_relative(path, experiment_dir)
        if relative:
            sources.add(relative)
    return sources


def load_standalone_expected_hash_paths(path: Path) -> set[str]:
    spec = importlib.util.spec_from_file_location("candidate_standalone_checker", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load standalone checker: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return set(module.EXPECTED_HASH_PATHS)


def check_manifest_consistency(config: dict[str, Any], *, repo_root: Path) -> None:
    paths = config["paths"]
    experiment_dir = paths["experiment_dir"]
    manifest_config = config["manifest_consistency"]
    experiment_manifest = load_yaml(resolve_path(repo_root, paths["experiment_manifest"]))
    bundle_manifest = load_json(resolve_path(repo_root, paths["bundle_manifest"]))

    included_key = manifest_config["included_artifacts_key"]
    excluded_key = manifest_config["excluded_artifacts_key"]
    included = set(experiment_manifest.get(included_key, []))
    excluded = set(experiment_manifest.get(excluded_key, []))
    expected_excluded = set(manifest_config.get("excluded_internal_notes", []))
    bundled_sources = bundle_experiment_sources(bundle_manifest, experiment_dir)

    failures: list[str] = []
    for path in sorted(expected_excluded - excluded):
        failures.append(f"excluded internal note missing from manifest: {path}")
    for path in sorted(excluded - expected_excluded):
        failures.append(f"unexpected excluded internal note in manifest: {path}")
    for path in sorted(excluded & bundled_sources):
        failures.append(f"excluded internal note is bundled: {path}")
    for path in sorted(included - bundled_sources):
        failures.append(f"manifest artifact is not bundled: {path}")
    for path in sorted(bundled_sources - included):
        failures.append(f"bundled experiment source missing from manifest artifacts: {path}")

    configured_hash_paths = set(manifest_config.get("expected_hash_paths", []))
    standalone_hash_paths = load_standalone_expected_hash_paths(
        resolve_path(repo_root, paths["standalone_checker"])
    )
    if configured_hash_paths != standalone_hash_paths:
        for path in sorted(configured_hash_paths - standalone_hash_paths):
            failures.append(f"configured hash path missing from standalone checker: {path}")
        for path in sorted(standalone_hash_paths - configured_hash_paths):
            failures.append(f"standalone checker hash path missing from config: {path}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print("candidate manifest consistency check passed")


def write_promotion_readiness_report(
    config: dict[str, Any],
    *,
    report_path: Path | None,
) -> None:
    policy = config["promotion_policy"]
    readiness = config.get("readiness", {})
    lines = [
        f"# Candidate Promotion Readiness: {config['candidate_id']}",
        "",
        f"- Status: {config['status']}",
        f"- Public release allowed: {policy['public_release_allowed']}",
        f"- Zenodo allowed: {policy['zenodo_allowed']}",
        f"- Base public release: {config['base_public_release']}",
        f"- Workflow reuse target: {readiness.get('reusable_workflow_percent', 'unknown')}%",
        f"- Estimated slices to target: {readiness.get('estimated_slices_to_target', 'unknown')}",
        "",
        "## Goal",
        "",
        config.get("goal", "No goal recorded."),
        "",
        "## Promotion Blockers",
        "",
    ]
    lines.extend(f"- {blocker}" for blocker in policy.get("blockers", []))
    lines.extend(
        [
            "",
            "## Publication Boundary",
            "",
            "This candidate workflow is non-publishing. It must not create tags, "
            "GitHub Releases, or Zenodo archives.",
            "",
        ]
    )
    text = "\n".join(lines)
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(text, encoding="utf-8")
        print(f"wrote promotion readiness report: {report_path}")
    else:
        print(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(MODES))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    config_path = args.config.resolve()
    config = load_config(config_path)
    with tempfile.TemporaryDirectory(prefix="primeclock-candidate-workflow-") as temp_dir:
        variables = {
            "repo_root": str(repo_root),
            "config_dir": str(config_path.parent),
            "tmp": temp_dir,
            "python": sys.executable,
        }
        if args.mode in {"artifact-freshness", "all"}:
            check_artifact_freshness(config, repo_root=repo_root, variables=variables)
        if args.mode in {"manifest-consistency", "all"}:
            check_manifest_consistency(config, repo_root=repo_root)
        if args.mode in {"quick", "all"}:
            run_gate(config, "quick", repo_root=repo_root, variables=variables)
        if args.mode in {"bundle", "all"}:
            run_gate(config, "bundle", repo_root=repo_root, variables=variables)
        if args.mode in {"slow", "all"}:
            run_gate(config, "slow", repo_root=repo_root, variables=variables)
        if args.mode in {"promotion-readiness", "all"}:
            write_promotion_readiness_report(config, report_path=args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
