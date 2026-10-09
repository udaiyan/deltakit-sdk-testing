"""Shared fixtures for the Deltakit SDK test suite."""
import os
import pytest

from deltakit.circuit.gates import PauliBasis
from deltakit.explorer.codes import RepetitionCode, css_code_memory_circuit
from deltakit.explorer.qpu import QPU, SI1000Noise


# --- Cloud gating --------------------------------------------------------
# These tests only run if DELTAKIT_TOKEN is present in the environment.
# Locally, they skip. In CI (with the GitHub secret), they run.
requires_cloud = pytest.mark.skipif(
    not os.environ.get("DELTAKIT_TOKEN"),
    reason="DELTAKIT_TOKEN not set; skipping cloud-dependent tests",
)


# --- Code fixtures -------------------------------------------------------
@pytest.fixture
def rep_code_d3():
    """Distance-3 repetition code with Z-basis stabilisers."""
    return RepetitionCode(distance=3, stabiliser_type=PauliBasis.Z)


@pytest.fixture
def rep_code_d5():
    """Distance-5 repetition code with Z-basis stabilisers."""
    return RepetitionCode(distance=5, stabiliser_type=PauliBasis.Z)


# --- Circuit fixtures ----------------------------------------------------
@pytest.fixture
def rep_circuit_d3(rep_code_d3):
    """Distance-3, 3-round memory circuit."""
    return css_code_memory_circuit(
        css_code=rep_code_d3,
        num_rounds=3,
        logical_basis=PauliBasis.Z,
    )


# --- Noisy circuit fixtures ---------------------------------------------
@pytest.fixture
def noisy_rep_circuit_d3(rep_circuit_d3):
    """Distance-3 circuit with SI1000 noise at p=0.01."""
    noise = SI1000Noise(p=0.01)
    qpu = QPU(qubits=rep_circuit_d3.qubits, noise_model=noise)
    return qpu.compile_and_add_noise_to_circuit(rep_circuit_d3)