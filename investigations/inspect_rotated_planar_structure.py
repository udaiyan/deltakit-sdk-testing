"""Inspect the stabiliser/parity-matrix structure of RotatedPlanarCode.

RepetitionCode has only one basis, so we could not tell what the
group ordering convention is. A rotated planar code has both X and Z
stabilisers, which reveals the order unambiguously.

We inspect:
  - len(stabilisers)                       -> should be 2
  - basis of each inner group
  - shape of parity_check_matrices         -> (x_matrix, z_matrix)
  - which group's count matches which matrix
"""
from deltakit.explorer.codes import RotatedPlanarCode


def basis_of_group(group):
    """Identify the Pauli basis of a stabiliser group by inspecting the
    first stabiliser's pauli product."""
    if len(group) == 0:
        return "(empty)"
    first = group[0]
    # Stabiliser repr looks like: Stabiliser((PauliZ(Qubit(...)), ...), ...)
    repr_str = repr(first)
    if "PauliZ" in repr_str and "PauliX" not in repr_str:
        return "Z"
    if "PauliX" in repr_str and "PauliZ" not in repr_str:
        return "X"
    return f"mixed? {repr_str[:80]}"


code = RotatedPlanarCode(width=3, height=3)

print("=" * 70)
print(f"RotatedPlanarCode(width=3, height=3)")
print("=" * 70)

print(f"\nType: {type(code).__name__}")
print(f"data_qubits: {len(code.data_qubits)}")
print(f"ancilla_qubits: {len(code.ancilla_qubits)}")
print(f"total qubits: {len(code.qubits)}")
print(f"use_ancilla_qubits: {code.use_ancilla_qubits}")

print(f"\n.stabilisers outer length: {len(code.stabilisers)}")
for i, group in enumerate(code.stabilisers):
    print(f"  group[{i}]: len={len(group)}, basis={basis_of_group(group)}")

x_matrix, z_matrix = code.parity_check_matrices
print(f"\nparity_check_matrices:")
print(f"  x_matrix shape: {x_matrix.shape}  (rows == # of X stabilisers)")
print(f"  z_matrix shape: {z_matrix.shape}  (rows == # of Z stabilisers)")

print(f"\nlogical operators:")
print(f"  x_logical_operators: {len(code.x_logical_operators)}")
print(f"  z_logical_operators: {len(code.z_logical_operators)}")
print(f"  calculate_number_of_logical_qubits(): "
      f"{code.calculate_number_of_logical_qubits()}")

print("\n" + "=" * 70)