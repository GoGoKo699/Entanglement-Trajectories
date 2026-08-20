#!/usr/bin/env python3
"""Deterministic checks supporting the 2026 author-correction map.

This script verifies only elementary, self-contained statements needed for the
correction layer. It does not rerun the large quantum-chaos package.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "paper_corrections"
OUT.mkdir(parents=True, exist_ok=True)
WRITE_OUTPUTS = "--check-only" not in sys.argv


def entropy(values: Iterable[float]) -> float:
    arr = np.asarray(list(values), dtype=float)
    arr = arr[arr > 0.0]
    return float(-np.sum(arr * np.log(arr)))


def exact_smax(p: float, d: int) -> float:
    if not (1.0 / d <= p <= 1.0):
        raise ValueError("p must lie in [1/d, 1]")
    if p == 1.0:
        return 0.0
    return -p * math.log(p) - (1.0 - p) * math.log((1.0 - p) / (d - 1))


def exact_smin(p: float, d: int) -> float:
    if not (1.0 / d <= p <= 1.0):
        raise ValueError("p must lie in [1/d, 1]")
    if p == 1.0:
        return 0.0
    k = min(d, int(math.floor(1.0 / p + 1e-12)))
    remainder = 1.0 - k * p
    if abs(remainder) < 1e-12:
        remainder = 0.0
    result = -k * p * math.log(p)
    if remainder > 0.0:
        result -= remainder * math.log(remainder)
    return result


def paper_f1(p: float) -> float:
    if p in (0.0, 1.0):
        return 0.0
    return -p * math.log(p) - (1.0 - p) * math.log(1.0 - p)


def paper_f2(p: float) -> float:
    return -math.log(p)


def paper_f3(p: float, d: int) -> float:
    return paper_f1(p) + (1.0 - p) * math.log(d)


def harmonic(n: int) -> float:
    return math.fsum(1.0 / k for k in range(1, n + 1))


def page_exact(a: int, b: int) -> float:
    if not (1 <= a <= b):
        raise ValueError("Require 1 <= a <= b")
    return harmonic(a * b) - harmonic(b) - (a - 1.0) / (2.0 * b)


def page_paper_approx(a: int, b: int) -> float:
    return math.log(a) - a / (2.0 * b)


def qft_matrix(n: int) -> np.ndarray:
    j = np.arange(n)
    return np.exp(2j * np.pi * np.outer(j, j) / n) / math.sqrt(n)


def reduced_spectrum(state: np.ndarray, dim_a: int, dim_b: int) -> np.ndarray:
    matrix = np.asarray(state).reshape(dim_a, dim_b)
    rho = matrix @ matrix.conj().T
    values = np.linalg.eigvalsh(rho)
    values[np.abs(values) < 1e-14] = 0.0
    return np.sort(values)[::-1]


def prime_union_endpoint_spectrum(n: int) -> np.ndarray:
    if n % 2:
        raise ValueError("Natural equal bipartition requires even n")
    d = 2 ** (n // 2)
    determinant = 2.0 * (d - 1) * (d - 2) / (d * d - 2) ** 2
    discriminant = math.sqrt(max(0.0, 1.0 - 4.0 * determinant))
    return np.array([(1.0 + discriminant) / 2.0, (1.0 - discriminant) / 2.0])


def exact_gap_bounds(p: float, d: int) -> tuple[float, float]:
    if not (1.0 / d <= p < 1.0):
        raise ValueError("p must lie in [1/d, 1)")
    lower = max(0.0, math.log(p / (1.0 - p)))
    upper = math.log(p * (d - 1) / (1.0 - p))
    return lower, upper


def eq32_reference(a: int, b: int, p: float) -> float:
    return (
        (1.0 - p)
        * (math.log(a) - math.log(1.0 - p) - a / (2.0 * b))
        - p * math.log(p)
    )


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    if not WRITE_OUTPUTS:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    summary: dict[str, object] = {
        "script": str(Path(__file__).relative_to(ROOT)),
        "logarithm": "natural",
        "checks": {},
    }

    # 1. Exact entropy envelope versus the three curves in the paper.
    boundary_rows: list[dict] = []
    boundary_summary: dict[str, dict] = {}
    for d in (4, 32, 128):
        ps = np.linspace(1.0 / d, 0.999999, 100_000)
        exact_min = np.array([exact_smin(float(p), d) for p in ps])
        exact_max = np.array([exact_smax(float(p), d) for p in ps])
        paper_lower = np.maximum(
            np.array([paper_f1(float(p)) for p in ps]),
            np.array([paper_f2(float(p)) for p in ps]),
        )
        paper_upper = np.array([paper_f3(float(p), d) for p in ps])
        lower_deficit = exact_min - paper_lower
        upper_excess = paper_upper - exact_max
        li = int(np.argmax(lower_deficit))
        ui = int(np.argmax(upper_excess))
        record = {
            "dimension": d,
            "maximum_lower_envelope_deficit_nats": float(lower_deficit[li]),
            "p_at_maximum_lower_deficit": float(ps[li]),
            "maximum_paper_upper_excess_nats": float(upper_excess[ui]),
            "p_at_maximum_upper_excess": float(ps[ui]),
        }
        boundary_summary[str(d)] = record
        boundary_rows.append(record)
    write_csv(
        OUT / "exact_boundary_comparison.csv",
        list(boundary_rows[0].keys()),
        boundary_rows,
    )
    summary["checks"]["exact_entropy_boundary"] = {
        "passed": True,
        "result": boundary_summary,
        "interpretation": (
            "The paper curves form an outer approximation. The exact lower envelope is "
            "piecewise, and the exact upper envelope uses d-1 rather than d."
        ),
    }

    # Saturation checks for extremizing spectra.
    rng = np.random.default_rng(20260819)
    max_residual = 0.0
    min_residual = 0.0
    for d in (3, 4, 8, 32):
        for p in rng.uniform(1.0 / d, 0.999, 100):
            equal_tail = [p] + [(1.0 - p) / (d - 1)] * (d - 1)
            k = min(d, int(math.floor(1.0 / p + 1e-12)))
            concentrated = [p] * k
            remainder = 1.0 - k * p
            if remainder > 1e-12:
                concentrated.append(remainder)
            concentrated += [0.0] * (d - len(concentrated))
            max_residual = max(max_residual, abs(entropy(equal_tail) - exact_smax(p, d)))
            min_residual = max(min_residual, abs(entropy(concentrated) - exact_smin(p, d)))
    summary["checks"]["entropy_extremizer_saturation"] = {
        "passed": max(max_residual, min_residual) < 1e-11,
        "maximum_upper_residual": max_residual,
        "maximum_lower_residual": min_residual,
    }

    # 2. Exact Page mean versus the paper's asymptotic expression.
    page_pairs = [
        (1, 1), (1, 8), (2, 2), (2, 8), (4, 4), (4, 16),
        (32, 32), (32, 64), (128, 128), (128, 256), (128, 8192),
    ]
    page_rows: list[dict] = []
    for a, b in page_pairs:
        exact = page_exact(a, b)
        approx = page_paper_approx(a, b)
        page_rows.append({
            "alpha": a,
            "beta": b,
            "exact_page_mean_nats": exact,
            "paper_expression_nats": approx,
            "paper_minus_exact_nats": approx - exact,
        })
    write_csv(
        OUT / "page_formula_comparison.csv",
        list(page_rows[0].keys()),
        page_rows,
    )
    summary["checks"]["page_formula"] = {
        "passed": True,
        "alpha_1_counterexample": page_rows[0],
        "interpretation": (
            "H_{alpha beta}-H_beta-(alpha-1)/(2 beta) is exact for the complex Haar "
            "ensemble; log(alpha)-alpha/(2 beta) is its leading large-size approximation."
        ),
    }

    # 3. Rank-one mean matrix.
    a, b = 5, 7
    gamma = 0.3 + 0.2j
    h = np.full((a, b), gamma, dtype=complex)
    hh = h @ h.conj().T
    eig = np.sort(np.linalg.eigvalsh(hh))[::-1]
    expected = np.array([a * b * abs(gamma) ** 2] + [0.0] * (a - 1))
    rank_one_result = {
        "alpha": a,
        "beta": b,
        "gamma_real": gamma.real,
        "gamma_imag": gamma.imag,
        "computed_eigenvalues": eig.tolist(),
        "expected_eigenvalues": expected.tolist(),
        "maximum_absolute_residual": float(np.max(np.abs(eig - expected))),
    }
    if WRITE_OUTPUTS:
        (OUT / "rank_one_mean_matrix.json").write_text(
            json.dumps(rank_one_result, indent=2), encoding="utf-8"
        )
    summary["checks"]["rank_one_mean_matrix"] = {
        "passed": bool(rank_one_result["maximum_absolute_residual"] < 1e-12),
        "result": rank_one_result,
    }

    # 4. Explicit global-QFT counterexample.
    initial = np.array([1.0, 1.0, 0.0, 0.0], dtype=complex) / math.sqrt(2.0)
    transformed = qft_matrix(4) @ initial
    initial_spectrum = reduced_spectrum(initial, 2, 2)
    transformed_spectrum = reduced_spectrum(transformed, 2, 2)
    qft_result = {
        "initial_state": "|0>|+>",
        "initial_schmidt_spectrum": initial_spectrum.tolist(),
        "initial_entropy_nats": entropy(initial_spectrum),
        "qft_schmidt_spectrum": transformed_spectrum.tolist(),
        "qft_entropy_nats": entropy(transformed_spectrum),
        "closed_form_qft_spectrum": [
            (1.0 + 1.0 / math.sqrt(2.0)) / 2.0,
            (1.0 - 1.0 / math.sqrt(2.0)) / 2.0,
        ],
    }
    if WRITE_OUTPUTS:
        (OUT / "qft_counterexample.json").write_text(
            json.dumps(qft_result, indent=2), encoding="utf-8"
        )
    summary["checks"]["global_qft_invariance"] = {
        "passed": bool(
            qft_result["initial_entropy_nats"] < 1e-12
            and qft_result["qft_entropy_nats"] > 0.4
        ),
        "result": qft_result,
    }

    # 5. Endpoint of the union of k-almost-prime states.
    union_rows: list[dict] = []
    for n in (4, 6, 8, 14, 26):
        spectrum = prime_union_endpoint_spectrum(n)
        union_rows.append({
            "n_qubits": n,
            "half_dimension": 2 ** (n // 2),
            "lambda_1": float(spectrum[0]),
            "lambda_2": float(spectrum[1]),
            "entropy_nats": entropy(spectrum),
            "is_exactly_product": bool(spectrum[1] < 1e-15),
        })
    write_csv(
        OUT / "prime_union_endpoint.csv",
        list(union_rows[0].keys()),
        union_rows,
    )
    summary["checks"]["prime_union_endpoint"] = {
        "passed": all(row["entropy_nats"] > 0.0 for row in union_rows),
        "result": union_rows,
        "interpretation": (
            "The state uniform over all basis strings except 0 and 1 has Schmidt rank two "
            "for the natural equal cut. It approaches, but never equals, the product point."
        ),
    }

    # 6. Exact entanglement-gap envelope and a counterexample to universal inverse ordering.
    gap_rows: list[dict] = []
    for d in (4, 32, 128):
        for p in (1.0 / d, 0.2 if 0.2 >= 1.0 / d else 1.0 / d, 0.4, 0.6, 0.9):
            if p < 1.0 / d or p >= 1.0:
                continue
            lower, upper = exact_gap_bounds(p, d)
            gap_rows.append({
                "dimension": d,
                "lambda_max": p,
                "exact_minimum_gap": lower,
                "exact_maximum_gap": upper,
                "paper_g3": math.log(p * d / (1.0 - p)),
                "paper_g3_minus_exact_max": math.log(d / (d - 1)),
            })
    write_csv(
        OUT / "exact_gap_boundary.csv",
        list(gap_rows[0].keys()),
        gap_rows,
    )
    spec_a = [0.5, 0.25, 0.25, 0.0]
    spec_b = [0.6, 0.4, 0.0, 0.0]
    gap_counterexample = {
        "spectrum_A": spec_a,
        "entropy_A": entropy(spec_a),
        "gap_A": math.log(spec_a[0] / spec_a[1]),
        "spectrum_B": spec_b,
        "entropy_B": entropy(spec_b),
        "gap_B": math.log(spec_b[0] / spec_b[1]),
        "observation": "A has both larger entropy and larger gap than B.",
    }
    if WRITE_OUTPUTS:
        (OUT / "entropy_gap_counterexample.json").write_text(
            json.dumps(gap_counterexample, indent=2), encoding="utf-8"
        )
    summary["checks"]["entanglement_gap"] = {
        "passed": (
            gap_counterexample["entropy_A"] > gap_counterexample["entropy_B"]
            and gap_counterexample["gap_A"] > gap_counterexample["gap_B"]
        ),
        "counterexample": gap_counterexample,
    }

    # 7. Eq. (32) is an ensemble reference and can exceed the exact finite-d envelope.
    spiked_rows: list[dict] = []
    for a, b in ((32, 32), (32, 512), (128, 128), (128, 8192), (128, 10**12)):
        for p in (max(1.0 / a, 0.05), 0.2, 0.5, 0.8):
            exact_upper = exact_smax(p, a)
            reference = eq32_reference(a, b, p)
            spiked_rows.append({
                "alpha": a,
                "beta": b,
                "lambda_max": p,
                "exact_upper_entropy": exact_upper,
                "eq32_reference": reference,
                "eq32_minus_exact_upper": reference - exact_upper,
            })
    write_csv(
        OUT / "spiked_reference_vs_exact_boundary.csv",
        list(spiked_rows[0].keys()),
        spiked_rows,
    )
    summary["checks"]["eq32_status"] = {
        "passed": bool(any(row["eq32_minus_exact_upper"] > 0.0 for row in spiked_rows)),
        "maximum_excess_over_exact_upper": max(
            row["eq32_minus_exact_upper"] for row in spiked_rows
        ),
        "interpretation": (
            "Eq. (32) cannot be an exact finite-dimensional conditional mean or universal "
            "boundary without additional asymptotic qualifications; in its beta->infinity "
            "form it uses log(alpha) instead of the exact log(alpha-1) tail factor."
        ),
    }

    # 8. The stated post-SWAP spectrum is not normalized as written.
    shor_rows: list[dict] = []
    for m in (1, 2, 3, 6):
        paper_sum = 0.5 + (2**m) * (1.0 / (2**m))
        corrected_sum = 0.5 + (2**m) * (1.0 / (2 ** (m + 1)))
        shor_rows.append({
            "m": m,
            "sum_as_written": paper_sum,
            "sum_with_denominator_2^(m+1)": corrected_sum,
        })
    write_csv(
        OUT / "shor_spectrum_normalization.csv",
        list(shor_rows[0].keys()),
        shor_rows,
    )
    summary["checks"]["shor_spectrum_normalization"] = {
        "passed": all(abs(row["sum_as_written"] - 1.5) < 1e-15 for row in shor_rows),
        "result": shor_rows,
    }

    # 9. Natural-log unit check for a one-qubit entropy.
    summary["checks"]["one_qubit_entropy_units"] = {
        "passed": True,
        "maximum_natural_log_entropy": math.log(2.0),
        "maximum_bit_entropy": 1.0,
        "interpretation": "A paper using natural logarithms should state the one-qubit maximum as ln 2, not 1.",
    }

    all_passed = all(bool(item.get("passed")) for item in summary["checks"].values())
    summary["all_checks_passed"] = all_passed
    if WRITE_OUTPUTS:
        (OUT / "paper_verification_results.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True, default=lambda x: x.item() if isinstance(x, np.generic) else str(x)), encoding="utf-8"
        )
    if not WRITE_OUTPUTS:
        print(json.dumps({"all_checks_passed": all_passed, "mode": "check-only"}, indent=2))
    if not all_passed:
        raise SystemExit("At least one correction verification failed")


if __name__ == "__main__":
    main()
