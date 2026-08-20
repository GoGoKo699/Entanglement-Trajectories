"""Trajectory simulation and canonical observable extraction."""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

import numpy as np

from .aggregates import mean_cut_metric
from .dataset import CANONICAL_COLUMNS, SCHEMA_VERSION, canonical_to_legacy
from .dynamics import (
    build_evolver,
    half_chain_spectrum,
    initialize_state,
    single_qubit_spectra,
    state_norm,
)
from .metrics import (
    geometric_entanglement_linear,
    linear_entropy,
    log_negativity_pure,
    min_entropy,
    von_neumann_entropy,
)
from .models import MODEL_ORDER, ModelRun, all_runs, disorder_seed, initial_state_seed


DEFAULT_SYSTEM_SIZES: tuple[int, ...] = (10, 12, 14, 16, 18, 20)


def metrics_from_spectrum(lam: np.ndarray) -> dict[str, float]:
    """Canonical normalized half-chain metrics from one reduced spectrum."""
    d = int(np.asarray(lam).size)
    return {
        "half_vn": von_neumann_entropy(lam, base=2.0, normalized=True),
        "half_linear": linear_entropy(lam, normalized=True),
        "half_logneg": log_negativity_pure(lam, base=2.0, normalized=True),
        "half_geometric_linear": geometric_entanglement_linear(lam, normalized=True),
        "half_lambda_max": float(np.max(lam)),
        "half_min_entropy": min_entropy(lam, base=2.0, normalized=True),
    }


def one_site_mean_metrics(spectra: np.ndarray) -> dict[str, float]:
    """Means over all one-site-versus-rest cuts.

    These are aggregates over a collection of cuts, not functions of one
    half-chain spectrum and not generic multipartite entanglement measures.
    """
    return {
        "one_site_mean_vn": mean_cut_metric(spectra, "von_neumann_entropy", normalized=True),
        "one_site_mean_linear": mean_cut_metric(spectra, "linear_entropy", normalized=True),
        "one_site_mean_logneg": mean_cut_metric(spectra, "log_negativity_pure", normalized=True),
        "one_site_mean_geometric_linear": mean_cut_metric(
            spectra, "geometric_linear", normalized=True
        ),
    }


def all_observables(psi: np.ndarray, n: int) -> dict[str, float]:
    one_site = single_qubit_spectra(psi, n)
    half = half_chain_spectrum(psi, n)
    return {**one_site_mean_metrics(one_site), **metrics_from_spectrum(half)}


def iter_run_observations(
    run: ModelRun,
    n: int,
    *,
    max_steps: int | None = None,
    measure_every: int = 1,
    save_spectra: bool = False,
) -> Iterator[tuple[dict[str, Any], np.ndarray | None]]:
    """Yield canonical rows and optional half-chain spectra for one trajectory."""
    if n < 2 or measure_every < 1:
        raise ValueError("n must be at least two and measure_every at least one.")
    total_steps = 4 * n if max_steps is None else int(max_steps)
    if total_steps < 0:
        raise ValueError("max_steps must be nonnegative.")
    psi = initialize_state(run, n)
    evolver = build_evolver(run, n)
    init_seed = initial_state_seed(run.model, n, run.run_id)
    field_seed = disorder_seed(run.model, n, run.run_id)

    for step in range(total_steps + 1):
        if step % measure_every == 0:
            spectrum = half_chain_spectrum(psi, n)
            row = {
                "schema_version": SCHEMA_VERSION,
                "model": run.model,
                "n": int(n),
                "run_id": run.run_id,
                "regime": run.regime,
                "initial_state": run.initial_state,
                "step": int(step),
                "tau": float(step / n),
                "initial_state_seed": init_seed,
                "disorder_seed": field_seed,
                **one_site_mean_metrics(single_qubit_spectra(psi, n)),
                **metrics_from_spectrum(spectrum),
            }
            yield row, spectrum.copy() if save_spectra else None
        if step < total_steps:
            evolver.step(psi)

    final_norm = state_norm(psi)
    if abs(final_norm - 1.0) > 1e-8:
        raise ArithmeticError(f"Final state norm drifted to {final_norm:.17g}.")


def simulate_frame(
    *,
    system_sizes: Iterable[int] = DEFAULT_SYSTEM_SIZES,
    models: Iterable[str] = MODEL_ORDER,
    run_ids: Iterable[str] | None = None,
    max_steps: int | None = None,
    measure_every: int = 1,
    verbose: bool = False,
):
    """Simulate selected runs and return a canonical pandas DataFrame."""
    import pandas as pd

    wanted = None if run_ids is None else set(run_ids)
    rows: list[dict[str, Any]] = []
    for n in system_sizes:
        for run in all_runs(models):
            if wanted is not None and run.run_id not in wanted:
                continue
            if verbose:
                print(f"n={int(n):2d} model={run.model:18s} run={run.run_id}", flush=True)
            rows.extend(
                row
                for row, _ in iter_run_observations(
                    run,
                    int(n),
                    max_steps=max_steps,
                    measure_every=measure_every,
                    save_spectra=False,
                )
            )
    if not rows:
        raise ValueError("No trajectories selected.")
    frame = pd.DataFrame(rows)
    return frame.loc[:, CANONICAL_COLUMNS].sort_values(
        ["n", "model", "run_id", "step"]
    ).reset_index(drop=True)


def write_simulation(
    frame,
    output: str | Path,
    *,
    legacy_schema: bool = False,
) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if legacy_schema:
        canonical_to_legacy(frame).to_csv(output, index=False, float_format="%.17g")
    else:
        frame.loc[:, CANONICAL_COLUMNS].to_csv(output, index=False, float_format="%.17g")
    return output
