"""Unit tests for planar QEC code construction.

RotatedPlanarCode is a two-basis code (both X and Z stabilisers present),
which makes it structurally richer than RepetitionCode. These tests
validate its layout invariants and the shape of its stabiliser data.

Verified facts about RotatedPlanarCode (width=3, height=3):
  - data_qubits    = 9  (= width * height)
  - ancilla_qubits = 8  (= width * height - 1)
  - total qubits   = 17
  - stabilisers    = 1 group of 8 (all measured in one SIMULTANEOUS round)
  - parity matrices: X(4, 9), Z(4, 9)  -> 4 X-stabilisers, 4 Z-stabilisers
  - 1 logical qubit
"""
import pytest

from deltakit.explorer.codes import RotatedPlanarCode


class TestRotatedPlanarCodeConstruction:
    """Structural invariants of the default 3x3 rotated planar code."""

    def test_constructs(self, rotated_planar_3x3):
        assert rotated_planar_3x3 is not None

    def test_data_qubit_count_equals_width_times_height(self, rotated_planar_3x3):
        """Invariant: rotated planar code is built on a width x height grid
        of data qubits, so data_qubits == width * height."""
        assert len(rotated_planar_3x3.data_qubits) == 3 * 3

    def test_data_qubit_count_5x5(self, rotated_planar_5x5):
        """Same invariant holds for a different size."""
        assert len(rotated_planar_5x5.data_qubits) == 5 * 5

    def test_ancilla_count_equals_data_minus_one(self, rotated_planar_3x3):
        """Invariant: a rotated planar patch has one fewer stabiliser than
        data qubits (one stabiliser is redundant by the code structure)."""
        assert len(rotated_planar_3x3.ancilla_qubits) == len(
            rotated_planar_3x3.data_qubits
        ) - 1

    def test_total_qubit_count(self, rotated_planar_3x3):
        expected = len(rotated_planar_3x3.data_qubits) + len(
            rotated_planar_3x3.ancilla_qubits
        )
        assert len(rotated_planar_3x3.qubits) == expected

    def test_ancilla_qubits_enabled_by_default(self, rotated_planar_3x3):
        assert rotated_planar_3x3.use_ancilla_qubits is True

    def test_single_logical_qubit(self, rotated_planar_3x3):
        """Invariant: the rotated planar patch encodes exactly one
        logical qubit."""
        assert rotated_planar_3x3.calculate_number_of_logical_qubits() == 1

    def test_distinct_sizes_do_not_alias(self, rotated_planar_3x3, rotated_planar_5x5):
        assert rotated_planar_3x3 is not rotated_planar_5x5
        assert len(rotated_planar_3x3.data_qubits) != len(
            rotated_planar_5x5.data_qubits
        )


class TestRotatedPlanarCodeStabilisers:
    """Stabiliser structure and parity-matrix consistency."""

    def test_has_both_x_and_z_stabilisers(self, rotated_planar_3x3):
        """A two-basis code: unlike RepetitionCode, this must have
        non-zero X and Z stabiliser counts."""
        x_matrix, z_matrix = rotated_planar_3x3.parity_check_matrices
        assert x_matrix.shape[0] > 0, "expected X stabilisers"
        assert z_matrix.shape[0] > 0, "expected Z stabilisers"

    def test_stabiliser_groups_are_measurement_rounds(self, rotated_planar_3x3):
        """`.stabilisers` is grouped by measurement round, not by basis.

        With default SIMULTANEOUS scheduling, all stabilisers measure in
        one round, so the outer tuple has length 1.
        """
        assert len(rotated_planar_3x3.stabilisers) == 1

    def test_group_contains_all_stabilisers(self, rotated_planar_3x3):
        """Total stabiliser count matches the sum of the parity matrix rows."""
        x_matrix, z_matrix = rotated_planar_3x3.parity_check_matrices
        expected_total = x_matrix.shape[0] + z_matrix.shape[0]
        group = rotated_planar_3x3.stabilisers[0]
        assert len(group) == expected_total

    def test_stabiliser_count_equals_ancilla_count(self, rotated_planar_3x3):
        """Each stabiliser has one ancilla, so the counts must agree."""
        group = rotated_planar_3x3.stabilisers[0]
        assert len(group) == len(rotated_planar_3x3.ancilla_qubits)

    def test_parity_matrices_have_matching_column_count(self, rotated_planar_3x3):
        """Both parity matrices act on the same data qubits, so their
        column counts must match and equal the number of data qubits."""
        x_matrix, z_matrix = rotated_planar_3x3.parity_check_matrices
        assert x_matrix.shape[1] == z_matrix.shape[1]
        assert x_matrix.shape[1] == len(rotated_planar_3x3.data_qubits)

    def test_parity_matrix_values_are_binary(self, rotated_planar_3x3):
        """Parity check matrices are over GF(2): every entry must be 0 or 1."""
        x_matrix, z_matrix = rotated_planar_3x3.parity_check_matrices
        for matrix in (x_matrix, z_matrix):
            assert set(matrix.flatten().tolist()).issubset({0, 1})

    def test_expected_3x3_stabiliser_counts(self, rotated_planar_3x3):
        """Locked-in contract for the canonical 3x3 patch:
        4 X-stabilisers and 4 Z-stabilisers (8 total)."""
        x_matrix, z_matrix = rotated_planar_3x3.parity_check_matrices
        assert x_matrix.shape[0] == 4
        assert z_matrix.shape[0] == 4


class TestRotatedPlanarCodeNegative:
    """Negative tests - invalid construction parameters."""

    def test_width_below_2_raises(self):
        """Docstring states width must be >= 2."""
        with pytest.raises((ValueError, AssertionError)):
            RotatedPlanarCode(width=1, height=3)

    def test_height_below_2_raises(self):
        """Docstring states height must be >= 2."""
        with pytest.raises((ValueError, AssertionError)):
            RotatedPlanarCode(width=3, height=1)

    def test_zero_width_raises(self):
        with pytest.raises((ValueError, AssertionError)):
            RotatedPlanarCode(width=0, height=3)