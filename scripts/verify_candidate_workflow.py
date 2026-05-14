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
import os
import re
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
    "candidate-integrity",
    "gate-c",
    "gate-p-readiness",
    "slow",
    "research-review",
    "source-only-hygiene",
    "artifact-freshness",
    "manifest-consistency",
    "process-hygiene",
    "promotion-readiness",
    "public-theorem-bundle",
    "public-theorem-doi-integrity",
    "public-theorem-integrity",
    "public-theorem-review",
    "v2-6-special-point-obstruction",
    "v2-6-special-point-lemma-formalization",
    "v2-6-special-point-gate-r-review",
    "v2-6-endpoint-distance-proof-obligation",
    "v2-6-gate-r-local-first-process",
    "v2-6-special-point-theorem-note-decision",
    "v2-6-special-point-theorem-note-candidate",
    "v2-6-mod6-ancestry-diagnostic",
    "v2-6-k2-multigap-dilution-diagnostic",
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


def bundle_manifest_files_and_dirs(bundle_manifest: dict[str, Any]) -> tuple[set[str], set[str]]:
    files: set[str] = set()
    dirs: set[str] = set()
    for entry in bundle_manifest.get("root_file_map", []):
        files.add(entry["source"])
    for key in ["root_files", "research_files"]:
        files.update(bundle_manifest.get(key, []))
    dirs.update(bundle_manifest.get("research_dirs", []))
    return files, dirs


