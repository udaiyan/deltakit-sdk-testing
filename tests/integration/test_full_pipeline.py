"""Integration tests: the end-to-end QEC pipeline."""
import numpy as np
import pytest

from deltakit.circuit.gates import PauliBasis
from deltakit.explorer.codes import css_code_memory_circuit
from deltakit.explorer.qpu import QPU, SI1000Noise
from deltakit.explorer.simulation import simulate_with_stim


SHOTS = 1000


def build_noisy_stim_circuit(code, num_rounds=3, p=0.01):
    circuit = css_code_memory_circuit(
        css_code=code, num_rounds=num_rounds, logical_basis=PauliBasis.Z
    )
    qpu = QPU(qubits=circuit.qubits, noise_model=SI1000Noise(p=p))
    noisy = qpu.compile_and_add_noise_to_circuit(circuit)
    return noisy.as_stim_circuit(), circuit


@pytest.mark.integration
class TestFullPipelineRuns:

    def test_repetition_code_pipeline(self, rep_code_d3):
        stim_circuit, _ = build_noisy_stim_circuit(rep_code_d3)
        result = simulate_with_stim(stim_circuit, shots=SHOTS)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_returns_measurements_object(self, rep_code_d3):
        stim_circuit, _ = build_noisy_stim_circuit(rep_code_d3)
        measurements, leakage = simulate_with_stim(stim_circuit, shots=SHOTS)
        assert measurements is not None
        assert leakage is None

    def test_measurements_shape(self, rep_code_d3):
        stim_circuit, _ = build_noisy_stim_circuit(rep_code_d3)
        measurements, _ = simulate_with_stim(stim_circuit, shots=SHOTS)
        arr = measurements.as_numpy()
        assert arr.shape[0] == SHOTS

    def test_measurements_are_binary(self, rep_code_d3):
        stim_circuit, _ = build_noisy_stim_circuit(rep_code_d3)
        measurements, _ = simulate_with_stim(stim_circuit, shots=100)
        arr = measurements.as_numpy()
        assert set(np.unique(arr).tolist()).issubset({0, 1})

    def test_planar_code_pipeline(self, rotated_planar_3x3):
        stim_circuit, _ = build_noisy_stim_circuit(rotated_planar_3x3)
        measurements, _ = simulate_with_stim(stim_circuit, shots=SHOTS)
        assert measurements.as_numpy().shape[0] == SHOTS


@pytest.mark.integration
class TestDetectorsAndObservables:

    def test_detector_conversion_produces_arrays(self, rep_code_d3):
        stim_circuit, _ = build_noisy_stim_circuit(rep_code_d3)
        measurements, _ = simulate_with_stim(stim_circuit, shots=SHOTS)
        detectors, observables = (
            measurements.to_detectors_and_observables(stim_circuit)
        )
        det_arr = detectors.as_numpy()
        obs_arr = observables.as_numpy()
        assert det_arr.shape[0] == SHOTS
        assert obs_arr.shape[0] == SHOTS
        assert det_arr.dtype == np.uint8
        assert obs_arr.dtype == np.uint8

    def test_observables_are_binary(self, rep_code_d3):
        stim_circuit, _ = build_noisy_stim_circuit(rep_code_d3)
        measurements, _ = simulate_with_stim(stim_circuit, shots=SHOTS)
        _, observables = measurements.to_detectors_and_observables(stim_circuit)
        obs_arr = observables.as_numpy()
        assert set(np.unique(obs_arr).tolist()).issubset({0, 1})


@pytest.mark.integration
class TestPhysicalInvariants:

    def test_higher_noise_yields_more_detector_events(self, rep_code_d3):
        low_p = 0.001
        high_p = 0.02

        def detector_rate(p):
            stim_circuit, _ = build_noisy_stim_circuit(rep_code_d3, p=p)
            measurements, _ = simulate_with_stim(stim_circuit, shots=SHOTS)
            detectors, _ = measurements.to_detectors_and_observables(
                stim_circuit
            )
            return detectors.as_numpy().mean()

        low_rate = detector_rate(low_p)
        high_rate = detector_rate(high_p)
        assert high_rate > low_rate, (
            "detector rate did not increase with noise: "
            + str(low_rate) + " -> " + str(high_rate)
        )

    def test_zero_noise_produces_no_detections(self, rep_code_d3):
        stim_circuit, _ = build_noisy_stim_circuit(rep_code_d3, p=0.0)
        measurements, _ = simulate_with_stim(stim_circuit, shots=SHOTS)
        detectors, _ = measurements.to_detectors_and_observables(stim_circuit)
        arr = detectors.as_numpy()
        assert arr.sum() == 0, str(arr.sum()) + " detector events fired at p=0"
