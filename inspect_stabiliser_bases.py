"""Inspect the basis of EVERY stabiliser in each group.

Earlier inspection was misleading: it only checked the first stabiliser's
repr and concluded the group was single-basis. In fact a RotatedPlanarCode
has both X and Z stabilisers, and they appear together in one group.

This script:
  1. Counts how many PauliX vs PauliZ stabilisers are in each group
  2. Tries different schedule_type values to see if outer tuple grows
  3. Compares against the parity matrix row counts
"""
from collections import Counter

from deltakit.explorer.codes import RotatedPlanarCode
from deltakit_explorer.codes._planar_code._planar_code import ScheduleType


def basis_counts(group):
    """Count X vs Z stabilisers in a group by inspecting every member."""
    counter = Counter()
    for stab in group:
        r = repr(stab)
        # Count occurrences of PauliX(...) and PauliZ(...) in the product
        has_x = "PauliX(" in r
        has_z = "PauliZ(" in r
        if has_x and not has_z:
            counter["X"] += 1
        elif has_z and not has_x:
            counter["Z"] += 1
        elif has_x and has_z:
            counter["mixed"] += 1
        else:
            counter["unknown"] += 1
    return counter


def describe(label, code):
    print(f"\n--- {label} ---")
    print(f"  data_qubits: {len(code.data_qubits)}")
    print(f"  ancilla_qubits: {len(code.ancilla_qubits)}")
    print(f"  .stabilisers outer length: {len(code.stabilisers)}")
    for i, group in enumerate(code.stabilisers):
        counts = basis_counts(group)
        print(f"    group[{i}]: len={len(group)}, basis counts={dict(counts)}")
    x_matrix, z_matrix = code.parity_check_matrices
    print(f"  parity matrices: X{x_matrix.shape}, Z{z_matrix.shape}")


print("=" * 70)
print("Stabiliser basis inspection")
print("=" * 70)

describe(
    "RotatedPlanarCode(3,3) SIMULTANEOUS (default)",
    RotatedPlanarCode(width=3, height=3),
)

# Try alternative schedules - does the outer tuple length change?
for sched_name in ("SIMULTANEOUS", "SEPARATE"):
    sched = getattr(ScheduleType, sched_name, None)
    if sched is None:
        print(f"\n(ScheduleType.{sched_name} not available)")
        continue
    try:
        code = RotatedPlanarCode(width=3, height=3, schedule_type=sched)
        describe(f"RotatedPlanarCode(3,3) schedule={sched_name}", code)
    except Exception as e:
        print(f"\n(ScheduleType.{sched_name} failed: {type(e).__name__}: {e})")

print("\n" + "=" * 70)