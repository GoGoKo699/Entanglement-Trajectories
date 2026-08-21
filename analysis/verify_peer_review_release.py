#!/usr/bin/env python3
"""Verify closure of the peer-review release blockers and major claim gates.

This is a deterministic audit of the frozen repository evidence. It does not
rerun the dense state-vector simulations through n=20 or the full bootstrap;
those workflows remain separately available. Use ``--write-report`` to save a
machine-readable result.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import tempfile
import zipfile

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
import sys
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from entanglement_trajectories.boundaries import metric_bounds_fixed_lmax
from entanglement_trajectories.metrics import hartley_entropy, numerical_schmidt_rank
from entanglement_trajectories.robustness import majorization_transition_audit


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def json_member(archive: Path, member: str) -> dict:
    with zipfile.ZipFile(archive) as zf:
        return json.loads(zf.read(member))


def check_hartley() -> dict:
    d = 1024
    p = 1.0 - 1.0e-14
    tail = (1.0 - p) / (d - 1)
    equal_tail = np.full(d, tail)
    equal_tail[0] = p
    bounds = metric_bounds_fixed_lmax("hartley_entropy", p, d, base=2.0)
    exact = hartley_entropy(equal_tail, base=2.0)
    numerical = numerical_schmidt_rank(equal_tail, threshold=1.0e-15)
    require(math.isclose(bounds.lower, 1.0, abs_tol=1e-12), "Hartley lower boundary")
    require(math.isclose(bounds.upper, 10.0, abs_tol=1e-12), "Hartley upper boundary")
    require(math.isclose(exact, 10.0, abs_tol=1e-12), "exact Hartley entropy")
    require(numerical == 1, "thresholded numerical rank counterexample")
    return {
        "p": p,
        "dimension": d,
        "tail_eigenvalue": tail,
        "exact_bounds_bits": [bounds.lower, bounds.upper],
        "exact_equal_tail_bits": exact,
        "numerical_rank_at_1e-15": numerical,
    }


def check_xxz() -> dict:
    archive = ROOT / "data" / "xxz_convergence_n10_n12_n14.zip"
    require(archive.is_file(), "missing XXZ convergence archive")
    with zipfile.ZipFile(archive) as zf:
        require(zf.testzip() is None, "XXZ archive CRC failure")
        summary = json.loads(zf.read("xxz_convergence_summary.json"))
        rows = sum(1 for _ in zf.read("xxz_convergence_halfmetrics_n10_n12_n14.csv").decode("utf-8").splitlines()) - 1
    final_pair = summary["pairwise_refinement"]["16_vs_32"]
    effects = summary["core_claim_sensitivity"]
    global_by_substep = {int(row["substeps"]): float(row["global_pc1_fraction"]) for row in effects}
    shift = abs(global_by_substep[1] - global_by_substep[32])
    require(rows == 3528, "unexpected XXZ convergence row count")
    require(summary["decision"]["one_substep_converged"] is False, "one-step XXZ must remain unconverged")
    require(float(final_pair["overall_max_abs"]) < 0.002, "16-vs-32 convergence gate")
    require(shift < 0.001, "central common-mode sensitivity to XXZ refinement")
    return {
        "rows": rows,
        "one_substep_converged": False,
        "max_abs_16_vs_32": float(final_pair["overall_max_abs"]),
        "global_pc1_shift_1_vs_32": shift,
    }


def check_spectra_and_majorization() -> dict:
    archive = ROOT / "data" / "spectra_selected_n20.zip"
    require(archive.is_file(), "missing selected spectra archive")
    spectra_count = 0
    with tempfile.TemporaryDirectory(prefix="peer_review_spectra_") as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(archive) as zf:
            require(zf.testzip() is None, "selected spectra archive CRC failure")
            members = [name for name in zf.namelist() if name.endswith(".npz")]
            require(len(members) == 5, "selected spectra archive member count")
            zf.extractall(tmp_path)
        for path in sorted(tmp_path.glob("*.npz")):
            with np.load(path, allow_pickle=False) as data:
                spectra = np.asarray(data["spectra"], dtype=float)
                require(str(data["spectrum_order"][0]) == "descending", f"spectrum order field: {path.name}")
                require(np.all(np.diff(spectra, axis=1) <= 1e-14), f"descending spectra: {path.name}")
                require(np.allclose(spectra.sum(axis=1), 1.0, atol=2e-12), f"spectrum normalization: {path.name}")
                spectra_count += len(spectra)
        audit = majorization_transition_audit(tmp_path, majorization_tol=1e-10, metric_tol=1e-10)
    competition = audit[audit["metric_event"] == "metric_competition"]
    require(spectra_count == 405, "selected spectrum count")
    require(len(audit) == 400, "selected transition count")
    require(len(competition) == 50, "selected competition count")
    require(set(competition["majorization_relation"]) == {"incomparable"}, "competition majorization mechanism")
    require(int((audit["majorization_relation"] == "incomparable").sum()) == 280, "incomparable transition count")
    return {
        "archive_members": 5,
        "spectra": spectra_count,
        "transitions": len(audit),
        "incomparable": 280,
        "metric_competition": 50,
        "competition_outside_incomparable": 0,
    }


def check_metric_summary() -> dict:
    archive = ROOT / "data" / "public_analysis_inputs.zip"
    summary = json_member(archive, "metric_robustness_scientific_summary.json")
    common = summary["common_mode"]
    classification = summary["classification_stress_tests"]
    require(math.isclose(common["boundary_pc1_explained"], 0.9026282298671149, abs_tol=2e-15), "common mode value")
    require(np.allclose(common["boundary_pc1_cluster_bootstrap_ci95"], [0.8626128030927239, 0.9341235189039404], atol=2e-15), "design-cluster interval")
    require(math.isclose(classification["centroid_leave_size_full"]["same_metric_mean_accuracy"], 0.875, abs_tol=1e-15), "centroid full same-metric")
    require(math.isclose(classification["centroid_leave_size_vertical"]["cross_metric_mean_accuracy"], 0.375, abs_tol=1e-15), "centroid vertical cross-metric")
    require(math.isclose(classification["individual_double_holdout_full"]["same_metric_mean_accuracy"], 0.3298611111111111, abs_tol=1e-15), "individual full double holdout")
    require(math.isclose(classification["lambda_max_path_baselines"][-1]["accuracy"], 0.4166666666666667, abs_tol=1e-15), "lambda-max baseline")
    require(summary["majorization_selected_spectra"]["competition_outside_incomparable"] == 0, "majorization summary")
    return {
        "boundary_pc1": common["boundary_pc1_explained"],
        "design_cluster_ci95": common["boundary_pc1_cluster_bootstrap_ci95"],
        "centroid_full_same": classification["centroid_leave_size_full"]["same_metric_mean_accuracy"],
        "centroid_full_cross": classification["centroid_leave_size_full"]["cross_metric_mean_accuracy"],
        "centroid_vertical_same": classification["centroid_leave_size_vertical"]["same_metric_mean_accuracy"],
        "centroid_vertical_cross": classification["centroid_leave_size_vertical"]["cross_metric_mean_accuracy"],
        "individual_full_same": classification["individual_double_holdout_full"]["same_metric_mean_accuracy"],
        "lambda_max_baseline": classification["lambda_max_path_baselines"][-1]["accuracy"],
    }


def check_sensitivity() -> dict:
    path = ROOT / "metadata" / "common_mode_sensitivity.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    values = [
        data["row_weighted_levels"],
        data["equal_trajectory_weight_levels"],
        data["within_trajectory_standardized_levels"],
        data["first_differences"],
        *data["leave_one_model_out"].values(),
        *data["by_size"].values(),
    ]
    require(min(values) > 0.86, "common-mode sensitivity minimum")
    return data


def check_figure_provenance() -> dict:
    builder = (ROOT / "scripts" / "build_public_figures.py").read_text(encoding="utf-8")
    rebuild = (ROOT / "scripts" / "rebuild_all_from_included_data.sh").read_text(encoding="utf-8")
    require("--analysis-input-dir" in builder, "figure builder explicit analysis input")
    require("--analysis-input-dir outputs/rebuild/results" in rebuild, "end-to-end figure dataflow")
    require("public_figure_input_provenance.json" in builder, "figure provenance record")
    names = [
        "figure_01_one_spectrum_many_lenses.png",
        "figure_02_exact_metric_arenas.png",
        "figure_03_metric_robustness_hierarchy.png",
        "figure_04_majorization_and_metric_competition.png",
        "figure_05_model_morphology_and_limits.png",
        "social_preview.png",
    ]
    for name in names:
        require((ROOT / "figures" / "public" / name).is_file(), f"missing public figure {name}")
    source_files = sorted((ROOT / "figures" / "public" / "data").glob("*"))
    require(source_files, "missing committed public-figure source tables")
    return {"public_images": len(names), "source_records": len(source_files), "end_to_end_mode": True}


def check_environment_and_workflow() -> dict:
    env = json.loads((ROOT / "environment" / "release-py311.json").read_text(encoding="utf-8"))
    workflow_text = (ROOT / ".github" / "workflows" / "qa.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)
    require(env["canonical_job"]["python_version"] == "3.11.15", "release Python")
    require(env["canonical_job"]["operating_system"] == "ubuntu-24.04", "release OS")
    require("actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd" in workflow_text, "checkout full SHA")
    require("actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1" in workflow_text, "setup-python full SHA")
    require(workflow.get("permissions", {}).get("contents") == "read", "least privilege")
    for relative in ["requirements/release-build.txt", "requirements/release-py311.txt", ".python-version"]:
        require((ROOT / relative).is_file(), f"missing release lock {relative}")
    return {
        "os": env["canonical_job"]["operating_system"],
        "python": env["canonical_job"]["python_version"],
        "pinned_runtime_packages": len(env["packages"]),
        "pinned_build_packages": len(env["build_packages"]),
        "immutable_action_refs": True,
    }


def check_language_and_records() -> dict:
    authoritative = [
        ROOT / "README.md",
        ROOT / "START_HERE.md",
        ROOT / "SCIENTIFIC_POSITION.md",
        ROOT / "AI_CONTEXT.md",
        ROOT / "docs" / "SCIENTIFIC_OVERVIEW.md",
        ROOT / "docs" / "METRIC_ROBUSTNESS_RESULT.md",
        ROOT / "paper" / "AUTHOR_CLARIFICATION_2026.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in authoritative)
    prohibited = [
        "four tested quantum-chaos families",
        "Across the tested pure-state chaos families",
        "Trotterized random-field XXZ.",
        "narrow corrigendum draft",
        "checksum-tracked",
    ]
    for phrase in prohibited:
        require(phrase not in text, f"stale public wording: {phrase}")
    for relative in ["REFERENCES.md", "metadata/references.json", "LICENSE", "LICENSE-CONTENT.md", "metadata/peer_review_issue_resolution.csv"]:
        require((ROOT / relative).is_file(), f"missing record {relative}")
    return {"authoritative_documents_checked": len(authoritative), "stale_phrases": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    result = {
        "schema_version": "entanglement-trajectories-peer-review-release-audit-1.0",
        "repository_version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "checks": {
            "hartley_exactness": check_hartley(),
            "xxz_convergence": check_xxz(),
            "spectra_and_majorization": check_spectra_and_majorization(),
            "metric_summary": check_metric_summary(),
            "common_mode_sensitivity": check_sensitivity(),
            "public_figure_provenance": check_figure_provenance(),
            "release_environment": check_environment_and_workflow(),
            "language_and_records": check_language_and_records(),
        },
        "all_checks_passed": True,
        "release_recommendation": "GO after one green locked hosted CI run and application of the remaining repository metadata settings.",
    }
    text = json.dumps(result, indent=2) + "\n"
    if args.write_report:
        path = args.write_report
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
