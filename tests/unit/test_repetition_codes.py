"""Unit tests for QEC code construction.

These test the code objects themselves - not the full pipeline. If the
codes are wrong, everything downstream is meaningless, so this is the
foundation layer of the test pyramid.

All assertions target attributes confirmed to exist via live inspection
of the installed deltakit-explorer 0.9.3 package.

Findings recorded during development:
  - RepetitionCode does NOT expose `stabiliser_type` as an attribute
    (parameter used at construction time only).
  - `.stabilisers` is a tuple of stabiliser-groups, one group per basis
    that exists. A Z-only code has len(stabilisers) == 1.
  - `.parity_check_matrices` returns (x_matrix, z_matrix); the unused
    basis has shape (0, distance).
"""
import pytest

from deltakit.circuit.gates import PauliBasis
from deltakit.explorer.codes import RepetitionCode


class TestRepetitionCodeConstruction:
    """Validate construction and structural invariants of RepetitionCode."""

    def test_distance_3_constructs(self, rep_code_d3):
        assert rep_code_d3 is not None

    def test_distance_attribute_matches_construction(self, rep_code_d3, rep_code_d5):
        assert rep_code_d3.distance == 3
        assert rep_code_d5.distance == 5

    def test_data_qubit_count_equals_distance(self, rep_code_d3):
        """Invariant: an n-distance repetition code has n data qubits."""
        assert len(rep_code_d3.data_qubits) == rep_code_d3.distance

    def test_ancilla_qubit_count_equals_distance_minus_one(self, rep_code_d3):
        """Invariant: n-1 stabilisers, each with its own ancilla (when enabled)."""
        assert len(rep_code_d3.ancilla_qubits) == rep_code_d3.distance - 1

    def test_total_qubit_count(self, rep_code_d3):
        """Total = data + ancilla = d + (d - 1) = 2d - 1."""
        expected = 2 * rep_code_d3.distance - 1
        assert len(rep_code_d3.qubits) == expected

    def test_z_basis_stabilisers_single_group(self, rep_code_d3):
        """Invariant: `.stabilisers` is a tuple of groups, one per basis.

        For a Z-only repetition code we observe a single inner tuple
        containing d-1 Z-stabilisers.
        """
        stabs = rep_code_d3.stabilisers
        assert len(stabs) == 1, "Z-only code should have exactly one basis group"
        z_stabs = stabs[0]
        assert len(z_stabs) == rep_code_d3.distance - 1

    def test_x_basis_stabilisers_single_group(self):
        """Mirror of the Z-basis case, using X stabilisers."""
        code = RepetitionCode(distance=3, stabiliser_type=PauliBasis.X)
        stabs = code.stabilisers
        assert len(stabs) == 1
        x_stabs = stabs[0]
        assert len(x_stabs) == code.distance - 1

    def test_stabiliser_count_consistent_with_parity_matrix(self, rep_code_d3):
        """Cross-check: stabiliser count matches the Z parity matrix rows.

        Two independent representations of the same data - if they
        diverge, one of them has a bug.
        """
        stabs = rep_code_d3.stabilisers
        z_stabs = stabs[0]
        x_matrix, z_matrix = rep_code_d3.parity_check_matrices
        assert len(z_stabs) == z_matrix.shape[0]

    def test_z_basis_code_has_empty_x_parity_matrix(self, rep_code_d3):
        """A Z-basis repetition code has no X-type stabilisers."""
        x_matrix, z_matrix = rep_code_d3.parity_check_matrices
        assert x_matrix.shape[0] == 0
        assert z_matrix.shape == (rep_code_d3.distance - 1, rep_code_d3.distance)

    def test_x_basis_code_has_empty_z_parity_matrix(self):
        """Mirror: an X-basis repetition code has no Z-type stabilisers."""
        code = RepetitionCode(distance=3, stabiliser_type=PauliBasis.X)
        x_matrix, z_matrix = code.parity_check_matrices
        assert z_matrix.shape[0] == 0
        assert x_matrix.shape == (code.distance - 1, code.distance)

    def test_ancilla_qubits_enabled_by_default(self, rep_code_d3):
        assert rep_code_d3.use_ancilla_qubits is True

    def test_ancilla_qubits_can_be_disabled(self):
        """When ancillas are disabled, qubits == data_qubits."""
        code = RepetitionCode(
            distance=3, stabiliser_type=PauliBasis.Z, use_ancilla_qubits=False
        )
        assert code.use_ancilla_qubits is False
        assert code.qubits == code.data_qubits

    def test_distinct_instances_do_not_share_state(self, rep_code_d3, rep_code_d5):
        """Sanity: two fixtures must be independent objects."""
        assert rep_code_d3 is not rep_code_d5
        assert rep_code_d3.distance != rep_code_d5.distance


class TestRepetitionCodeNegative:
    """Negative tests - invalid inputs must fail clearly and early."""

    def test_distance_zero_raises(self):
        with pytest.raises((ValueError, AssertionError)):
            RepetitionCode(distance=0, stabiliser_type=PauliBasis.Z)

    def test_negative_distance_raises(self):
        with pytest.raises((ValueError, AssertionError)):
            RepetitionCode(distance=-1, stabiliser_type=PauliBasis.Z)

    def test_invalid_stabiliser_type_raises(self):
        """Passing a non-PauliBasis value should fail loudly, not silently."""
        with pytest.raises((TypeError, ValueError, AttributeError)):
            RepetitionCode(distance=3, stabiliser_type="Z")