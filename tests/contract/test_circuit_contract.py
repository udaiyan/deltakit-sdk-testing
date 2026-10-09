"""Contract tests: the public API returns what it promises.

Contract tests assert on shape and type of return values - not on the
internal values themselves. They catch silent API drift: a function that
keeps running but returns a different structure than callers expect.
"""
import pytest

from deltakit.circuit.gates import PauliBasis
from deltakit.explorer.codes import css_code_memory_circuit


@pytest.mark.contract
class TestCssCodeMemoryCircuitContract:

    def test_returns_circuit_object(self, rep_code_d3):
        circuit = css_code_memory_circuit(
            css_code=rep_code_d3, num_rounds=3, logical_basis=PauliBasis.Z
        )
        assert hasattr(circuit, "qubits")
        assert hasattr(circuit, "as_stim_circuit")

    def test_circuit_has_qubits(self, rep_code_d3):
        circuit = css_code_memory_circuit(
            css_code=rep_code_d3, num_rounds=3, logical_basis=PauliBasis.Z
        )
        assert len(circuit.qubits) > 0

    def test_qubits_is_a_frozenset(self, rep_code_d3):
        """Contract: `circuit.qubits` is hashable, immutable, and unique."""
        circuit = css_code_memory_circuit(
            css_code=rep_code_d3, num_rounds=3, logical_basis=PauliBasis.Z
        )
        assert isinstance(circuit.qubits, frozenset)

    def test_as_stim_circuit_is_accepted_by_simulation(self, rep_circuit_d3):
        """Contract: `.as_stim_circuit()` output is consumable by
        `simulate_with_stim` - the only downstream consumer that matters.

        We test the real contract (interoperability with the simulation
        API) rather than `isinstance(..., stim.Circuit)`, because Stim is
        vendored via deltakit-stim and is not importable as a top-level
        module in this environment.
        """
        from deltakit.explorer.simulation import simulate_with_stim

        stim_circuit = rep_circuit_d3.as_stim_circuit()
        assert stim_circuit is not None

        # If this raises, the contract is broken
        result = simulate_with_stim(stim_circuit, shots=10)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_as_stim_circuit_is_repeatable(self, rep_circuit_d3):
        """Contract: converting to Stim is idempotent (same input -> same output)."""
        a = rep_circuit_d3.as_stim_circuit()
        b = rep_circuit_d3.as_stim_circuit()
        assert str(a) == str(b)


@pytest.mark.contract
class TestQpuContract:

    def test_compile_and_add_noise_returns_circuit(self, rep_circuit_d3):
        from deltakit.explorer.qpu import QPU, SI1000Noise
        noise = SI1000Noise(p=0.01)
        qpu = QPU(qubits=rep_circuit_d3.qubits, noise_model=noise)
        noisy = qpu.compile_and_add_noise_to_circuit(rep_circuit_d3)
        assert hasattr(noisy, "as_stim_circuit")

    def test_noisy_circuit_differs_from_ideal(self, rep_circuit_d3):
        from deltakit.explorer.qpu import QPU, SI1000Noise
        ideal_stim = str(rep_circuit_d3.as_stim_circuit())
        noise = SI1000Noise(p=0.01)
        qpu = QPU(qubits=rep_circuit_d3.qubits, noise_model=noise)
        noisy_stim = str(
            qpu.compile_and_add_noise_to_circuit(
                rep_circuit_d3
            ).as_stim_circuit()
        )
        assert ideal_stim != noisy_stim, "noise model had no effect"