"""Inspect the .stabilisers structure across code types.

We learned that .stabilisers is a tuple of unknown length. This script
checks three codes to reveal the grouping convention:

  - RepetitionCode (Z basis)  -> likely only Z stabilisers
  - RepetitionCode (X basis)  -> likely only X stabilisers
  - RotatedPlanarCode         -> has BOTH X and Z stabilisers
"""
from deltakit.circuit.gates import PauliBasis
from deltakit.explorer.codes import RepetitionCode, RotatedPlanarCode


def describe(label, code):
    print(f"\n--- {label} ---")
    print(f"  type: {type(code).__name__}")
    print(f"  distance: {code.distance}")

    stabs = code.stabilisers
    print(f"  .stabilisers type: {type(stabs).__name__}")
    print(f"  .stabilisers outer length: {len(stabs)}")

    for i, group in enumerate(stabs):
        print(f"    group[{i}]: type={type(group).__name__}, "
              f"len={len(group)}")
        # Identify basis of the first stabiliser in the group, if any
        if len(group) > 0:
            first = group[0]
            # A Stabiliser has a pauli_product attribute or similar
            print(f"      first stabiliser repr: {repr(first)[:100]}")
        else:
            print(f"      (empty group)")

    x_matrix, z_matrix = code.parity_check_matrices
    print(f"  parity_check_matrices:")
    print(f"    X matrix shape: {x_matrix.shape}")
    print(f"    Z matrix shape: {z_matrix.shape}")


print("=" * 70)
print("Stabiliser structure inspection")
print("=" * 70)

describe(
    "RepetitionCode, Z stabilisers",
    RepetitionCode(distance=3, stabiliser_type=PauliBasis.Z),
)

describe(
    "RepetitionCode, X stabilisers",
    RepetitionCode(distance=3, stabiliser_type=PauliBasis.X),
)

describe(
    "RotatedPlanarCode, distance 3",
    RotatedPlanarCode(distance=3),
)

print("\n" + "=" * 70)