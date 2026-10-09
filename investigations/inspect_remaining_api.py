"""Consolidated inspection of the remaining unknown API surfaces.

Covers:
  1. Measurements object returned by simulate_with_stim
  2. Decoders available in deltakit_decode
  3. Client API (token handling)
  4. Exact exception types raised by invalid inputs

After running this, we have enough facts to write the entire remaining
test suite in one pass without guessing.
"""
import inspect
import traceback

print("=" * 70)
print("[1] Measurements object API")
print("=" * 70)

try:
    from deltakit.circuit.gates import PauliBasis
    from deltakit.explorer.codes import RepetitionCode, css_code_memory_circuit
    from deltakit.explorer.qpu import QPU, SI1000Noise
    from deltakit.explorer.simulation import simulate_with_stim

    code = RepetitionCode(distance=3, stabiliser_type=PauliBasis.Z)
    circuit = css_code_memory_circuit(
        css_code=code, num_rounds=3, logical_basis=PauliBasis.Z
    )
    noisy = QPU(
        qubits=circuit.qubits, noise_model=SI1000Noise(p=0.01)
    ).compile_and_add_noise_to_circuit(circuit)
    stim_circuit = noisy.as_stim_circuit()

    result = simulate_with_stim(stim_circuit, shots=100)
    print(f"  simulate_with_stim returned: {type(result).__name__} "
          f"of length {len(result) if isinstance(result, tuple) else 'N/A'}")

    measurements, leakage = result
    print(f"\n  Measurements type: {type(measurements).__name__}")
    print(f"  Leakage type:      {type(leakage).__name__}")

    print(f"\n  Measurements public members:")
    for name in sorted(dir(measurements)):
        if name.startswith("_"):
            continue
        try:
            value = getattr(measurements, name)
            if callable(value):
                sig = ""
                try:
                    sig = str(inspect.signature(value))
                except Exception:
                    sig = "(?)"
                print(f"    {name}{sig}  (method)")
            else:
                r = repr(value)
                if len(r) > 70:
                    r = r[:67] + "..."
                print(f"    {name} = {r}")
        except Exception as e:
            print(f"    {name} <error: {type(e).__name__}>")

    # Try the calls we'd use in integration tests
    print(f"\n  Probing expected measurement methods:")
    for method in ["as_numpy", "to_detectors_and_observables",
                   "to_logical_observables", "reshape"]:
        fn = getattr(measurements, method, None)
        print(f"    {method}: {'present' if fn else 'MISSING'}")

except Exception:
    traceback.print_exc()


print("\n" + "=" * 70)
print("[2] Decoder classes in deltakit_decode")
print("=" * 70)

try:
    import deltakit_decode
    public = [n for n in dir(deltakit_decode) if not n.startswith("_")]
    print(f"  deltakit_decode public names:")
    for name in sorted(public):
        obj = getattr(deltakit_decode, name)
        kind = type(obj).__name__
        print(f"    {name:40s} ({kind})")
except Exception as e:
    print(f"  FAILED: {type(e).__name__}: {e}")

# Try likely submodules
print(f"\n  Probing common submodule paths:")
for path in [
    "deltakit_decode",
    "deltakit_decode.decoders",
    "deltakit_decode.decoding",
    "deltakit_decode.noise_sources",
    "deltakit_decode.analysis",
]:
    try:
        mod = __import__(path, fromlist=["*"])
        names = [n for n in dir(mod) if not n.startswith("_")]
        print(f"    OK   {path}  ({len(names)} public names)")
        for n in names[:15]:
            print(f"           {n}")
    except Exception as e:
        print(f"    FAIL {path}  {type(e).__name__}: {e}")


print("\n" + "=" * 70)
print("[3] Client API")
print("=" * 70)

try:
    from deltakit import Client
    print(f"  Client class: {Client}")
    print(f"\n  Client methods:")
    for name in sorted(dir(Client)):
        if name.startswith("_"):
            continue
        obj = getattr(Client, name)
        if callable(obj):
            sig = ""
            try:
                sig = str(inspect.signature(obj))
            except Exception:
                sig = "(?)"
            print(f"    {name}{sig}")

    print(f"\n  Client docstring (first 20 lines):")
    doc = Client.__doc__ or "(no docstring)"
    for line in doc.splitlines()[:20]:
        print(f"    {line}")
except Exception:
    traceback.print_exc()


print("\n" + "=" * 70)
print("[4] Exact exception types on invalid input")
print("=" * 70)

from deltakit.circuit.gates import PauliBasis
from deltakit.explorer.codes import RepetitionCode, RotatedPlanarCode
from deltakit.explorer.qpu import SI1000Noise

cases = [
    ("RepetitionCode(distance=0)",
     lambda: RepetitionCode(distance=0, stabiliser_type=PauliBasis.Z)),
    ("RepetitionCode(distance=-1)",
     lambda: RepetitionCode(distance=-1, stabiliser_type=PauliBasis.Z)),
    ("RepetitionCode(stabiliser_type='Z')",
     lambda: RepetitionCode(distance=3, stabiliser_type="Z")),
    ("RotatedPlanarCode(width=1, height=3)",
     lambda: RotatedPlanarCode(width=1, height=3)),
    ("RotatedPlanarCode(width=0, height=3)",
     lambda: RotatedPlanarCode(width=0, height=3)),
    ("SI1000Noise(p=-0.1)",
     lambda: SI1000Noise(p=-0.1)),
    ("SI1000Noise(p=1.5)",
     lambda: SI1000Noise(p=1.5)),
]

for label, fn in cases:
    try:
        fn()
        print(f"  {label:45s}  -> NO EXCEPTION (silent)")
    except Exception as e:
        print(f"  {label:45s}  -> {type(e).__name__}: {e}")


print("\n" + "=" * 70)
print("Done. Paste the full output.")
print("=" * 70)