def load_public_release_files_and_dirs(
    repo_root: Path,
    *,
    release_config_path: str,
    release_builder_path: str,
) -> tuple[set[str], set[str]]:
    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    builder_path = resolve_path(repo_root, release_builder_path)
    spec = importlib.util.spec_from_file_location("public_release_builder_for_hygiene", builder_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load public release builder: {builder_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    release_config = load_json(resolve_path(repo_root, release_config_path))
    files = set(module.root_files(release_config))
    files.update(module.research_files(release_config))
    for source, _target in module.ROOT_FILE_MAP:
        files.add(source)
    dirs = set(module.RESEARCH_DIRS)
    return files, dirs


def source_path_is_in_sources(path: str, files: set[str], dirs: set[str]) -> bool:
    if path in files:
        return True
    normalized_dirs = {directory.rstrip("/") for directory in dirs}
    return any(path.startswith(f"{directory}/") for directory in normalized_dirs)


def check_source_only_hygiene(config: dict[str, Any], *, repo_root: Path) -> None:
    source_only = config.get("source_only_research")
    if not isinstance(source_only, dict):
        raise SystemExit("source-only hygiene failure: missing source_only_research config")

    def require_full_repo_input(relative_path: str, *, role: str) -> Path:
        path = resolve_path(repo_root, relative_path)
        if not path.exists():
            raise SystemExit(
                "source-only hygiene is not applicable outside full repo: "
                f"missing {role} input {relative_path}"
            )
        return path

    files = source_only.get("files", [])
    accepted_markers = source_only.get("accepted_name_markers", [])
    failures: list[str] = []
    for relative_path in files:
        path = resolve_path(repo_root, relative_path)
        if not path.is_file():
            failures.append(f"missing source-only research file: {relative_path}")
        if accepted_markers and not any(marker in Path(relative_path).name for marker in accepted_markers):
            failures.append(f"source-only research file does not follow version naming: {relative_path}")

    candidate_files: set[str] = set()
    candidate_dirs: set[str] = set()
    for manifest_path in source_only.get("candidate_bundle_manifests", []):
        manifest = load_json(
            require_full_repo_input(manifest_path, role="candidate manifest")
        )
        manifest_files, manifest_dirs = bundle_manifest_files_and_dirs(manifest)
        candidate_files.update(manifest_files)
        candidate_dirs.update(manifest_dirs)

    require_full_repo_input(source_only["public_release_config"], role="public release config")
    require_full_repo_input(source_only["public_release_builder"], role="public release builder")
    public_files, public_dirs = load_public_release_files_and_dirs(
        repo_root,
        release_config_path=source_only["public_release_config"],
        release_builder_path=source_only["public_release_builder"],
    )

    for relative_path in files:
        if source_path_is_in_sources(relative_path, candidate_files, candidate_dirs):
            failures.append(f"source-only research file is in candidate bundle sources: {relative_path}")
        if source_path_is_in_sources(relative_path, public_files, public_dirs):
            failures.append(f"source-only research file is in public release sources: {relative_path}")

    if failures:
        for failure in failures:
            print(f"FAIL: source-only hygiene failure: {failure}")
        raise SystemExit(1)
    print("source-only research hygiene check passed")


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


def markdown_section_bodies(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if match:
            current = match.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {heading: "\n".join(lines).strip() for heading, lines in sections.items()}


def check_research_review(config: dict[str, Any], *, repo_root: Path) -> None:
    review = config.get("research_review")
    if not isinstance(review, dict):
        raise SystemExit("research review gate failure: missing research_review config")

    note_path = resolve_path(repo_root, review["note"])
    if not note_path.is_file():
        raise SystemExit(f"research review gate failure: missing note {note_path}")

    text = note_path.read_text(encoding="utf-8")
    sections = markdown_section_bodies(text)
    failures: list[str] = []

    for section in review.get("required_sections", []):
        if not sections.get(section):
            failures.append(f"missing required research review section: {section}")

    decision_body = sections.get("Decision", "")
    allowed_decisions = set(review.get("allowed_decisions", []))
    candidate_decision = review.get("candidate_packaging_decision")
    matching_decisions = [
        decision
        for decision in sorted(allowed_decisions)
        if re.search(rf"(?<![A-Za-z0-9_-]){re.escape(decision)}(?![A-Za-z0-9_-])", decision_body)
    ]
    if not matching_decisions:
        failures.append("missing or unknown research review decision")
    elif candidate_decision not in matching_decisions:
        failures.append(
            "research review decision does not allow candidate packaging: "
            + ", ".join(matching_decisions)
        )

    for term in review.get("forbidden_artifact_basis_terms", []):
        if re.search(re.escape(term), text, re.IGNORECASE):
            failures.append(
                "research review note must not base research value on artifact "
                f"integrity term: {term}"
            )

    if failures:
        for failure in failures:
            print(f"FAIL: research review gate failure: {failure}")
        raise SystemExit(1)
    print("candidate research review gate passed")


def status_report_failures(
    text: str,
    *,
    source: str,
    required_fields: list[str] | None = None,
) -> list[str]:
    required = set(required_fields or [
        "goal",
        "current_completion_percent",
        "remaining_slices_estimate",
    ])
    failures: list[str] = []
    if "goal" in required and not re.search(r"\bGoal\b|目的", text, re.IGNORECASE):
        failures.append(f"{source}: missing goal/purpose section")
    if "current_completion_percent" in required and not re.search(
        r"\b\d{1,3}(?:\s*(?:-|to|〜)\s*\d{1,3})?\s*%",
        text,
    ):
        failures.append(f"{source}: missing current completion percent")
    if "remaining_slices_estimate" in required and not (
        re.search(
            r"\b\d+(?:\s*(?:-|to|〜)\s*\d+)?\s*(?:slice|slices)\b",
            text,
            re.IGNORECASE,
        )
        or re.search(
            r"\b(?:slice|slices)\b.*\b\d+",
            text,
            re.IGNORECASE,
        )
        or re.search(
            r"\d+(?:\s*(?:-|to|〜)\s*\d+)?\s*スライス",
            text,
        )
        or re.search(
            r"スライス.*\d+",
            text,
        )
    ):
        failures.append(f"{source}: missing remaining slice estimate")
    return failures


def load_pr_body_from_event() -> tuple[str | None, str | None]:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event_name = os.environ.get("GITHUB_EVENT_NAME")
    if event_name != "pull_request" or not event_path:
        return None, None
    path = Path(event_path)
    if not path.is_file():
        return None, f"pull_request event missing GITHUB_EVENT_PATH file: {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    body = data.get("pull_request", {}).get("body")
    return body or "", None


def candidate_bundle_source_paths(
    config: dict[str, Any],
    *,
    repo_root: Path,
) -> set[str]:
    paths = config["paths"]
    bundle_manifest = load_json(resolve_path(repo_root, paths["bundle_manifest"]))
    sources: set[str] = set()
    for entry in bundle_manifest.get("root_file_map", []):
        sources.add(entry["source"])
    for key in ["root_files", "research_files"]:
        sources.update(bundle_manifest.get(key, []))
    for relative_dir in bundle_manifest.get("research_dirs", []):
        root = resolve_path(repo_root, relative_dir)
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                sources.add(path.relative_to(repo_root).as_posix())
    return sources


def should_scan_text_path(relative_path: str, hygiene: dict[str, Any]) -> bool:
    path = Path(relative_path)
    if path.suffix.lower() not in {".json", ".md", ".py", ".txt", ".yaml", ".yml"}:
        return False
    excluded = set(hygiene.get("artifact_scan_exclude_paths", []))
    if relative_path in excluded or path.name in excluded:
        return False
    for prefix in hygiene.get("artifact_scan_exclude_prefixes", []):
        if relative_path.startswith(prefix.rstrip("/") + "/"):
            return False
    return True


def forbidden_term_matches(text: str, terms: list[str]) -> list[str]:
    matches: list[str] = []
    for term in terms:
        pattern = r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])"
        if re.search(pattern, text, re.IGNORECASE):
            matches.append(term)
    return matches


def check_artifact_text_hygiene(
    config: dict[str, Any],
    *,
    repo_root: Path,
) -> list[str]:
    hygiene = config.get("process_hygiene", {})
    terms = list(hygiene.get("artifact_forbidden_terms", []))
    terms.extend(hygiene.get("process_wording_forbidden_terms", []))
    failures: list[str] = []
    for relative_path in sorted(candidate_bundle_source_paths(config, repo_root=repo_root)):
        if not should_scan_text_path(relative_path, hygiene):
            continue
        path = resolve_path(repo_root, relative_path)
        if not path.is_file():
            failures.append(f"artifact text scan missing source file: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for term in forbidden_term_matches(text, terms):
            failures.append(
                "process/private wording is not allowed in candidate artifacts: "
                f"{term!r} in {relative_path}"
            )
    return failures


def check_timezone_docs(config: dict[str, Any], *, repo_root: Path) -> list[str]:
    failures: list[str] = []
    for item in config.get("process_hygiene", {}).get("timezone_docs", []):
        path = resolve_path(repo_root, item["path"])
        text = path.read_text(encoding="utf-8")
        required = item.get("required_text")
        if required:
            if required not in text:
                failures.append(f"{item['path']}: missing timezone text {required!r}")
            continue
        label = item.get("label", item["path"])
        if not re.search(r"\bUTC\b", text) or not re.search(r"\bJST\b", text):
            failures.append(f"{label}: important schedule time must include UTC and JST")
    return failures


def process_hygiene_failures(
    config: dict[str, Any],
    *,
    repo_root: Path,
    readiness_text: str | None = None,
    pr_body: str | None = None,
    require_pr_body: bool = False,
) -> list[str]:
    failures: list[str] = []
    required_fields = config.get("process_hygiene", {}).get("status_report_required_fields")
    report_text = readiness_text or promotion_readiness_report_text(config)
    failures.extend(
        status_report_failures(
            report_text,
            source="promotion readiness report",
            required_fields=required_fields,
        )
    )
    event_body, event_failure = load_pr_body_from_event()
    if event_failure:
        failures.append(event_failure)
    if pr_body is None:
        pr_body = event_body
    if require_pr_body and pr_body is None:
        failures.append("pull_request event requires PR body hygiene validation")
    if pr_body is not None:
        failures.extend(
            status_report_failures(
                pr_body,
                source="PR body",
                required_fields=required_fields,
            )
        )
    failures.extend(check_timezone_docs(config, repo_root=repo_root))
    failures.extend(check_artifact_text_hygiene(config, repo_root=repo_root))
    return failures


def check_process_hygiene(
    config: dict[str, Any],
    *,
    repo_root: Path,
    readiness_text: str | None = None,
    pr_body_path: Path | None = None,
) -> None:
    pr_body = pr_body_path.read_text(encoding="utf-8") if pr_body_path else None
    require_pr_body = os.environ.get("GITHUB_EVENT_NAME") == "pull_request"
    failures = process_hygiene_failures(
        config,
        repo_root=repo_root,
        readiness_text=readiness_text,
        pr_body=pr_body,
        require_pr_body=require_pr_body,
    )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print("candidate process hygiene check passed")


def promotion_readiness_report_text(config: dict[str, Any]) -> str:
    policy = config["promotion_policy"]
    readiness = config.get("readiness", {})
    current_completion = readiness.get("current_completion_percent")
    if current_completion is None:
        current_completion = readiness.get("reusable_workflow_percent", "unknown")
    remaining_slices = readiness.get("estimated_slices_to_target", "unknown")
    lines = [
        f"# Candidate Promotion Readiness: {config['candidate_id']}",
        "",
        f"- Status: {config['status']}",
        f"- Public release allowed: {policy['public_release_allowed']}",
        f"- Zenodo allowed: {policy['zenodo_allowed']}",
        f"- Base public release: {config['base_public_release']}",
        "",
        "## Goal",
        "",
        config.get("goal", "No goal recorded."),
        "",
        "## Current Completion",
        "",
        f"- Current completion percent: {current_completion}%",
        f"- Workflow reuse target: {readiness.get('reusable_workflow_percent', 'unknown')}%",
        "",
        "## Remaining Slice Estimate",
        "",
        f"- Remaining slice estimate: {remaining_slices} slices",
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
    return "\n".join(lines)


def write_promotion_readiness_report(
    config: dict[str, Any],
    *,
    report_path: Path | None,
) -> str:
    text = promotion_readiness_report_text(config)
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(text, encoding="utf-8")
        print(f"wrote promotion readiness report: {report_path}")
    else:
        print(text)
    return text


def resolve_optional_path(path: Path | None) -> Path | None:
    return path.resolve() if path else None


def require_config_sections(
    config: dict[str, Any],
    *,
    mode: str,
    sections: list[str],
) -> None:
    missing = [section for section in sections if section not in config]
    if missing:
        raise SystemExit(
            "candidate workflow config does not define mode "
            f"{mode!r} for this config; missing config section(s): "
            + ", ".join(missing)
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(MODES))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--pr-body", type=Path)
    args = parser.parse_args()

    repo_root = repo_root_from_script()
    config_path = args.config.resolve()
    config = load_config(config_path)
    pr_body_path = resolve_optional_path(args.pr_body)
    with tempfile.TemporaryDirectory(prefix="primeclock-candidate-workflow-") as temp_dir:
        variables = {
            "repo_root": str(repo_root),
            "config_dir": str(config_path.parent),
            "tmp": temp_dir,
            "python": sys.executable,
        }
        if args.mode in {"research-review", "all"}:
            check_research_review(config, repo_root=repo_root)
        if args.mode in {"source-only-hygiene", "all"}:
            check_source_only_hygiene(config, repo_root=repo_root)
        if args.mode in {"artifact-freshness", "all"}:
            require_config_sections(
                config,
                mode="artifact-freshness",
                sections=["artifact_freshness"],
            )
            check_artifact_freshness(config, repo_root=repo_root, variables=variables)
        if args.mode in {"manifest-consistency", "all"}:
            require_config_sections(
                config,
                mode="manifest-consistency",
                sections=["paths", "manifest_consistency"],
            )
            check_manifest_consistency(config, repo_root=repo_root)
        if args.mode in {"quick", "all"}:
            run_gate(config, "quick", repo_root=repo_root, variables=variables)
        if args.mode in {"candidate-integrity", "all"}:
            run_gate(config, "candidate-integrity", repo_root=repo_root, variables=variables)
        if args.mode in {"bundle", "all"}:
            run_gate(config, "bundle", repo_root=repo_root, variables=variables)
        if args.mode == "gate-c":
            run_gate(config, "candidate-integrity", repo_root=repo_root, variables=variables)
            run_gate(config, "bundle", repo_root=repo_root, variables=variables)
            run_gate(config, "gate-c", repo_root=repo_root, variables=variables)
        if args.mode in {"gate-p-readiness", "all"}:
            run_gate(config, "gate-p-readiness", repo_root=repo_root, variables=variables)
        if args.mode in {"public-theorem-integrity", "all"}:
            run_gate(config, "public-theorem-integrity", repo_root=repo_root, variables=variables)
        if args.mode in {"public-theorem-doi-integrity", "all"}:
            run_gate(config, "public-theorem-doi-integrity", repo_root=repo_root, variables=variables)
        if args.mode in {"public-theorem-bundle", "all"}:
            run_gate(config, "public-theorem-bundle", repo_root=repo_root, variables=variables)
        if args.mode == "v2-6-special-point-obstruction" or (
            args.mode == "all"
            and "v2-6-special-point-obstruction" in config.get("gates", {})
        ):
            run_gate(
                config,
                "v2-6-special-point-obstruction",
                repo_root=repo_root,
                variables=variables,
            )
        if args.mode == "v2-6-special-point-lemma-formalization" or (
            args.mode == "all"
            and "v2-6-special-point-lemma-formalization" in config.get("gates", {})
        ):
            run_gate(
                config,
                "v2-6-special-point-lemma-formalization",
                repo_root=repo_root,
                variables=variables,
            )
        if args.mode == "v2-6-special-point-gate-r-review" or (
            args.mode == "all"
            and "v2-6-special-point-gate-r-review" in config.get("gates", {})
        ):
            run_gate(
                config,
                "v2-6-special-point-gate-r-review",
                repo_root=repo_root,
                variables=variables,
            )
        if args.mode == "v2-6-endpoint-distance-proof-obligation" or (
            args.mode == "all"
            and "v2-6-endpoint-distance-proof-obligation" in config.get("gates", {})
        ):
            run_gate(
                config,
                "v2-6-endpoint-distance-proof-obligation",
                repo_root=repo_root,
                variables=variables,
            )
        if args.mode == "v2-6-gate-r-local-first-process" or (
            args.mode == "all"
            and "v2-6-gate-r-local-first-process" in config.get("gates", {})
        ):
            run_gate(
                config,
                "v2-6-gate-r-local-first-process",
                repo_root=repo_root,
                variables=variables,
            )
        if args.mode == "v2-6-special-point-theorem-note-decision" or (
            args.mode == "all"
            and "v2-6-special-point-theorem-note-decision" in config.get("gates", {})
        ):
            run_gate(
                config,
                "v2-6-special-point-theorem-note-decision",
                repo_root=repo_root,
                variables=variables,
            )
        if args.mode == "v2-6-special-point-theorem-note-candidate" or (
            args.mode == "all"
            and "v2-6-special-point-theorem-note-candidate" in config.get("gates", {})
        ):
            run_gate(
                config,
                "v2-6-special-point-theorem-note-candidate",
                repo_root=repo_root,
                variables=variables,
            )
        if args.mode == "v2-6-mod6-ancestry-diagnostic" or (
            args.mode == "all"
            and "v2-6-mod6-ancestry-diagnostic" in config.get("gates", {})
        ):
            run_gate(
                config,
                "v2-6-mod6-ancestry-diagnostic",
                repo_root=repo_root,
                variables=variables,
            )
        if args.mode == "v2-6-k2-multigap-dilution-diagnostic" or (
            args.mode == "all"
            and "v2-6-k2-multigap-dilution-diagnostic" in config.get("gates", {})
        ):
            run_gate(
                config,
                "v2-6-k2-multigap-dilution-diagnostic",
                repo_root=repo_root,
                variables=variables,
            )
        if args.mode == "public-theorem-review":
            run_gate(config, "public-theorem-integrity", repo_root=repo_root, variables=variables)
            run_gate(config, "public-theorem-doi-integrity", repo_root=repo_root, variables=variables)
            run_gate(config, "public-theorem-bundle", repo_root=repo_root, variables=variables)
        if args.mode in {"slow", "all"}:
            run_gate(config, "slow", repo_root=repo_root, variables=variables)
        if args.mode in {"promotion-readiness", "all"}:
            require_config_sections(
                config,
                mode="promotion-readiness",
                sections=["promotion_policy"],
            )
            text = write_promotion_readiness_report(config, report_path=args.report)
            check_process_hygiene(
                config,
                repo_root=repo_root,
                readiness_text=text,
                pr_body_path=pr_body_path,
            )
        elif args.mode == "process-hygiene":
            require_config_sections(
                config,
                mode="process-hygiene",
                sections=["promotion_policy"],
            )
            check_process_hygiene(config, repo_root=repo_root, pr_body_path=pr_body_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
