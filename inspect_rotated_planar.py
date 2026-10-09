"""Inspect the real constructor signature of RotatedPlanarCode.

We discovered that RotatedPlanarCode(distance=3) raises a TypeError:
    __init__() got an unexpected keyword argument 'distance'

This script reveals what the constructor actually expects, plus the
signatures of related planar/toric codes so we can see the convention.
"""
import inspect

from deltakit.explorer.codes import (
    RotatedPlanarCode,
    UnrotatedPlanarCode,
    UnrotatedToricCode,
)


def describe(cls):
    print(f"\n{'=' * 70}")
    print(f"Class: {cls.__name__}")
    print(f"{'=' * 70}")

    print("\n--- __init__ signature ---")
    try:
        print(f"  {inspect.signature(cls.__init__)}")
    except Exception as e:
        print(f"  <error: {type(e).__name__}: {e}>")

    print("\n--- Class docstring (first 40 lines) ---")
    doc = cls.__doc__ or "(no docstring)"
    for line in doc.splitlines()[:40]:
        print(f"  {line}")


describe(RotatedPlanarCode)
describe(UnrotatedPlanarCode)
describe(UnrotatedToricCode)

print("\n" + "=" * 70)
print("Done.")
print("=" * 70)