"""Inspect the public surface of a RepetitionCode instance.

We discovered that .stabiliser_type does not exist. This script shows
what IS available, so we can write correct assertions.
"""
from deltakit.circuit.gates import PauliBasis
from deltakit.explorer.codes import RepetitionCode

code = RepetitionCode(distance=3, stabiliser_type=PauliBasis.Z)

print("=" * 70)
print("RepetitionCode instance inspection")
print("=" * 70)
print(f"\nType: {type(code)}")
print(f"MRO: {[c.__name__ for c in type(code).__mro__]}")

print("\n--- Public attributes / properties ---")
for name in sorted(dir(code)):
    if name.startswith("_"):
        continue
    try:
        value = getattr(code, name)
        # Skip methods and other callables for readability
        if callable(value):
            print(f"  {name:30s}  (callable: {type(value).__name__})")
        else:
            repr_value = repr(value)
            if len(repr_value) > 60:
                repr_value = repr_value[:57] + "..."
            print(f"  {name:30s}  = {repr_value}")
    except Exception as e:
        print(f"  {name:30s}  <error: {type(e).__name__}: {e}>")

print("\n--- __init__ signature ---")
import inspect
try:
    print(f"  {inspect.signature(RepetitionCode.__init__)}")
except Exception as e:
    print(f"  <error: {e}>")

print("\n--- Class docstring (first 30 lines) ---")
doc = RepetitionCode.__doc__ or "(no docstring)"
for line in doc.splitlines()[:30]:
    print(f"  {line}")

print("\n" + "=" * 70)