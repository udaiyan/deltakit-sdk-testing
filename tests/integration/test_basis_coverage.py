"""Basis coverage tests: run the full pipeline across every combination
of code stabiliser basis and logical memory basis.

The QEC pipeline has two independent choices:
  1. The code's stabiliser basis (Z or X) - what the code watches for
  2. The logical basis of the memory experiment - which logical operator
     is being protected

The four combinations are:
  - Z-stabiliser code, Z logical memory  (bit-flip protection)
  - Z-stabiliser code, X logical memory  (dual - tests SDK consistency)
  - X-stabiliser code, Z logical memory  (dual - tests SDK consistency)
  - X-stabiliser code, X logical memory  (phase-flip protection)

For RotatedPlanarCode, which has both X and Z stabilisers natively,
both logical bases are physically meaningful.

Running the pipeline across all combinations surfaces any combination-
specific bugs that single-basis tests would miss.
"""
import numpy as np
import pytest

from deltakit.circuit.gates import PauliBasis
from deltakit.explorer.codes import (
    RepetitionCode,
    RotatedPlanarCode,
    css_code_memory_circuit,
)
from deltakit.explorer.qpu import QPU, SI1000Noise
from deltakit.explorer.simulation import simulate_with_stim


SHOTS = 1000
LOW_P = 0.001
HIGH_P = 0.02


REP_COMBINATIONS = [
    (PauliBasis.Z, PauliBasis.Z, "Zstab-Zlogical"),
    (PauliBasis.Z, PauliBasis.X, "Zstab-Xlogical"),
    (PauliBasis.X, PauliBasis.Z, "Xstab-Zlogical"),
    (PauliBasis.X, PauliBasis.X, "Xstab-Xlogical"),
]
REP_IDS = [c[2] for c in REP_COMBINATIONS]

PLANAR_COMBINATIONS = [
    (PauliBasis.Z, "Zlogical"),
    (PauliBasis.X, "Xlogical"),
]
PLANAR_IDS = [c[1] for c in PLANAR_COMBINATIONS]


def build_rep_stim(stab_basis, logical_basis, p=0.01):
    code = RepetitionCode(distance=3, stabiliser_type=stab_basis)
    circuit = css_code_memory_circuit(
        css_code=code, num_rounds=3, logical_basis=logical_basis
    )
    qpu = QPU(qubits=circuit.qubits, noise_model=SI1000Noise(p=p))
    return qpu.compile_and_add_noise_to_circuit(circuit).as_stim_circuit()


def build_planar_stim(logical_basis, p=0.01):
    code = RotatedPlanarCode(width=3, height=3)
    circuit = css_code_memory_circuit(
        css_code=code, num_rounds=3, logical_basis=logical_basis
    )
    qpu = QPU(qubits=circuit.qubits, noise_model=SI1000Noise(p=p))
    return qpu.compile_and_add_noise_to_circuit(circuit).as_stim_circuit()


def run_pipeline(stim_circuit, shots=SHOTS):
    measurements, leakage = simulate_with_stim(stim_circuit, shots=shots)
    detectors, observables = measurements.to_detectors_and_observables(
        stim_circuit
    )
    return measurements, detectors, observables


