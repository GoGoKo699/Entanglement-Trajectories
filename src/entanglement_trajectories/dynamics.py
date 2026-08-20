"""Deterministic dense-state-vector dynamics used by the follow-up study.

The implementation preserves the numerical conventions of the GPT-5.5 package
while separating model evolution from metric definitions.  Qubit indexing is
little-endian throughout: qubit 0 is the least-significant computational-basis
bit and forms the lower half of the default balanced cut.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Protocol

import numpy as np

from .models import ModelRun, disorder_seed, initial_state_seed


DT_RECORD_XXZ = 0.25
XXZ_TROTTER_SUBSTEPS = 1

I2 = np.eye(2, dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
HADAMARD = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2.0)
CZ_LOCAL = np.diag([1, 1, 1, -1]).astype(np.complex128)


def rx(theta: float) -> np.ndarray:
    """Return ``exp(-i theta X)``."""
    return np.cos(theta) * I2 - 1j * np.sin(theta) * X


def rz(theta: float) -> np.ndarray:
    """Return ``exp(-i theta Z)``."""
    return np.array(
        [[np.exp(-1j * theta), 0.0], [0.0, np.exp(1j * theta)]],
        dtype=np.complex128,
    )


def kron_local(low_qubit_gate: np.ndarray, high_qubit_gate: np.ndarray) -> np.ndarray:
    """Kronecker product in the local little-endian basis ``|00>,|01>,|10>,|11>``."""
    return np.kron(high_qubit_gate, low_qubit_gate)


def zz_phase_gate(theta: float) -> np.ndarray:
    """Return ``exp(-i theta Z tensor Z)`` in the local little-endian basis."""
    return np.diag(
        [
            np.exp(-1j * theta),
            np.exp(1j * theta),
            np.exp(1j * theta),
            np.exp(-1j * theta),
        ]
    ).astype(np.complex128)


def xxz_pair_gate(delta: float, dt: float) -> np.ndarray:
    """Return ``exp[-i dt (XX + YY + delta ZZ)]`` for one adjacent pair."""
    out = np.zeros((4, 4), dtype=np.complex128)
    phase_parallel = np.exp(-1j * dt * delta)
    out[0, 0] = phase_parallel
    out[3, 3] = phase_parallel

    phase_antiparallel = np.exp(1j * dt * delta)
    c = np.cos(2.0 * dt)
    s = np.sin(2.0 * dt)
    out[1, 1] = phase_antiparallel * c
    out[2, 2] = phase_antiparallel * c
    out[1, 2] = phase_antiparallel * (-1j * s)
    out[2, 1] = phase_antiparallel * (-1j * s)
    return out


def apply_1q_gate_inplace(psi: np.ndarray, gate: np.ndarray, q: int) -> None:
    """Apply a one-qubit gate to little-endian qubit ``q``."""
    if psi.ndim != 1 or psi.size == 0 or psi.size & (psi.size - 1):
        raise ValueError("psi must be a nonempty power-of-two state vector.")
    if gate.shape != (2, 2):
        raise ValueError("gate must have shape (2,2).")
    n = int(round(math.log2(psi.size)))
    if q < 0 or q >= n:
        raise IndexError(q)
    stride = 1 << q
    period = stride << 1
    blocks = psi.reshape(-1, period)
    a0 = blocks[:, :stride].copy()
    a1 = blocks[:, stride:period].copy()
    blocks[:, :stride] = gate[0, 0] * a0 + gate[0, 1] * a1
    blocks[:, stride:period] = gate[1, 0] * a0 + gate[1, 1] * a1


def apply_1q_layer_inplace(psi: np.ndarray, gate: np.ndarray, n: int) -> None:
    for q in range(n):
        apply_1q_gate_inplace(psi, gate, q)


def apply_2q_adjacent_gate_inplace(psi: np.ndarray, gate: np.ndarray, q: int) -> None:
    """Apply a gate to adjacent little-endian qubits ``(q,q+1)``."""
    if gate.shape != (4, 4):
        raise ValueError("gate must have shape (4,4).")
    n = int(round(math.log2(psi.size)))
    if q < 0 or q + 1 >= n:
        raise IndexError(q)
    stride = 1 << q
    period = stride << 2
    blocks = psi.reshape(-1, period)
    vec = [blocks[:, i * stride : (i + 1) * stride].copy() for i in range(4)]
    for row in range(4):
        blocks[:, row * stride : (row + 1) * stride] = sum(
            gate[row, col] * vec[col] for col in range(4)
        )


def apply_even_odd_layer_inplace(
    psi: np.ndarray, gate: np.ndarray, n: int, parity: int
) -> None:
    if parity not in (0, 1):
        raise ValueError("parity must be 0 or 1.")
    for q in range(parity, n - 1, 2):
        apply_2q_adjacent_gate_inplace(psi, gate, q)


def basis_state(n: int, index: int) -> np.ndarray:
    if n < 1 or index < 0 or index >= 1 << n:
        raise ValueError("Invalid basis-state request.")
    psi = np.zeros(1 << n, dtype=np.complex128)
    psi[index] = 1.0
    return psi


def neel_state(n: int) -> np.ndarray:
    """Return ``|0101...>`` with bit ``q=q mod 2`` in little-endian order."""
    idx = sum(1 << q for q in range(n) if q & 1)
    return basis_state(n, idx)


def random_product_state(n: int, seed: int) -> np.ndarray:
    """Deterministic product of independently Haar-uniform one-qubit states."""
    rng = np.random.default_rng(int(seed))
    psi = np.array([1.0 + 0.0j], dtype=np.complex128)
    for _ in range(n):
        u, v = rng.random(2)
        theta = np.arccos(1.0 - 2.0 * u)
        phi = 2.0 * np.pi * v
        a0 = np.cos(theta / 2.0)
        a1 = np.exp(1j * phi) * np.sin(theta / 2.0)
        psi = np.concatenate([a0 * psi, a1 * psi])
    return psi.astype(np.complex128, copy=False)


def baker_localized_basis_state(n: int) -> np.ndarray:
    """The deterministic localized basis state used in the historical package."""
    index = int(0.37 * (1 << n)) % (1 << n)
    return basis_state(n, index)


def initialize_state(run: ModelRun, n: int) -> np.ndarray:
    if run.initial_state == "neel":
        return neel_state(n)
    if run.initial_state == "basis_localized":
        return baker_localized_basis_state(n)
    if run.initial_state == "random_product":
        seed = initial_state_seed(run.model, n, run.run_id)
        assert seed is not None
        return random_product_state(n, seed)
    raise ValueError(f"Unknown initial state: {run.initial_state!r}")


def state_norm(psi: np.ndarray) -> float:
    return float(np.vdot(psi, psi).real)


def single_qubit_spectra(psi: np.ndarray, n: int) -> np.ndarray:
    """Return ordered spectra of all one-qubit reductions, shape ``(n,2)``."""
    norm2 = state_norm(psi)
    if norm2 <= 0.0:
        raise ValueError("State has zero norm.")
    out = np.empty((n, 2), dtype=np.float64)
    for q in range(n):
        stride = 1 << q
        period = stride << 1
        blocks = psi.reshape(-1, period)
        a0 = blocks[:, :stride]
        a1 = blocks[:, stride:period]
        rho00 = float(np.vdot(a0, a0).real) / norm2
        rho11 = float(np.vdot(a1, a1).real) / norm2
        rho01 = np.vdot(a1, a0) / norm2
        det = float(np.clip(rho00 * rho11 - abs(rho01) ** 2, 0.0, 0.25))
        delta = math.sqrt(max(0.0, 1.0 - 4.0 * det))
        out[q] = (0.5 * (1.0 + delta), 0.5 * (1.0 - delta))
    return out


def half_chain_spectrum(psi: np.ndarray, n: int) -> np.ndarray:
    """Ordered reduced spectrum for the lower-half balanced cut."""
    if n < 2:
        raise ValueError("n must be at least 2.")
    m = n // 2
    d_a = 1 << m
    d_b = 1 << (n - m)
    if psi.shape != (1 << n,):
        raise ValueError(f"psi must have shape {(1 << n,)}.")
    norm2 = state_norm(psi)
    if norm2 <= 0.0:
        raise ValueError("State has zero norm.")
    matrix = psi.reshape(d_b, d_a).T
    rho = matrix @ matrix.conj().T
    rho /= norm2
    eig = np.linalg.eigvalsh(rho).real
    if eig.min(initial=0.0) < -1e-10:
        raise ArithmeticError(f"Reduced spectrum has material negativity: {eig.min()}")
    eig[eig < 0.0] = 0.0
    total = float(eig.sum())
    if total <= 0.0:
        raise ArithmeticError("Reduced spectrum has zero trace.")
    eig /= total
    eig.sort()
    return eig[::-1].copy()


class Evolver(Protocol):
    def step(self, psi: np.ndarray) -> None: ...


@dataclass
class QCAEvolver:
    n: int
    cell_gate: np.ndarray

    def step(self, psi: np.ndarray) -> None:
        apply_even_odd_layer_inplace(psi, self.cell_gate, self.n, parity=0)
        apply_even_odd_layer_inplace(psi, self.cell_gate, self.n, parity=1)


@dataclass
class KickedIsingEvolver:
    n: int
    rx_gate: np.ndarray
    diagonal_phase: np.ndarray

    def step(self, psi: np.ndarray) -> None:
        apply_1q_layer_inplace(psi, self.rx_gate, self.n)
        psi *= self.diagonal_phase


@dataclass
class BakerEvolver:
    n: int
    perturb_phase: np.ndarray | None

    def step(self, psi: np.ndarray) -> None:
        half = psi.size >> 1
        tmp = np.empty_like(psi)
        tmp[:half] = np.fft.fft(psi[:half], norm="ortho")
        tmp[half:] = np.fft.fft(psi[half:], norm="ortho")
        psi[:] = np.fft.ifft(tmp, norm="ortho")
        if self.perturb_phase is not None:
            psi *= self.perturb_phase


@dataclass
class XXZEvolver:
    n: int
    pair_half: np.ndarray
    pair_full: np.ndarray
    z_half_phase: np.ndarray
    substeps: int = XXZ_TROTTER_SUBSTEPS

    def step(self, psi: np.ndarray) -> None:
        for _ in range(self.substeps):
            psi *= self.z_half_phase
            apply_even_odd_layer_inplace(psi, self.pair_half, self.n, parity=0)
            apply_even_odd_layer_inplace(psi, self.pair_full, self.n, parity=1)
            apply_even_odd_layer_inplace(psi, self.pair_half, self.n, parity=0)
            psi *= self.z_half_phase


def qca_cell_gate(kind: str) -> np.ndarray:
    if kind == "clifford":
        return CZ_LOCAL @ kron_local(HADAMARD, HADAMARD)
    if kind == "nonclifford":
        return zz_phase_gate(0.73) @ kron_local(rx(0.37), rz(0.61)) @ CZ_LOCAL
    raise ValueError(f"Unknown QCA cell gate: {kind!r}")


def diagonal_z_phase(n: int, coeffs: np.ndarray, dt: float) -> np.ndarray:
    """Return ``exp[-i dt sum_q coeffs[q] Z_q]`` as a diagonal vector."""
    coeffs = np.asarray(coeffs, dtype=np.float64)
    if coeffs.shape != (n,):
        raise ValueError(f"coeffs must have shape {(n,)}.")
    indices = np.arange(1 << n, dtype=np.uint64)
    angle = np.zeros(1 << n, dtype=np.float64)
    for q in range(n):
        bit = ((indices >> np.uint64(q)) & np.uint64(1)).astype(np.float64)
        angle += coeffs[q] * (1.0 - 2.0 * bit)
    return np.exp(-1j * dt * angle).astype(np.complex128)


def kicked_ising_diagonal_phase(n: int, J: float, hz: float) -> np.ndarray:
    """Return ``exp[-i(J sum ZZ + hz sum Z)]`` for an open chain."""
    indices = np.arange(1 << n, dtype=np.uint64)
    angle = np.zeros(1 << n, dtype=np.float64)
    z_values: list[np.ndarray] = []
    for q in range(n):
        bit = ((indices >> np.uint64(q)) & np.uint64(1)).astype(np.float64)
        zq = 1.0 - 2.0 * bit
        z_values.append(zq)
        angle += hz * zq
    for q in range(n - 1):
        angle += J * z_values[q] * z_values[q + 1]
    return np.exp(-1j * angle).astype(np.complex128)


def baker_perturb_phase(n: int, epsilon: float) -> np.ndarray | None:
    if abs(epsilon) == 0.0:
        return None
    N = 1 << n
    q = np.arange(N, dtype=np.float64)
    return np.exp(-1j * epsilon * np.cos(2.0 * np.pi * q / N)).astype(np.complex128)


def xxz_disorder_fields(run: ModelRun, n: int) -> np.ndarray:
    if run.model != "random_field_xxz":
        raise ValueError("XXZ disorder fields requested for a non-XXZ run.")
    seed = disorder_seed(run.model, n, run.run_id)
    assert seed is not None
    rng = np.random.default_rng(seed)
    return rng.uniform(-float(run.parameters["W"]), float(run.parameters["W"]), size=n)


def build_evolver(run: ModelRun, n: int) -> Evolver:
    p = run.parameters
    if run.model == "qca":
        return QCAEvolver(n=n, cell_gate=qca_cell_gate(str(p["cell_gate"])))
    if run.model == "kicked_ising":
        return KickedIsingEvolver(
            n=n,
            rx_gate=rx(float(p["hx"])),
            diagonal_phase=kicked_ising_diagonal_phase(n, float(p["J"]), float(p["hz"])),
        )
    if run.model == "quantum_baker":
        return BakerEvolver(n=n, perturb_phase=baker_perturb_phase(n, float(p["epsilon"])))
    if run.model == "random_field_xxz":
        substeps = int(p.get("trotter_substeps", XXZ_TROTTER_SUBSTEPS))
        dt_record = float(p.get("dt_record", DT_RECORD_XXZ))
        dt = dt_record / substeps
        fields = xxz_disorder_fields(run, n)
        return XXZEvolver(
            n=n,
            pair_half=xxz_pair_gate(float(p["Delta"]), 0.5 * dt),
            pair_full=xxz_pair_gate(float(p["Delta"]), dt),
            z_half_phase=diagonal_z_phase(n, fields, 0.5 * dt),
            substeps=substeps,
        )
    raise ValueError(f"Unknown model: {run.model!r}")
