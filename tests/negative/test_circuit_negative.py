"""Negative tests: invalid inputs must fail loudly and early.

A well-designed SDK rejects bad input at the boundary. These tests
document the exact exception type and message where verified, and flag
known defects with xfail markers.

Verified exception behaviour (deltakit-explorer 0.9.3):
  - RepetitionCode(distance=0)  -> ValueError("Code distance must be at least 2.")
  - RepetitionCode(stabiliser_type='Z') -> ValueError about PauliBasis
  - RotatedPlanarCode(width=1)  -> ValueError("Width and height need to be ...")
  - css_code_memory_circuit(num_rounds=0) -> raises (SDK is correctly defensive)

Known defects (recorded as xfail):
  - SI1000Noise(p=-0.1) silently accepted
  - SI1000Noise(p=1.5)  silently accepted
"""
import pytest

from deltakit.circuit.gates import PauliBasis
from deltakit.explorer.codes import (
    RepetitionCode,
    RotatedPlanarCode,
    css_code_memory_circuit,
)
from deltakit.explorer.qpu import SI1000Noise


@pytest.mark.negative
class TestRepetitionCodeRejectsBadInput:

    def test_distance_one_raises(self):
        with pytest.raises(ValueError):
            RepetitionCode(distance=1, stabiliser_type=PauliBasis.Z)

    def test_distance_zero_raises_with_message(self):
        with pytest.raises(ValueError, match="at least 2"):
            RepetitionCode(distance=0, stabiliser_type=PauliBasis.Z)

    def test_string_stabiliser_type_raises(self):
        with pytest.raises(ValueError, match="PauliBasis"):
            RepetitionCode(distance=3, stabiliser_type="Z")


@pytest.mark.negative
class TestRotatedPlanarCodeRejectsBadInput:

    def test_width_one_raises(self):
        with pytest.raises(ValueError, match="Width and height"):
            RotatedPlanarCode(width=1, height=3)

    def test_height_one_raises(self):
        with pytest.raises(ValueError, match="Width and height"):
            RotatedPlanarCode(width=3, height=1)

    def test_zero_dimension_raises(self):
        with pytest.raises(ValueError):
            RotatedPlanarCode(width=0, height=0)


@pytest.mark.negative
class TestNoiseParameterValidation:
    """Noise probabilities must lie in [0, 1].

    Marked xfail because the SDK currently accepts out-of-range values
    silently. See DEFECT-002 in TESTING.md.
    """

    @pytest.mark.xfail(
        reason="DEFECT-002: SI1000Noise accepts p<0 silently",
        strict=False,
    )
    def test_negative_probability_raises(self):
        with pytest.raises(ValueError):
            SI1000Noise(p=-0.1)

    @pytest.mark.xfail(
        reason="DEFECT-002: SI1000Noise accepts p>1 silently",
        strict=False,
    )
    def test_probability_above_one_raises(self):
        with pytest.raises(ValueError):
            SI1000Noise(p=1.5)


@pytest.mark.negative
class TestCircuitGeneratorRejectsBadInput:
    """`css_code_memory_circuit` must reject nonsensical parameters."""

    def test_zero_rounds_raises(self, rep_code_d3):
        """A memory experiment with zero rounds is degenerate.

        The SDK correctly raises; this test locks in that behaviour.
        """
        with pytest.raises((ValueError, AssertionError)):
            css_code_memory_circuit(
                css_code=rep_code_d3, num_rounds=0, logical_basis=PauliBasis.Z
            )

    def test_negative_rounds_raises(self, rep_code_d3):
        with pytest.raises((ValueError, AssertionError)):
            css_code_memory_circuit(
                css_code=rep_code_d3, num_rounds=-1, logical_basis=PauliBasis.Z
            )

    def test_invalid_logical_basis_raises(self, rep_code_d3):
        with pytest.raises((ValueError, TypeError, AttributeError)):
            css_code_memory_circuit(
                css_code=rep_code_d3,
                num_rounds=3,
                logical_basis="not-a-basis",
            )