@pytest.mark.integration
class TestRepetitionCodeBasisCoverage:

    @pytest.mark.parametrize(
        "stab_basis,logical_basis,label", REP_COMBINATIONS, ids=REP_IDS
    )
    def test_pipeline_completes(self, stab_basis, logical_basis, label):
        stim_circuit = build_rep_stim(stab_basis, logical_basis)
        measurements, _, _ = run_pipeline(stim_circuit)
        assert measurements.as_numpy().shape[0] == SHOTS

    @pytest.mark.parametrize(
        "stab_basis,logical_basis,label", REP_COMBINATIONS, ids=REP_IDS
    )
    def test_measurements_are_binary(self, stab_basis, logical_basis, label):
        stim_circuit = build_rep_stim(stab_basis, logical_basis)
        measurements, _, _ = run_pipeline(stim_circuit)
        arr = measurements.as_numpy()
        assert set(np.unique(arr).tolist()).issubset({0, 1})

    @pytest.mark.parametrize(
        "stab_basis,logical_basis,label", REP_COMBINATIONS, ids=REP_IDS
    )
    def test_detector_conversion_produces_arrays(
        self, stab_basis, logical_basis, label
    ):
        stim_circuit = build_rep_stim(stab_basis, logical_basis)
        _, detectors, observables = run_pipeline(stim_circuit)
        assert detectors.as_numpy().shape[0] == SHOTS
        assert observables.as_numpy().shape[0] == SHOTS
        assert detectors.as_numpy().dtype == np.uint8
        assert observables.as_numpy().dtype == np.uint8

    @pytest.mark.parametrize(
        "stab_basis,logical_basis,label", REP_COMBINATIONS, ids=REP_IDS
    )
    def test_zero_noise_produces_no_detections(
        self, stab_basis, logical_basis, label
    ):
        """At p=0, no detector event should fire for any combination."""
        stim_circuit = build_rep_stim(stab_basis, logical_basis, p=0.0)
        _, detectors, _ = run_pipeline(stim_circuit)
        total = detectors.as_numpy().sum()
        assert total == 0, f"{label}: {total} events fired at p=0"

    @pytest.mark.parametrize(
        "stab_basis,logical_basis,label", REP_COMBINATIONS, ids=REP_IDS
    )
    def test_higher_noise_yields_more_detections(
        self, stab_basis, logical_basis, label
    ):
        stim_low = build_rep_stim(stab_basis, logical_basis, p=LOW_P)
        stim_high = build_rep_stim(stab_basis, logical_basis, p=HIGH_P)
        _, det_low, _ = run_pipeline(stim_low)
        _, det_high, _ = run_pipeline(stim_high)
        rate_low = det_low.as_numpy().mean()
        rate_high = det_high.as_numpy().mean()
        assert rate_high > rate_low, (
            f"{label}: rate did not increase: "
            f"{rate_low:.4f} -> {rate_high:.4f}"
        )


@pytest.mark.integration
class TestRotatedPlanarCodeBasisCoverage:

    @pytest.mark.parametrize(
        "logical_basis,label", PLANAR_COMBINATIONS, ids=PLANAR_IDS
    )
    def test_pipeline_completes(self, logical_basis, label):
        stim_circuit = build_planar_stim(logical_basis)
        measurements, _, _ = run_pipeline(stim_circuit)
        assert measurements.as_numpy().shape[0] == SHOTS

    @pytest.mark.parametrize(
        "logical_basis,label", PLANAR_COMBINATIONS, ids=PLANAR_IDS
    )
    def test_detector_conversion_produces_arrays(self, logical_basis, label):
        stim_circuit = build_planar_stim(logical_basis)
        _, detectors, observables = run_pipeline(stim_circuit)
        assert detectors.as_numpy().shape[0] == SHOTS
        assert observables.as_numpy().shape[0] == SHOTS

    @pytest.mark.parametrize(
        "logical_basis,label", PLANAR_COMBINATIONS, ids=PLANAR_IDS
    )
    def test_zero_noise_produces_no_detections(self, logical_basis, label):
        stim_circuit = build_planar_stim(logical_basis, p=0.0)
        _, detectors, _ = run_pipeline(stim_circuit)
        total = detectors.as_numpy().sum()
        assert total == 0, f"{label}: {total} events fired at p=0"

    @pytest.mark.parametrize(
        "logical_basis,label", PLANAR_COMBINATIONS, ids=PLANAR_IDS
    )
    def test_higher_noise_yields_more_detections(self, logical_basis, label):
        stim_low = build_planar_stim(logical_basis, p=LOW_P)
        stim_high = build_planar_stim(logical_basis, p=HIGH_P)
        _, det_low, _ = run_pipeline(stim_low)
        _, det_high, _ = run_pipeline(stim_high)
        rate_low = det_low.as_numpy().mean()
        rate_high = det_high.as_numpy().mean()
        assert rate_high > rate_low, (
            f"{label}: rate did not increase: "
            f"{rate_low:.4f} -> {rate_high:.4f}"
        )