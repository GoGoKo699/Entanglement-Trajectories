"""Canonical model and run registry for the quantum-chaos follow-up study.

The registry makes every dynamical family, parameter choice, initial-state
choice, and deterministic seed rule explicit.  The names preserve the 2026
follow-up data IDs while replacing ambiguous human-facing labels.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from typing import Any, Iterable


MODEL_ORDER: tuple[str, ...] = (
    "qca",
    "kicked_ising",
    "quantum_baker",
    "random_field_xxz",
)

MODEL_LABELS: dict[str, str] = {
    "qca": "Brickwork Floquet QCA",
    "kicked_ising": "Open-chain kicked Ising",
    "quantum_baker": "Balazs-Voros-style quantum baker",
    "random_field_xxz": "Random-field XXZ product-formula circuit",
}


@dataclass(frozen=True)
class ModelRun:
    """One deterministic trajectory family member."""

    model: str
    run_id: str
    regime: str
    initial_state: str
    parameters: dict[str, Any]
    description: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def stable_seed(*items: object) -> int:
    """Stable 32-bit seed independent of Python hash randomization."""
    payload = repr(items).encode("utf-8")
    digest = hashlib.blake2b(payload, digest_size=8).digest()
    return int.from_bytes(digest, "little") & 0xFFFFFFFF


def qca_runs() -> list[ModelRun]:
    return [
        ModelRun(
            "qca",
            "QCA_1",
            "clifford_reference",
            "neel",
            {"cell_gate": "clifford", "boundary": "open", "brickwork": "even_then_odd"},
            "Clifford brickwork reference from a Neel product state.",
        ),
        ModelRun(
            "qca",
            "QCA_2",
            "clifford_reference",
            "random_product",
            {"cell_gate": "clifford", "boundary": "open", "brickwork": "even_then_odd"},
            "Clifford brickwork reference from a deterministic Haar-random product state.",
        ),
        ModelRun(
            "qca",
            "QCA_3",
            "nonclifford_scrambling",
            "neel",
            {
                "cell_gate": "nonclifford",
                "zz_angle": 0.73,
                "rx_low_angle": 0.37,
                "rz_high_angle": 0.61,
                "boundary": "open",
                "brickwork": "even_then_odd",
            },
            "Non-Clifford brickwork Floquet circuit from a Neel product state.",
        ),
        ModelRun(
            "qca",
            "QCA_4",
            "nonclifford_scrambling",
            "random_product",
            {
                "cell_gate": "nonclifford",
                "zz_angle": 0.73,
                "rx_low_angle": 0.37,
                "rz_high_angle": 0.61,
                "boundary": "open",
                "brickwork": "even_then_odd",
            },
            "Non-Clifford brickwork Floquet circuit from a deterministic random product state.",
        ),
    ]


def kicked_ising_runs() -> list[ModelRun]:
    base = {"J": 0.7, "hx": 1.05, "boundary": "open", "floquet_order": "x_kick_then_zz_z"}
    return [
        ModelRun(
            "kicked_ising",
            "KI_1",
            "transverse_reference",
            "neel",
            {**base, "hz": 0.0},
            "Transverse-field reference from a Neel product state.",
        ),
        ModelRun(
            "kicked_ising",
            "KI_2",
            "transverse_reference",
            "random_product",
            {**base, "hz": 0.0},
            "Transverse-field reference from a deterministic random product state.",
        ),
        ModelRun(
            "kicked_ising",
            "KI_3",
            "tilted_field",
            "neel",
            {**base, "hz": 0.5},
            "Tilted-field kicked Ising trajectory from a Neel product state.",
        ),
        ModelRun(
            "kicked_ising",
            "KI_4",
            "tilted_field",
            "random_product",
            {**base, "hz": 0.5},
            "Tilted-field kicked Ising trajectory from a deterministic random product state.",
        ),
    ]


def baker_runs() -> list[ModelRun]:
    base = {"fourier_convention": "numpy_ortho", "boundary_phases": "periodic_fft_convention"}
    return [
        ModelRun(
            "quantum_baker",
            "QB_1",
            "standard",
            "basis_localized",
            {**base, "epsilon": 0.0},
            "Balazs-Voros-style baker map from a deterministic localized basis state.",
        ),
        ModelRun(
            "quantum_baker",
            "QB_2",
            "standard",
            "random_product",
            {**base, "epsilon": 0.0},
            "Balazs-Voros-style baker map from a deterministic random product state.",
        ),
        ModelRun(
            "quantum_baker",
            "QB_3",
            "phase_perturbed",
            "basis_localized",
            {**base, "epsilon": 0.3, "phase": "exp[-i epsilon cos(2 pi q/N)]"},
            "Phase-perturbed baker map from a localized basis state.",
        ),
        ModelRun(
            "quantum_baker",
            "QB_4",
            "phase_perturbed",
            "random_product",
            {**base, "epsilon": 0.3, "phase": "exp[-i epsilon cos(2 pi q/N)]"},
            "Phase-perturbed baker map from a deterministic random product state.",
        ),
    ]


def xxz_runs() -> list[ModelRun]:
    base = {
        "Delta": 1.0,
        "dt_record": 0.25,
        "trotter_substeps": 1,
        "trotter_order": "second_order_field_even_odd_even_field",
        "simulation_interpretation": "fixed one-substep symmetric product-formula circuit",
        "boundary": "open",
    }
    return [
        ModelRun(
            "random_field_xxz",
            "XXZ_1",
            "weak_disorder",
            "neel",
            {**base, "W": 0.5},
            "Weak-disorder XXZ trajectory from a Neel product state.",
        ),
        ModelRun(
            "random_field_xxz",
            "XXZ_2",
            "weak_disorder",
            "random_product",
            {**base, "W": 0.5},
            "Weak-disorder XXZ trajectory from a deterministic random product state.",
        ),
        ModelRun(
            "random_field_xxz",
            "XXZ_3",
            "strong_disorder",
            "neel",
            {**base, "W": 8.0},
            "Strong-disorder XXZ trajectory from a Neel product state.",
        ),
        ModelRun(
            "random_field_xxz",
            "XXZ_4",
            "strong_disorder",
            "random_product",
            {**base, "W": 8.0},
            "Strong-disorder XXZ trajectory from a deterministic random product state.",
        ),
    ]


MODEL_RUN_FACTORIES = {
    "qca": qca_runs,
    "kicked_ising": kicked_ising_runs,
    "quantum_baker": baker_runs,
    "random_field_xxz": xxz_runs,
}


def all_runs(models: Iterable[str] | None = None) -> list[ModelRun]:
    selected = MODEL_ORDER if models is None else tuple(models)
    rows: list[ModelRun] = []
    for model in selected:
        if model not in MODEL_RUN_FACTORIES:
            raise KeyError(f"Unknown model {model!r}; available: {sorted(MODEL_RUN_FACTORIES)}")
        rows.extend(MODEL_RUN_FACTORIES[model]())
    return rows


def run_by_id(run_id: str) -> ModelRun:
    for run in all_runs():
        if run.run_id == run_id:
            return run
    raise KeyError(run_id)


def initial_state_seed(model: str, n: int, run_id: str) -> int | None:
    run = run_by_id(run_id)
    if run.model != model:
        raise ValueError(f"Run {run_id} belongs to {run.model}, not {model}.")
    if run.initial_state != "random_product":
        return None
    return stable_seed("init", model, int(n), run_id)


def disorder_seed(model: str, n: int, run_id: str) -> int | None:
    run = run_by_id(run_id)
    if run.model != model:
        raise ValueError(f"Run {run_id} belongs to {run.model}, not {model}.")
    if model != "random_field_xxz":
        return None
    return stable_seed("xxz_disorder", int(n), run_id)
